import asyncio
import functools
import unittest.mock

import pytest

from unitelabs.cdk.subscriptions import Publisher

ONE_OP_TIME = 0.01


def first_pipe(x: str) -> str:
    return x.upper()


def second_pipe(x: str) -> dict[str, str]:
    return {"value": x + "2"}


class TestSource:
    async def test_should_allow_coroutine_as_source(self):
        msg = "value"

        async def source() -> str:
            return msg

        pub = Publisher[str](source=source, interval=ONE_OP_TIME)
        sub = pub.subscribe()
        assert await sub.get() == msg

        pub.unsubscribe(sub)

    async def test_should_allow_callable_as_source(self):
        msg = "value"

        def source() -> str:
            return msg

        pub = Publisher[str](source=source, interval=ONE_OP_TIME)
        sub = pub.subscribe()
        assert await sub.get() == msg

        pub.unsubscribe(sub)

    async def test_should_allow_partial_coroutine_as_source(self):
        msg = "value"

        async def source(msg: str) -> str:
            return msg

        pub = Publisher[str](source=functools.partial(source, msg), interval=ONE_OP_TIME)
        sub = pub.subscribe()
        assert await sub.get() == msg

        pub.unsubscribe(sub)

    async def test_should_allow_partial_callable_as_source(self):
        msg = "value"

        def source(msg: str) -> str:
            return msg

        pub = Publisher[str](source=functools.partial(source, msg), interval=ONE_OP_TIME)
        sub = pub.subscribe()
        assert await sub.get() == msg

        pub.unsubscribe(sub)

    async def test_should_type_check_source(self):
        # Requires visual check
        def source() -> str:
            return "value"

        pub = Publisher[int](source=source, interval=ONE_OP_TIME)
        sub = pub.subscribe()
        assert await sub.get() == "value"

        pub.unsubscribe(sub)


class TestSubscribe:
    async def test_should_start_polling_after_add(self):
        mock = unittest.mock.Mock(side_effect=[f"value {i}" for i in range(10)])
        pub = Publisher[str](maxsize=10, source=mock, interval=ONE_OP_TIME)
        pub._set = unittest.mock.Mock(wraps=pub._set)

        assert not pub._update_task
        mock.assert_not_called()

        sub = pub.subscribe()
        pub._set.assert_called_once()
        await asyncio.sleep(ONE_OP_TIME)

        assert sub.qsize() >= 1
        mock.assert_called()
        assert pub._update_task

        pub.unsubscribe(sub)

    async def test_should_not_start_polling_again_if_other_subscribers(self):
        pub = Publisher[str](maxsize=10, source=lambda: "value", interval=ONE_OP_TIME)
        pub._set = unittest.mock.Mock(wraps=pub._set)
        assert not pub._update_task

        sub = pub.subscribe()
        assert pub._update_task
        pub._set.assert_called_once()
        pub._set.reset_mock()

        sub2 = pub.subscribe()
        pub._set.assert_not_called()

        for s in [sub, sub2]:
            pub.unsubscribe(s)

    async def test_should_add_current_value_to_new_subscription(self):
        mock = unittest.mock.Mock(side_effect=[f"value {i}" for i in range(10)])
        pub = Publisher[str](maxsize=10, source=mock, interval=ONE_OP_TIME)

        value = "value"
        pub.update(value)

        sub = pub.subscribe()
        assert await sub.get() == value
        mock.assert_not_called()

        pub.unsubscribe(sub)


class TestUnsubscribe:
    async def test_should_cancel_update_task_if_no_subscribers(self):
        # create a data generator for the publisher
        x = 0

        async def get_next_value() -> str:
            nonlocal x
            x += 1
            return f"update {x}"

        pub = Publisher[str](maxsize=10, source=get_next_value, interval=ONE_OP_TIME)
        assert not pub._update_task

        # create subscription and let it run for a while
        sub = pub.subscribe()
        iterations = 5
        await asyncio.sleep(ONE_OP_TIME * iterations)

        # check that internals are set and queue is being populated
        assert sub.qsize() >= iterations
        assert pub._update_task

        # save a reference to the task and remove the subscription
        task = pub._update_task
        pub.unsubscribe(sub)

        # check that internals from source are cleared
        assert not pub._update_task

        # give the task some to time to be gracefully cancelled
        await asyncio.sleep(0.01)
        assert task.cancelled()


class TestSubscription_Get:
    async def test_should_get_new_value(self):
        mock = unittest.mock.Mock(side_effect=[f"update {i}" for i in range(10)])
        pub = Publisher[str](source=mock, interval=ONE_OP_TIME, maxsize=10)

        sub = pub.subscribe()

        for i in range(10):
            value = await sub.get()
            assert value == f"update {i}"
            assert pub.current == f"update {i}"
            assert mock.call_count == i + 1

        # cleanup
        pub.unsubscribe(sub)

    async def test_should_timeout_if_nothing_matches_predicate(self):
        mock = unittest.mock.Mock(side_effect=[f"update {i}" for i in range(10)])
        pub = Publisher[str](source=mock, interval=ONE_OP_TIME, maxsize=10)

        sub = pub.subscribe()
        with pytest.raises(TimeoutError):
            await sub.get(lambda x: "value" in x, timeout=0.05)

        # cleanup
        pub.unsubscribe(sub)


class TestPipe:
    async def test_should_type_check_pipes(self):
        # Requires visual check
        def invalid_pipe(x: int) -> str:
            return "value"

        pub = Publisher[str](source=lambda: "value", interval=ONE_OP_TIME)
        pub.pipe(invalid_pipe)

    async def test_should_create_new_publisher(self):
        mock = unittest.mock.Mock(side_effect=[f"update {i}" for i in range(10)])
        pub = Publisher[str](source=mock, interval=ONE_OP_TIME, maxsize=10)

        piped = pub.pipe(first_pipe).pipe(second_pipe)
        assert piped._pipes == [first_pipe, second_pipe]

        assert piped != pub
        assert isinstance(piped, Publisher)

    async def test_should_add_subscription_to_new_publisher_only(self):
        mock = unittest.mock.Mock(side_effect=[f"update {i}" for i in range(10)])
        pub = Publisher[str](source=mock, interval=ONE_OP_TIME, maxsize=10)

        piped = pub.pipe(first_pipe).pipe(second_pipe)
        sub = piped.subscribe()
        assert sub._pipes == [first_pipe, second_pipe]

        assert sub in piped._subscribers
        assert sub not in pub._subscribers

        # cleanup
        piped.unsubscribe(sub)
