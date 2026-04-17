---
title: Never Use Bare `except:`
impact: HIGH
impactDescription: bare except swallows KeyboardInterrupt, SystemExit, and async cancellation
tags: error, exceptions, bare-except
references: https://docs.python.org/3/tutorial/errors.html#handling-exceptions, https://docs.python.org/3/library/exceptions.html#BaseException, https://peps.python.org/pep-0008/#programming-recommendations
---

## Never Use Bare `except:`

`except:` (with no exception type) catches **`BaseException`** — every exception in the interpreter, including the ones you must not silently swallow:

- `KeyboardInterrupt` — Ctrl-C
- `SystemExit` — `sys.exit()`, normal interpreter shutdown
- `asyncio.CancelledError` (3.8+) and `BaseExceptionGroup` (3.11+) — async cancellation
- `MemoryError`, `GeneratorExit`, internal interpreter signals

Bare `except` is broader than `except Exception:`, and the breadth is exactly the problem. PEP 8 calls it out: *"A bare `except:` clause will catch `SystemExit` and `KeyboardInterrupt` exceptions, making it harder to interrupt a program with Control-C."* `flake8` / `ruff` flag it as `E722`. Treat any bare `except:` as a bug.

**Incorrect (bare except — Ctrl-C cannot interrupt this loop):**

```python
while True:
    try:
        process_one()
    except:                      # E722: bare except
        log("retrying")
        time.sleep(1)
```

A user who hits Ctrl-C is ignored. A `sys.exit()` from a child function is ignored. An async `CancelledError` is swallowed and the task hangs.

**Incorrect (`except BaseException:` — same problem, spelled out):**

```python
try:
    do_work()
except BaseException:           # don't catch BaseException directly either
    log("done")
```

Catching `BaseException` is the explicit form of the same mistake.

**Correct (catch what you actually intend to handle):**

```python
while True:
    try:
        process_one()
    except (TimeoutError, ConnectionError) as exc:
        log("retrying", exc_info=exc)
        time.sleep(1)
    # KeyboardInterrupt, SystemExit, CancelledError propagate as they should
```

**Correct when you need a true catch-all (last line of defense — log and re-raise):**

```python
def handle_request(req: Request) -> Response:
    try:
        return process(req)
    except Exception:           # NOT bare; excludes BaseException-only types
        logger.exception("unhandled error in request handler")
        raise                   # never swallow
```

Use `except Exception:` (not bare) at the outermost layer of a request handler, worker loop, or top-level entrypoint where you must log unexpected errors. Always re-raise — see `error-specific-exceptions` for the broader handler discussion, and `error-preserve-cancellation` for why `CancelledError` must reach the event loop.

**The only legitimate use of `except BaseException:`** is in framework-level cleanup code that genuinely must run before the process exits (e.g., flushing logs in a process supervisor) — and even then, the handler must re-raise. If you're not writing that, you don't need it.
