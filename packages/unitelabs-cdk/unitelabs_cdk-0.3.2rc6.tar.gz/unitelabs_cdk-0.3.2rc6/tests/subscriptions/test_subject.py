import asyncio
import unittest.mock

import pytest

from unitelabs.cdk import Subject
from unitelabs.cdk.subscriptions.subscription import Subscription

ONE_OP_TIME = 0.01


def first_pipe(x: str) -> str:
    return x.upper()


def second_pipe(x: str) -> dict[str, str]:
    return {"value": x}


async def redundant_update(subject: Subject[str]) -> None:
    """Update the subject 10x, once per operation time, with redundant updates after the first iteration."""
    for x in range(1, 11):
        if x > 1:
            subject.update(f"update {x - 1}")  # redundant update
        subject.update(f"update {x}")
        await asyncio.sleep(ONE_OP_TIME)


class TestDefaults:
    async def test_should_set_default_value_as_current(self):
        subject = Subject[str]()
        assert subject.current is None

    async def test_should_set_default_maxsize(self):
        subject = Subject[str]()
        sub = subject.subscribe()
        assert sub.maxsize == 0


class TestUpdate:
    async def test_should_update_current_value(self):
        subject = Subject[str](maxsize=10)
        subject.update("new value")
        assert subject.current == "new value"

    async def test_should_notify_even_if_value_is_current(self):
        subject = Subject[str](maxsize=10)
        subject.notify = unittest.mock.Mock(wraps=subject.notify)
        subject.update("DEFAULT_VALUE")
        subject.notify.assert_called_once()


class TestSubscribe:
    async def test_should_add_subscription(self):
        subject = Subject[str](maxsize=10)
        sub = subject.subscribe()
        assert isinstance(sub, Subscription)
        assert sub in subject._subscribers

    async def test_should_not_set_current_value_on_subscription(self, create_task):
        subject = Subject[str](maxsize=10)
        FIRST_UPDATE = "first"
        subject.update(FIRST_UPDATE)
        assert subject.current == FIRST_UPDATE

        sub = subject.subscribe()
        assert subject.current == FIRST_UPDATE

        update_task = next(create_task(redundant_update(subject)))
        assert await sub.get() == "update 1"
        assert subject.current == "update 1"

        update_task.cancel()
        await asyncio.sleep(0.01)
        assert update_task.done()
        subject.unsubscribe(sub)


class TestUnsubscribe:
    async def test_should_remove_subscription(self):
        subject = Subject[str](maxsize=10)
        sub = subject.subscribe()
        assert sub in subject._subscribers
        subject.unsubscribe(sub)
        assert sub not in subject._subscribers

    async def test_should_raise_value_error_on_unknown_subscription(self):
        subject = Subject[str](maxsize=10)
        with pytest.raises(ValueError, match="Subscription not found in subscribers or children."):
            subject.unsubscribe(Subscription(10))

    async def test_should_raise_value_error_on_twice_removed(self):
        subject = Subject[str](maxsize=10)
        sub = subject.subscribe()
        subject.unsubscribe(sub)
        with pytest.raises(ValueError, match="Subscription not found in subscribers or children."):
            subject.unsubscribe(sub)

    async def test_should_cancel_subscription(self):
        subject = Subject[str](maxsize=10)
        sub = subject.subscribe()
        sub.cancel = unittest.mock.Mock(wraps=sub.cancel)

        subject.unsubscribe(sub)

        sub.cancel.assert_called_once()
        assert sub not in subject._subscribers

    async def test_should_allow_unsubscribe_from_child_subjects(self):
        subject = Subject[str](maxsize=10)
        child_subject = subject.pipe(first_pipe).pipe(second_pipe)

        sub = child_subject.subscribe()
        assert sub in subject.subscribers
        assert sub in child_subject.subscribers

        subject.unsubscribe(sub)
        assert sub not in subject.subscribers
        assert sub not in child_subject.subscribers


