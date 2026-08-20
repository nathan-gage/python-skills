"""Proofs for python-async-best-practices rule claims."""

import asyncio
import concurrent.futures
import gc
import os
import threading

import pytest


def test_gather_leaves_siblings_running_on_failure():
    """async-own-your-tasks: "asyncio.gather ... the first exception propagates while sibling
    coroutines keep running unsupervised."
    """

    async def main() -> None:
        proceed = asyncio.Event()
        finished = asyncio.Event()

        async def failer() -> None:
            raise RuntimeError("boom")

        async def sibling() -> None:
            await proceed.wait()
            finished.set()

        sibling_task = asyncio.create_task(sibling())
        with pytest.raises(RuntimeError, match="boom"):
            await asyncio.gather(failer(), sibling_task)
        assert not sibling_task.done()  # gather raised; sibling still running, unowned
        proceed.set()
        await sibling_task
        assert finished.is_set()

    asyncio.run(main())


def test_taskgroup_cancels_siblings_on_failure():
    """async-own-your-tasks: "TaskGroup: block exit awaits everything; one failure cancels the rest." """

    async def main() -> None:
        sibling_cancelled = asyncio.Event()

        async def failer() -> None:
            raise RuntimeError("boom")

        async def sibling() -> None:
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                sibling_cancelled.set()
                raise

        with pytest.raises(ExceptionGroup):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(failer())
                tg.create_task(sibling())
        assert sibling_cancelled.is_set()

    asyncio.run(main())


def test_unretrieved_task_exception_reported_at_collection():
    """async-own-your-tasks: "Its exception is reported only when the task is collected —
    'Task exception was never retrieved'."
    """
    messages: list[str] = []

    async def main() -> None:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(lambda _loop, ctx: messages.append(ctx.get("message", "")))

        async def fail() -> None:
            raise ValueError("lost")

        task = asyncio.create_task(fail())
        await asyncio.sleep(0)  # let it fail; nobody awaits the result
        del task
        gc.collect()
        await asyncio.sleep(0)

    asyncio.run(main())
    assert any("Task exception was never retrieved" in m for m in messages)


def test_default_executor_size_formula_by_version():
    """async-no-blocking-event-loop: "The default executor behind asyncio.to_thread is sized for
    the host (min(32, cpu + 4) threads) ... before 3.13 that counts the host's CPUs even inside a
    CPU-limited container." 3.13+ switched to os.process_cpu_count() (affinity-aware).
    """
    import sys

    executor = concurrent.futures.ThreadPoolExecutor()  # the default-executor class and sizing
    if sys.version_info >= (3, 13):
        cpu = os.process_cpu_count()
    else:
        cpu = os.cpu_count()
    try:
        assert executor._max_workers == min(32, (cpu or 1) + 4)
    finally:
        executor.shutdown(wait=False)


def test_to_thread_cancellation_abandons_running_thread():
    """async-no-blocking-event-loop: "asyncio.to_thread abandons the thread and lets the awaiting
    task unwind ... but the thread itself always runs to completion."
    """
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()

    def work() -> None:
        started.set()
        release.wait(timeout=10)
        finished.set()

    async def main() -> None:
        task = asyncio.create_task(asyncio.to_thread(work))
        async with asyncio.timeout(10):
            while not started.is_set():
                await asyncio.sleep(0.001)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not finished.is_set()  # await unwound while the thread still runs

    asyncio.run(main())
    release.set()
    assert finished.wait(timeout=10)  # the abandoned thread ran to completion anyway


def test_break_abandons_generator_cleanup_until_finalization():
    """async-generator-cleanup: "Leaving an async for early abandons the generator with its
    finally blocks still pending" — and finalization happens at loop teardown, not at the break.
    """
    events: list[str] = []

    async def gen():
        try:
            yield 1
            yield 2
        finally:
            events.append("closed")

    async def main() -> None:
        async for _ in gen():
            break
        events.append("after-break")

    asyncio.run(main())
    assert events.index("after-break") < events.index("closed")  # cleanup ran late, not at break


def test_aclosing_ties_cleanup_to_block_exit():
    """async-generator-cleanup: "aclosing ties cleanup to block exit" — finally runs before the
    code after the with block.
    """
    from contextlib import aclosing

    events: list[str] = []

    async def gen():
        try:
            yield 1
            yield 2
        finally:
            events.append("closed")

    async def main() -> None:
        async with aclosing(gen()) as stream:
            async for _ in stream:
                break
        events.append("after-with")

    asyncio.run(main())
    assert events == ["closed", "after-with"]


def test_aclose_throws_generatorexit_at_current_yield():
    """async-generator-cleanup: "aclose() throws GeneratorExit into the generator at its
    current yield."
    """
    events: list[str] = []

    async def gen():
        try:
            yield 1
        except GeneratorExit:
            events.append("generatorexit-at-yield")
            raise

    async def main() -> None:
        stream = gen()
        assert await anext(stream) == 1
        await stream.aclose()

    asyncio.run(main())
    assert events == ["generatorexit-at-yield"]


