---
title: Re-Raise Cancellation After Cleanup
impact: HIGH
impactDescription: a swallowed cancellation turns shutdown and timeouts into hangs
tags: async, cancellation, asyncio, cleanup
references: https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError, https://docs.python.org/3/library/asyncio-task.html#task-cancellation, https://docs.python.org/3/library/asyncio-task.html#asyncio.shield
---

## Re-Raise Cancellation After Cleanup

Cancellation is control flow, not failure. `task.cancel()` delivers `asyncio.CancelledError` at the task's current await, and everything above — `asyncio.timeout`, `TaskGroup`, the caller awaiting the task — relies on that exception propagating back out. A handler that swallows it reports the task as completed: the canceller waits forever, shutdown hangs, timeouts stop timing out. On 3.8+ `CancelledError` subclasses `BaseException` precisely so `except Exception:` can't swallow it by accident; the remaining hazards are broad `BaseException` catches and results collected as values.

**Incorrect (cancellation swallowed in the handler and missed in the results):**

```python
async def run_job(job: Job) -> Result | None:
    try:
        return await execute(job)
    except BaseException:
        logger.exception("job failed")            # cancellation logged as a failure...
        return None                               # ...and swallowed — the canceller hangs

results = await asyncio.gather(*tasks, return_exceptions=True)
failures = [r for r in results if isinstance(r, Exception)]   # CancelledError is BaseException — invisible here
```

**Correct (cleanup, then let it propagate; treat collected cancellations as cancellation):**

```python
async def run_job(job: Job) -> Result | None:
    try:
        return await execute(job)
    except asyncio.CancelledError:
        await asyncio.shield(release_lease(job))  # must-complete cleanup, kept short
        raise                                     # cancellation keeps propagating
    except Exception:
        logger.exception("job failed")
        return None

results = await asyncio.gather(*tasks, return_exceptions=True)
for result in results:
    if isinstance(result, asyncio.CancelledError):
        raise result                              # a cancellation is not a result
    if isinstance(result, BaseException):
        logger.error("task failed: %r", result)
```

`gather(..., return_exceptions=True)` types each element as `T | BaseException` — check `isinstance(result, BaseException)` before using values, and route cancellations back into control flow instead of logging them as failures.

**Cleanup under cancellation:** once `CancelledError` is propagating, every subsequent await in an `except`/`finally` can be cancelled again — shield only the genuinely must-complete part (`asyncio.shield(...)`) and keep it short; an unshielded slow `finally` is a second hang. **Framework caveat:** the `BaseException` guarantee is stdlib-only — some frameworks deliver cooperative cancellation as `Exception` subclasses, so check the hierarchy before assuming a broad `except Exception:` is cancellation-safe there. For broad-catch hygiene generally, see `error-specific-exceptions` in python-best-practices.
