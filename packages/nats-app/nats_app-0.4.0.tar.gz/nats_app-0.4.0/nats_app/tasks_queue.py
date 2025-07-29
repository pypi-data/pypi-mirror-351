import contextlib
import logging
from collections import defaultdict
from collections.abc import Awaitable
from functools import wraps
from typing import Callable, Optional

import ujson
from nats.aio.msg import Msg, MsgAlreadyAckdError
from nats.js.api import AckPolicy, ConsumerConfig, StorageType, StreamConfig
from pydantic import BaseModel, PrivateAttr, validate_call

from nats_app.marshaling import normalize_payload

logger = logging.getLogger(__name__)


class MetaTask(BaseModel):
    task: str
    args: tuple | list
    kwargs: dict
    _msg: Optional[any] = PrivateAttr()

    @classmethod
    def from_msg(cls, msg: Msg) -> "MetaTask":
        m = cls(**ujson.loads(msg.data))
        m._msg = msg
        return m

    async def ack(self) -> None:
        with contextlib.suppress(MsgAlreadyAckdError):
            await self._msg.ack()

    async def nak(self, delay: int) -> None:
        with contextlib.suppress(MsgAlreadyAckdError):
            await self._msg.nak(delay=delay)

    async def retry(self, delay: int, max_retry: int) -> bool:
        num_delivered = self.metadata.num_delivered
        if num_delivered > max_retry:
            await self.ack()
            return False
        else:
            delay = delay + (num_delivered - 1) * 2
            await self.nak(delay=self.retry_delay(delay) or delay)
            return True

    def retry_delay(self, delay: int) -> Optional[int]:
        return delay + (self.metadata.num_delivered - 1) * 2 if self._msg else None

    @property
    def header(self) -> Optional[dict[str, str]]:
        return self._msg.header if self._msg else None

    @property
    def metadata(self) -> Msg.Metadata:
        return self._msg.metadata if self._msg else None

    @property
    def is_acked(self) -> bool:
        return self._msg.is_acked if self._msg else None

    @property
    def sid(self) -> int:
        return self._msg.sid if self._msg else None


class TaskParams(BaseModel):
    fn: Callable[..., Awaitable]
    skip_validate: bool = False
    subject: Optional[str] = None
    batch: int = 1
    timeout: Optional[int] = None
    consumer_config: Optional[ConsumerConfig] = None
    max_retry: int = 5
    fail_delay: int = 60

    def is_batch(self) -> bool:
        return self.batch is not None and self.batch > 1


def _get_fn_name(fn):
    return f"{fn.__module__}.{fn.__qualname__}"


