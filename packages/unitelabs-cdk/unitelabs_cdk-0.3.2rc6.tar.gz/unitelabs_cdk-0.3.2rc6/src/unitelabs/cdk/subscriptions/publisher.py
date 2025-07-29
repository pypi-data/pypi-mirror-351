import asyncio
import collections.abc
import functools
import inspect

import typing_extensions as typing

from ..sila.utils import clear_interval, set_interval
from .subject import Subject, T, U

if typing.TYPE_CHECKING:
    from .subscription import Subscription


class Publisher(typing.Generic[T], Subject[T]):
    """
    An observable which updates itself by polling a data source.

    Args:
      source: A function or coroutine that will be called at a fixed interval as the data source of the subscription.
      interval: How many seconds to wait between polling calls to `source`.
      maxsize: The maximum number of messages to track in the queue.

    Examples:
      Subscribe to a publisher which will call `method` every 2 seconds:
      >>> publisher = Publisher[str](source=method, interval=2, maxsize=10)
      >>> async for state in publisher.subscribe():
      >>>     yield state
    """

    def __init__(
        self,
        source: typing.Union[
            typing.Callable[[], collections.abc.Coroutine[typing.Any, typing.Any, T]],
            typing.Callable[[], T],
            functools.partial[typing.Callable[[], collections.abc.Coroutine[typing.Any, typing.Any, T]]],
            functools.partial[typing.Callable[[], T]],
        ],
        interval: float = 5,
        maxsize: int = 0,
    ) -> None:
        super().__init__(maxsize=maxsize)
        self._children: list[Publisher] = []

        self._update_task: typing.Optional[asyncio.Task] = None
        self._source = source
        self._interval = interval

    def _set(self) -> None:
        """
        Create a background task to poll the data `source` and update the current value.

        Task will be destroyed when all subscriptions to the `Publisher` are removed.
        """
        self._update_task = set_interval(self.__self_update, delay=self._interval)

    async def __self_update(self) -> None:
        if inspect.iscoroutinefunction(self._source) or (
            isinstance(self._source, functools.partial) and inspect.iscoroutinefunction(self._source.func)
        ):
            new_value = await self._source()
        else:
            new_value = self._source()

        self.update(new_value)

    @typing.override
    def subscribe(self) -> "Subscription[T]":
        if not self._update_task:
            self._set()

        subscription = super().subscribe()
        if self.current is not None:
            subscription.update(self.current)

        return subscription

    @typing.override
    def unsubscribe(self, subscriber: "Subscription[T]") -> None:
        super().unsubscribe(subscriber)

        if not self._subscribers and self._update_task:
            clear_interval(self._update_task)
            self._update_task = None
            self._value = None

    @typing.override
    def pipe(
        self,
        func: typing.Union[
            typing.Callable[[T], U],
            functools.partial[typing.Callable[[T], U]],
        ],
    ) -> "Publisher[U]":
        publisher = Publisher[U](source=self._source, interval=self._interval, maxsize=self._maxsize)
        publisher._pipes = [*self._pipes, func]
        self._children.append(publisher)
        return publisher