def test_cancellederror_is_not_exception():
    """async-preserve-cancellation: "On 3.8+ CancelledError subclasses BaseException precisely so
    except Exception: can't swallow it by accident."
    """
    assert not issubclass(asyncio.CancelledError, Exception)
    assert issubclass(asyncio.CancelledError, BaseException)


def test_gather_return_exceptions_yields_cancellation_as_value():
    """async-preserve-cancellation: "gather(..., return_exceptions=True) types each element as
    T | BaseException" — a cancelled child comes back as a CancelledError value interleaved with
    successes, invisible to an isinstance(r, Exception) filter.
    """

    async def main() -> None:
        started = asyncio.Event()

        async def victim() -> str:
            started.set()
            await asyncio.sleep(60)
            return "unreachable"

        async def succeeds() -> str:
            return "ok"

        task = asyncio.create_task(victim())
        gathered = asyncio.gather(task, succeeds(), return_exceptions=True)
        await started.wait()
        task.cancel()
        results = await gathered
        assert isinstance(results[0], asyncio.CancelledError)  # cancellation as a value
        assert not isinstance(results[0], Exception)  # an Exception filter misses it
        assert results[1] == "ok"  # interleaved with successes

    asyncio.run(main())


def test_absorbed_cancellation_reports_success():
    """async-preserve-cancellation: "Code that absorbs it doesn't crash — it completes: the task
    reports success (task.cancelled() is False), half-done work looks finished."
    """

    async def main() -> None:
        started = asyncio.Event()

        async def stubborn() -> str:
            started.set()
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                return "absorbed"                 # the claim under test
            return "unreachable"

        task = asyncio.create_task(stubborn())
        await started.wait()
        task.cancel()
        result = await task                       # no CancelledError raised to the awaiter
        assert result == "absorbed"
        assert task.cancelled() is False          # the task does not count as cancelled

    asyncio.run(main())


def test_absorbed_cancellation_defeats_timeout():
    """async-preserve-cancellation: "a surrounding asyncio.timeout expires without ever raising
    TimeoutError — the deadline is silently lost."
    """

    async def stubborn() -> str:
        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            return "absorbed"
        return "unreachable"

    async def main() -> None:
        async with asyncio.timeout(0.01):
            result = await stubborn()             # deadline fires, cancellation absorbed
        assert result == "absorbed"               # block exits normally; no TimeoutError anywhere

    asyncio.run(main())


def test_shutdown_drain_preserves_owner_cancellation():
    """async-own-your-tasks: cancelling the owner while it drains a cancelled child *delegates*
    the cancel to the child, so child.cancelled() is True even though the CancelledError belongs
    to the owner — the aclose example must consult owner.cancelling() and re-raise.
    """

    async def main() -> None:
        pump_started = asyncio.Event()
        cleanup_entered = asyncio.Event()

        async def pump_events() -> None:
            pump_started.set()
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                cleanup_entered.set()
                await asyncio.sleep(60)   # cleanup parks so the owner can be cancelled mid-drain

        async def do_aclose(pump: asyncio.Task[None]) -> None:
            owner = asyncio.current_task()
            pump.cancel()
            try:
                await pump
            except asyncio.CancelledError:
                if owner is not None and owner.cancelling():
                    raise                  # the owner itself is being cancelled
                if not pump.cancelled():
                    raise

        pump = asyncio.create_task(pump_events())
        await pump_started.wait()
        closer = asyncio.create_task(do_aclose(pump))
        await cleanup_entered.wait()       # closer is parked on `await pump`; pump parked in cleanup
        closer.cancel()
        with pytest.raises(asyncio.CancelledError):
            await closer
        assert closer.cancelled()          # the owner's cancellation propagated
        assert pump.cancelled()            # even though the delegated cancel landed on the pump too

    asyncio.run(main())


def test_shutdown_drain_surfaces_pre_cancellation_failure():
    """async-own-your-tasks: "the await ... surfaces a real exception if the task had already
    failed before the cancel" — the drain must not discard it.
    """

    async def main() -> None:
        async def pump_events() -> None:
            raise ValueError("pump broke before shutdown")

        pump = asyncio.create_task(pump_events())
        await asyncio.sleep(0)             # pump fails before anyone cancels it
        owner = asyncio.current_task()
        pump.cancel()                      # no-op on a finished task
        with pytest.raises(ValueError, match="pump broke"):
            try:
                await pump
            except asyncio.CancelledError:
                if owner is not None and owner.cancelling():
                    raise
                if not pump.cancelled():
                    raise

    asyncio.run(main())