class TestSubscription_Get:
    async def test_should_get_new_value(self):
        subject = Subject[str](maxsize=10)
        subscription: Subscription[str] = subject.subscribe()
        subscription.update = unittest.mock.Mock(wraps=subscription.update)

        for i in range(10):
            msg = f"update {i}"
            subject.update(msg)
            subscription.update.assert_called_with(msg)
            assert await subscription.get() == msg

        # cleanup
        subject.unsubscribe(subscription)

    async def test_should_timeout_if_nothing_queued(self):
        subject = Subject[str](maxsize=10)
        subscription: Subscription[str] = subject.subscribe()
        with pytest.raises(TimeoutError):
            await subscription.get(timeout=0.05)

        # cleanup
        subject.unsubscribe(subscription)

    async def test_should_timeout_if_nothing_matches_predicate(self, create_task):
        subject = Subject[str](maxsize=10)
        update_task = next(create_task(redundant_update(subject)))
        subscription: Subscription[str] = subject.subscribe()

        with pytest.raises(TimeoutError):
            await subscription.get(lambda x: "value" in x, timeout=0.05)

        # cleanup
        update_task.cancel()
        await asyncio.sleep(0.01)
        assert update_task.done()
        subject.unsubscribe(subscription)

    async def test_should_not_set_subject_current_value_on_new_subscriptions(self):
        subject = Subject[Exception](maxsize=10)
        subscription = subject.subscribe()

        exception = ValueError("Test exception")
        subject.update(exception)

        expected_exception = await subscription.get(lambda x: isinstance(x, ValueError))
        assert expected_exception == exception
        assert subject._value == exception

        new_subscription = subject.subscribe()
        with pytest.raises(TimeoutError):
            await new_subscription.get(lambda x: isinstance(x, ValueError), timeout=0.05)
        assert subject._value == exception

        # cleanup
        for s in [subscription, new_subscription]:
            subject.unsubscribe(s)


class TestPipes:
    async def test_should_type_check_pipes(self):
        # Requires visual check
        def invalid_pipe(x: int) -> str:
            return "value"

        subject = Subject[str](maxsize=10)
        sub = subject.pipe(invalid_pipe)

    async def test_should_create_new_subject(self):
        subject = Subject[str](maxsize=10)
        piped = subject.pipe(first_pipe).pipe(second_pipe)
        assert piped._pipes == [first_pipe, second_pipe]

        assert piped != subject
        assert isinstance(piped, Subject)

    async def test_should_not_set_pipes_on_current_subject(self):
        subject = Subject[str](maxsize=10)
        upper_subscription = subject.pipe(first_pipe).subscribe()
        assert subject._pipes == []
        assert upper_subscription._pipes == [first_pipe]

        to_dict_subscription = subject.pipe(second_pipe).subscribe()
        assert subject._pipes == []
        assert to_dict_subscription._pipes == [second_pipe]

        subject.update("value")
        assert await upper_subscription.get() == "VALUE"
        assert await to_dict_subscription.get() == {"value": "value"}

    async def test_should_track_child_subscription(self):
        subject = Subject[str](maxsize=10)
        piped = subject.pipe(first_pipe).pipe(second_pipe)

        sub = piped.subscribe()

        assert subject._children[0]._pipes == [first_pipe]
        assert subject._children[0]._children[0]._pipes == [first_pipe, second_pipe]

        assert sub in piped.subscribers
        assert sub in subject.subscribers

        # cleanup
        piped.unsubscribe(sub)

    async def test_should_update_value_in_all_child_subjects(self):
        subject = Subject[str](maxsize=10)
        sub = subject.subscribe()

        piped = subject.pipe(first_pipe).pipe(second_pipe)

        piped_sub = piped.subscribe()
        piped_sub.update = unittest.mock.Mock(wraps=piped_sub.update)

        subject.update("value")

        piped_sub.update.assert_called_once_with("value")
        assert await sub.get() == "value"
        assert await piped_sub.get() == {"value": "VALUE"}

        # cleanup
        for s in [sub, piped_sub]:
            subject.unsubscribe(s)
