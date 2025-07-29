import asyncio
import unittest.mock

import pytest

from unitelabs.cdk.subscriptions import Subscription

ONE_OP_TIME = 0.01


async def bg_cancel(subscription: Subscription, timeout: float = ONE_OP_TIME * 5):
    """Cancel the subscription after a delay, default ~5 operations."""
    await asyncio.sleep(timeout)
    await subscription.cancel()


class TestMaxsize:
    async def test_should_limit_queue_size(self):
        sub = Subscription[str](10)
        for i in range(10):
            sub.update(f"value{i}")
        assert sub.size == 10

        with pytest.raises(asyncio.QueueFull):
            sub.update("value11")

        assert sub.size == 10


class TestSize:
    async def test_should_return_current_size(self):
        sub = Subscription[str](10)
        assert sub.size == 0

        sub.update("value")
        assert sub.size == 1

        await sub.get()
        assert sub.size == 0


class TestUpdate:
    async def test_should_allow_none_value_in_subscription(self):
        sub = Subscription[str](10)
        values_added = ["value", None]
        for value in values_added:
            sub.update(value)

        seen = []
        async for value in sub:
            if value is None:
                await sub.cancel()

            seen.append(value)
        assert seen == values_added

    async def test_should_not_update_same_value(self):
        sub = Subscription[str](10)
        sub.put_nowait = unittest.mock.Mock(wraps=sub.put_nowait)

        # update twice
        sub.update("value")
        sub.update("value")

        assert sub._value == "value"
        sub.put_nowait.assert_called_once_with("value")


class TestCancel:
    async def test_should_stop_waiting_for_queue_task_after_cancel(self):
        sub = Subscription[str](10)

        cancel_task = asyncio.create_task(bg_cancel(sub, ONE_OP_TIME))
        async for value in sub:
            # this is never executed because the iterator is immediately exited
            assert value

        await asyncio.sleep(ONE_OP_TIME * 2)
        assert cancel_task.done()
        assert not sub._cancellation_tasks
        assert not sub._queue_tasks

    async def test_should_stop_iterating_after_cancel_in_loop(self):
        sub = Subscription[str](10)
        values = [f"value{i}" for i in range(1, 5)]
        for value in values:
            sub.update(value)

        seen = []
        async for value in sub:
            if value == values[2]:
                await sub.cancel()

            seen.append(value)
        assert seen == values[:3]

    async def test_should_stop_iterating_after_cancel_in_bg_task(self):
        sub = Subscription[str](10)
        N_OPS = 5

        async def make_updates():
            for i in range(10):
                sub.update(f"value{i}")
                await asyncio.sleep(ONE_OP_TIME)

        update_task = asyncio.create_task(make_updates())
        cancel_task = asyncio.create_task(bg_cancel(sub, ONE_OP_TIME * N_OPS))

        seen = [value async for value in sub]
        assert seen == [f"value{i}" for i in range(N_OPS)]

        await asyncio.sleep(ONE_OP_TIME * (N_OPS + 1))
        assert cancel_task.done()
        assert update_task.done()

        assert not sub._cancellation_tasks
        assert not sub._queue_tasks


class TestAsyncIterator:
    async def test_should_clear_tasks_after_each_iteration(self):
        sub = Subscription[str](10)
        for i in range(10):
            sub.update(f"value{i}")

        async for value in sub:
            assert "value" in value
            await asyncio.sleep(ONE_OP_TIME / 10)
            assert not sub._cancellation_tasks
            assert not sub._queue_tasks
            assert not sub._closed.is_set()
            if "9" in value:
                break


class TestGet:
    async def test_should_get_new_value(self):
        sub = Subscription[str](10)
        for i in range(10):
            msg = f"value{i}"
            sub.update(msg)
            assert await sub.get() == msg

    async def test_should_return_value_if_matches_predicate(self):
        sub = Subscription[str](10)
        msgs = [f"value{i}" for i in range(9)]
        msgs.insert(5, "find me 5")
        for msg in msgs:
            sub.update(msg)

        assert await sub.get(lambda x: "find me" in x) == "find me 5"

    async def test_should_timeout_if_nothing_in_queue(self):
        sub = Subscription[str](10)
        with pytest.raises(TimeoutError):
            await sub.get(timeout=0.05)

    async def test_should_timeout_if_nothing_matches_predicate(self):
        # create a subscription and populate it with values
        sub = Subscription[str](10)
        for value in [f"value {i}" for i in range(10)]:
            sub.update(value)

        with pytest.raises(TimeoutError):
            await sub.get(lambda x: "find me" in x, timeout=0.05)

    async def test_should_cycle_through_queued_items_until_match(self, create_task):
        sub = Subscription[str](10)

        # create a mock filter predicate to monitor how many times it was called
        def predicate(x: str) -> bool:
            return "5" in x

        mock_predicate = unittest.mock.Mock(wraps=predicate)

        # create background update task
        async def make_updates():
            for i in range(10):
                sub.update(f"value {i}")
                await asyncio.sleep(ONE_OP_TIME)

        update_task = next(create_task(make_updates()))

        assert await sub.get(mock_predicate) == "value 5"
        assert mock_predicate.call_count == 6

        # cleanup
        update_task.cancel()
        await asyncio.sleep(ONE_OP_TIME)
        assert update_task.done()


class TestPipe:
    async def test_should_type_check_pipes(self):
        # Requires visual check
        def invalid_pipe(x: int) -> str:
            return "value"

        sub = Subscription[str](10)
        sub.pipe(invalid_pipe)

    async def test_should_add_pipes_to_current_subscription(self):
        sub = Subscription[str](10)

        def first_pipe(x: str) -> str:
            return x.upper()

        def second_pipe(x: str) -> dict[str, str]:
            return {"value": x + "2"}

        sub.pipe(first_pipe)
        sub.pipe(second_pipe)

        assert sub._pipes == [first_pipe, second_pipe]

        sub.update("value")
        assert await sub.get() == {"value": "VALUE2"}
