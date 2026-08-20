---
title: Re-Raise Cancellation After Cleanup
impact: HIGH
impactDescription: absorbed cancellation reports success and silently defeats timeouts
tags: async, cancellation, asyncio, cleanup
references: https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError, https://docs.python.org/3/library/asyncio-task.html#task-cancellation, https://docs.python.org/3/library/asyncio-task.html#asyncio.shield
---

## Re-Raise Cancellation After Cleanup

Cancellation is control flow, not failure. `task.cancel()` delivers `asyncio.CancelledError` at the task's current await, and `asyncio.timeout`, `TaskGroup`, and every cancel-and-await shutdown path rely on that exception propagating back out. Code that absorbs it doesn't crash — it *completes*: the task reports success (`task.cancelled()` is `False`), half-done work looks finished, and a surrounding `asyncio.timeout` expires without ever raising `TimeoutError` — the deadline is silently lost. On 3.8+ `CancelledError` subclasses `BaseException` precisely so `except Exception:` can't absorb it by accident; the remaining hazards are broad `BaseException` catches and results collected as values.

**Incorrect (cancellation absorbed in the handler and missed in the results):**

```python
async def run_job(job: Job) -> Result | None:
    try:
        return await execute(job)
    except BaseException:
        logger.exception("job failed")            # cancellation logged as a failure...
        return None                               # ...and absorbed — the task "succeeds"; the timeout or
                                                  # shutdown that cancelled it believes the work finished

results = await asyncio.gather(*tasks, return_exceptions=True)
failures = [r for r in results if isinstance(r, Exception)]   # CancelledError is BaseException — invisible here
```

**Correct (short cleanup, then keep propagating; treat collected cancellations as cancellation):**

```python
async def run_job(job: Job) -> Result | None:
    try:
        return await execute(job)
    except asyncio.CancelledError:
        await release_lease(job)                  # brief, ordinary cleanup — then keep propagating
        raise
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

**Keep cleanup brief:** the handler runs while the task is still being cancelled, so a second cancellation can interrupt any await inside it — keep cleanup brief and local, then `raise`. `await asyncio.shield(coro)` is *not* a must-complete guarantee: it protects the inner work from the outer cancellation, but the awaiting line still raises, and the detached work then needs an owner holding its reference (see `async-own-your-tasks`). Reserve owned-task shield/drain machinery for cleanup that genuinely cannot be interrupted; most cleanup should be short enough to just run inline. **Framework caveat:** the `BaseException` guarantee is stdlib-only — some frameworks deliver cooperative cancellation as `Exception` subclasses, so check the hierarchy before assuming `except Exception:` is cancellation-safe there. For broad-catch hygiene generally, see `error-specific-exceptions` in python-best-practices.
