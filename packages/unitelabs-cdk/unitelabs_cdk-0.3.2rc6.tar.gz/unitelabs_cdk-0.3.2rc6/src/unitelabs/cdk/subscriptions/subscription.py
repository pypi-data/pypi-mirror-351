import asyncio
import collections.abc
import contextlib
import functools
import time

import typing_extensions as typing

T = typing.TypeVar("T")
U = typing.TypeVar("U")


class Subscription(asyncio.Queue[typing.Optional[T]], collections.abc.AsyncIterator[T]):
    """An AsyncIterable you can asynchronously add items to."""

    def __init__(
        self,
        maxsize: int,
        pipes: typing.Optional[
            list[
                typing.Union[
                    typing.Callable[[T], U],
                    functools.partial[typing.Callable[[T], U]],
                ]
            ]
        ] = None,
    ):
        super().__init__(maxsize)

        self._pipes = pipes or []

        self._value: typing.Optional[T] = None
        self._cancellation_tasks: set[asyncio.Task] = set()
        self._queue_tasks: set[asyncio.Task] = set()

        self._closed = asyncio.Event()

    @property
    def size(self) -> int:
        """The number of items in the queue."""

        return self.qsize()

    def update(self, value: "T") -> None:
        """Update the current value, if `value` is not current value."""

        if value != self._value:
            self._value = value
            self.put_nowait(value)

    async def cancel(self) -> None:
        """Cancel the subscription."""

        self._closed.set()

    def __aiter__(self) -> collections.abc.AsyncIterator["T"]:
        return self

    async def __anext__(self) -> typing.Union["T", "U", None]:
        if self._closed.is_set():
            raise StopAsyncIteration

        cancellation = asyncio.create_task(self._closed.wait(), name="subscription-cancellation")
        self._cancellation_tasks.add(cancellation)
        cancellation.add_done_callback(self._cancellation_tasks.discard)

        try:
            queue_task = asyncio.create_task(super().get(), name="subscription-queue")
            self._queue_tasks.add(queue_task)
            queue_task.add_done_callback(self._queue_tasks.discard)

            done, pending = await asyncio.wait((queue_task, cancellation), return_when=asyncio.FIRST_COMPLETED)
            if queue_task in done:
                item = queue_task.result()
                self.task_done()
                return self._pipe(item)

            if cancellation in done:
                for pending_task in pending:
                    with contextlib.suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(pending_task, 0)
                raise StopAsyncIteration
        finally:
            if not cancellation.done():
                cancellation.cancel()

            self._closed.clear()

    async def get(
        self,
        predicate: typing.Callable[["T"], bool] = lambda _: True,
        timeout: typing.Optional[float] = None,
    ) -> "U":
        """
        Request an upcoming value that satisfies the `predicate`.

        If used without `timeout` this will block indefinitely until a value satisfies the `predicate`.

        Args:
          predicate: A filter predicate to apply.
          timeout: How many seconds to wait for new value before timing out.

        Raises:
          TimeoutError: If the `timeout` is exceeded.
        """

        start_time = time.perf_counter()

        while True:
            wait_for = timeout + start_time - time.perf_counter() if timeout is not None else None
            try:
                value = await asyncio.wait_for(super().get(), timeout=wait_for)
                self.task_done()
            except (TimeoutError, asyncio.TimeoutError):
                raise TimeoutError from None

            if predicate(value):
                return self._pipe(value)

    def pipe(
        self,
        func: typing.Union[
            typing.Callable[[T], U],
            functools.partial[typing.Callable[[T], U]],
        ],
    ) -> "Subscription[U]":
        """Add a `func` to the list of functions which will iteratively be applied to values retrieved by `get`."""

        self._pipes.append(func)
        return typing.cast("Subscription[U]", self)

    def _pipe(self, value: "T") -> "U":
        for fn in self._pipes:
            value = fn(value)

        return typing.cast("U", value)
