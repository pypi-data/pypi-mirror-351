import asyncio
import functools

import typing_extensions as typing

from .subscription import Subscription

T = typing.TypeVar("T")
U = typing.TypeVar("U")


class Subject(typing.Generic[T]):
    """
    An observable that can be updated externally and subscribed to by multiple observers.

    Args:
      maxsize: The maximum number of messages to track in `Subscription` queues created by `subscribe`.
    """

    def __init__(
        self,
        maxsize: int = 0,
    ) -> None:
        self._maxsize = maxsize
        self._value: typing.Optional[T] = None

        self._subscribers: list[Subscription] = []
        self._cancellation_tasks: set[asyncio.Task] = set()
        self._pipes = []
        self._children: list[Subject] = []

    @property
    def current(self) -> typing.Optional[T]:
        """The current value."""

        return self._value

    @property
    def subscribers(self) -> list[Subscription]:
        """List of `Subscription`s which will be notified on `update`."""

        subs = self._subscribers.copy()
        for child in self._children:
            subs.extend(child.subscribers)
        return subs

    def subscribe(self) -> Subscription[T]:
        """Add a `Subscription` that will be notified on `update`."""

        subscription = Subscription(self._maxsize, pipes=self._pipes)

        self._subscribers.append(subscription)
        return subscription

    def unsubscribe(self, subscriber: Subscription) -> None:
        """Remove a `Subscription`."""

        task = asyncio.create_task(subscriber.cancel())
        self._cancellation_tasks.add(task)
        task.add_done_callback(self._cancellation_tasks.discard)

        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)
        elif subscriber in self.subscribers:
            for child in self._children:
                if subscriber in child.subscribers:
                    child.unsubscribe(subscriber)
                    break
        else:
            msg = "Subscription not found in subscribers or children."
            raise ValueError(msg)

    def notify(self) -> None:
        """Propagate the current value to all `Subscription`s."""

        for subscriber in self.subscribers:
            subscriber.update(self._value)

    def update(self, value: T) -> None:
        """Update the current value and `notify` all `Subscription`s."""

        self._value = value
        self.notify()

    def pipe(
        self, func: typing.Union[typing.Callable[[T], U], functools.partial[typing.Callable[[T], U]]]
    ) -> "Subject[U]":
        """
        Create a new `Subject` with `func` added to the list of pipes that are applied to values recieved from `notify`.

        Examples:
          Chain multiple pipe functions:
          >>> def first_pipe(x: str) -> str:
          ...     return x.upper()
          >>> def second_pipe(x: str) -> dict[str, str]:
          ...     return {"value": x}
          >>> piped = subject.pipe(first_pipe).pipe(second_pipe)
          >>> async for value in piped.subscribe():
          ...     print(value)
          Here a `value` received from `piped.subscribe()` is equivalent to `second_pipe(first_pipe(x))`
          where `x` is the value received from `Subject.update`.

          Create multiple subjects with different pipes that are simultaneously updated:
          >>> plus_one = subject.pipe(lambda x: x + 1)
          >>> times_two = subject.pipe(lambda x: x * 2)
          >>> subject.update(3)
          >>> await plus_one.get()  # 4
          >>> await times_two.get()  # 6

        Args:
          func: A pipe function to apply to all values received by `Subscription`.

        Returns:
          A new `Subject` with the pipe function added.
        """
        new_subject = Subject[U](maxsize=self._maxsize)
        new_subject._pipes = [*self._pipes, func]
        self._children.append(new_subject)
        return new_subject
