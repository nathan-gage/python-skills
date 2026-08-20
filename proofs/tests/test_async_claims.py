"""Proofs for python-best-practices async-* rule claims."""

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
