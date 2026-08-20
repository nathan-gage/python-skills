"""Proofs for python-best-practices error-* rule claims."""

import asyncio
import subprocess
import sys


def test_cancellederror_is_not_exception():
    """error-specific-exceptions: "asyncio.CancelledError inherits from BaseException, not Exception." """
    assert not issubclass(asyncio.CancelledError, Exception)
    assert issubclass(asyncio.CancelledError, BaseException)


def test_gather_return_exceptions_yields_cancellation_as_value():
    """error-specific-exceptions: "with gather(..., return_exceptions=True), each result is
    T | BaseException — cancellations and other BaseExceptions come back as values interleaved
    with successes."
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
        assert results[1] == "ok"  # interleaved with successes

    asyncio.run(main())


def test_assert_stripped_under_optimize():
    """error-assert-debug-only: "Python emits no code for assert under -O." """
    proc = subprocess.run(
        [sys.executable, "-O", "-c", "assert False, 'never raises under -O'"],
        capture_output=True,
    )
    assert proc.returncode == 0

    proc = subprocess.run([sys.executable, "-c", "assert False"], capture_output=True)
    assert proc.returncode != 0  # without -O the assert fires