class TaskQueue:
    def __init__(
        self,
        *,
        subjects: list[str],
        stream_name: Optional[str] = None,
        storage: StorageType = StorageType.FILE,
        stream_config: Optional[StreamConfig] = None,
        durable: Optional[str] = None,
        clean_bad_messages: bool = False,
    ):
        self._nc = None
        self._registered_tasks = {}

        self.stream_config = stream_config
        if not self.stream_config:
            self.stream_config = StreamConfig(
                name=stream_name,
                subjects=subjects,
                storage=storage,
            )

        self.durable = durable
        self.clean_bad_messages = clean_bad_messages

    @property
    def stream_name(self):
        return self.stream_config.name

    @property
    def storage(self):
        return self.stream_config.storage

    @property
    def subjects(self):
        return self.stream_config.subjects

    @property
    def default_subject(self):
        subject = self.subjects[0]
        if not subject.endswith(".*"):
            return subject
        else:
            return subject[:-1] + "task"

    def _get_subject(self, subject: Optional[str]):
        if not subject:
            return self.default_subject
        subj = subject.rstrip("*")
        for s in self.subjects:
            if subj.startswith(s.rstrip("*")):
                return subject
        raise ValueError(f"subject '{subject}' not configures in stream {self.stream_name}: subjects: {self.subjects}")

    def _set_delay(self, task_name: str, subject: str):
        async def _delay_fn(*args, **kwargs) -> None:
            if not self._nc:
                logger.error("TaskQueue: nats connection is not configured")
                raise ValueError("TaskQueue: nats connection is not configured")

            meta = MetaTask(
                task=task_name,
                args=[normalize_payload(v) for v in args],
                kwargs={k: normalize_payload(v) for k, v in kwargs.items()},
            )

            await self._nc.publish(subject, meta.model_dump(mode="json"))
            logger.info(
                f"pub task message '{meta.task}' to subject '{subject}' to stream '{self.stream_name}'"
                f"with args={meta.args} kwargs={meta.kwargs}"
            )

        return _delay_fn

    def task(
        self,
        cb=None,
        subject: Optional[str] = None,
        *,
        batch: int = 1,
        timeout: Optional[int] = None,
        ack_policy: AckPolicy = AckPolicy.EXPLICIT,
        fail_delay: int = 60,
        consumer_config: Optional[ConsumerConfig] = None,
        skip_validate: bool = False,
    ):
        def wrapper(fn):
            if not skip_validate and batch == 1:
                fn = validate_call(fn)

            fn.task_name = _get_fn_name(fn)
            fn.subject = self._get_subject(subject)
            fn.delay = self._set_delay(fn.task_name, fn.subject)

            self._registered_tasks[fn.task_name] = TaskParams(
                fn=fn,
                skip_validate=skip_validate,
                subject=fn.subject,
                batch=batch,
                timeout=timeout,
                consumer_config=consumer_config if consumer_config else ConsumerConfig(ack_policy=ack_policy),
                fail_delay=fail_delay,
            )

            logger.info(f"register delayed task: {fn.task_name}")

            @wraps(fn)
            async def wrap(*args, **kwargs):
                return await fn(*args, **kwargs)

            return wrap

        if callable(cb):
            return wrapper(cb)
        return wrapper

    def bind(self, nc):
        self._nc = nc
        nc._jetstream_configs.append(self.stream_config)

        # subscribe to stream
        single_message_tasks = defaultdict(dict)
        batch_messages_tasks = defaultdict(dict)
        for task_param in self._registered_tasks.values():
            if task_param.batch == 1:
                single_message_tasks[task_param.subject][task_param.fn.task_name] = task_param
            else:
                batch_messages_tasks[task_param.subject][task_param.fn.task_name] = task_param
        for subject, task_params in single_message_tasks.items():
            self._subscribe_batch_messages(subject, task_params)

        for subject, task_params in batch_messages_tasks.items():
            if len(task_params) > 1:
                batch = set([t.batch for t in task_params])
                timeout = set([t.timeout for t in task_params])
                ack_policy = set([t.consumer_config.ack_policy for t in task_params])
                fail_delay = set([t.fail_delay for t in task_params])
                if len(batch) > 1 or len(timeout) > 1 or len(ack_policy) > 1 or len(fail_delay) > 1:
                    raise ValueError(
                        f"batch message on subject='{subject}' received multiple task params={task_params}"
                    )
            self._subscribe_batch_messages(subject, task_params)

    async def _parse_msg(self, m: Msg) -> Optional[MetaTask]:
        try:
            return MetaTask.from_msg(m)
        except Exception:
            if self.clean_bad_messages:
                logger.warning(f"fail to parse message: {m.data} - cleaning up")
                await m.ack()
            return None

    def _subscribe_batch_messages(self, subject: str, task_params: dict[str, TaskParams]):
        tp = list(task_params.values())[0]

        @self._nc.js_pull_subscribe(
            subject,
            stream=self.stream_name,
            durable=self.durable,
            batch=tp.batch,
            timeout=tp.timeout,
            config=tp.consumer_config,
        )
        async def subscribe(msgs: list[Msg]):
            if not msgs:
                return

            data = [d for d in [await self._parse_msg(msg) for msg in msgs] if d is not None]
            if not data:
                return

            task_names = set([m.task for m in data])
            if len(task_names) > 1:
                logger.error(f"batch message received multiple task names: {task_names}")
                return
            task_name = data[0].task

            task_param = task_params.get(task_name)

            params = ujson.dumps([{"args": d.args, "kwargs": d.kwargs} for d in data])
            try:
                logger.info(f"call task='{task_name}'({params})")
                if tp.is_batch():
                    result = await task_param.fn(data)
                else:
                    result = await task_param.fn(*data[0].args, **data[0].kwargs)
                logger.info(f"finish task='{task_name}'({params}) result={result}")
                if not tp.is_batch() or tp.consumer_config.ack_policy == AckPolicy.ALL:
                    await msgs[len(msgs) - 1].ack()
            except Exception:
                logger.exception(f"fail task: {task_name}({params})")
                if not tp.is_batch():
                    msg = data[0]
                    num_delivered = msg.metadata.num_delivered
                    if num_delivered > tp.max_retry:
                        await msg.ack()
                        logger.warning(f"stop retry fail task: {task_name}({params}) - reach max retry count")
                    else:
                        delay = tp.fail_delay + (num_delivered - 1) * 2
                        await msg.nak(delay=delay)
                        logger.warning(f"retry fail task: {task_name}({params}) - "
                                         f"retry={num_delivered} delay={delay}")
                else:
                    if tp.consumer_config.ack_policy == AckPolicy.ALL:
                        num_delivered = min([d.metadata.num_delivered for d in data])
                        if num_delivered > tp.max_retry:
                            await msgs[len(msgs) - 1].ack()
                            logger.warning(f"stop retry fail task: {task_name}({params}) - reach max retry count")
                        else:
                            delay = tp.fail_delay + (num_delivered - 1) * 2
                            await msgs[len(msgs) - 1].nak(delay=delay)
                            logger.warning(f"retry fail task: {task_name}({params}) - "
                                           f"retry={num_delivered} delay={delay}")

        logger.info(
            f"connect to nats stream: '{self.stream_name}' on subject: '{subject}' "
            f"delayed batch tasks: {list(task_params.keys())}"
        )
