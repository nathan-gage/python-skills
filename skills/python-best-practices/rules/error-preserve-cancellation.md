---
title: Preserve Asyncio Cancellation Semantics
impact: HIGH
impactDescription: avoids hung tasks and false-positive review flags
tags: error, asyncio, cancellation, anyio
references: https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError, https://docs.python.org/3/library/exceptions.html#BaseException
---

## Preserve Asyncio Cancellation Semantics

Cancellation in asyncio is delivered by raising `CancelledError` inside the running task. Swallow it and the task hangs past its lifetime; false-flag code that already handles it correctly and you waste review cycles and churn working code.

Two facts do most of the work:

1. On Python 3.8+, `asyncio.CancelledError` inherits from `BaseException`, **not** `Exception`. So `except Exception:` is cancellation-safe. Do not flag `except Exception:` in an async function with "this swallows cancellation" — cite `error-specific-exceptions` reasons (hides bugs, leaks `str(e)`, obscures observability) instead.
2. `except BaseException:` **does** catch `CancelledError`. If you catch it, re-raise it.

**Incorrect (catches cancellation, returns as if successful):**

```python
async def fetch_with_retry() -> Result | None:
    try:
        return await upstream.get()
    except BaseException:          # catches CancelledError
        logger.warning("fetch failed")
        return None                # task now "completes" despite being cancelled
```

**Correct (re-raise cancellation, handle the rest):**

```python
async def fetch_with_retry() -> Result | None:
    try:
        return await upstream.get()
    except asyncio.CancelledError:
        raise                      # cancellation must propagate
    except Exception:
        logger.warning("fetch failed", exc_info=True)
        return None
```

Or just don't use `BaseException`:

```python
async def fetch_with_retry() -> Result | None:
    try:
        return await upstream.get()
    except Exception:              # CancelledError is BaseException — unaffected
        logger.warning("fetch failed", exc_info=True)
        return None
```

**In anyio / structured-concurrency contexts, use `get_cancelled_exc_class`:**

Trio and anyio replace `CancelledError` with their own class (anyio on trio backend uses `trio.Cancelled`). A narrow catch that hardcodes `asyncio.CancelledError` will miss it. If you need to branch on cancellation explicitly inside an anyio task, use the runtime accessor:

```python
import anyio

async def do_work() -> None:
    try:
        await upstream.get()
    except anyio.get_cancelled_exc_class():
        await best_effort_cleanup()
        raise
```

**`finally:` runs during cancellation — keep it bounded.**

Cleanup in `finally:` races against the cancellation itself. Don't await operations that can block indefinitely. If a specific cleanup step must complete, wrap it in `asyncio.shield()`:

```python
async def session() -> None:
    conn = await open_connection()
    try:
        await use(conn)
    finally:
        await asyncio.shield(conn.close())  # survives task cancellation
```

**Review heuristic for `except Exception:` in async code:** flag it for diagnostic precision, client-visible error leaks, or swallowing domain bugs — never for cancellation safety on Python 3.8+. Before claiming otherwise, verify the project's Python version and whether the catch is `Exception` or `BaseException`.
