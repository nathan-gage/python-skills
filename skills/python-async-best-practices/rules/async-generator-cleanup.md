---
title: Close Abandoned Async Generators Deterministically
impact: MEDIUM
impactDescription: abandoned generators finalize late, on a dying loop, or never
tags: async, generators, cleanup, aclosing
references: https://docs.python.org/3/library/contextlib.html#contextlib.aclosing, https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens, https://peps.python.org/pep-0525/#finalization
---

## Close Abandoned Async Generators Deterministically

Leaving an `async for` early — `break`, `return`, an exception — abandons the generator with its `finally` blocks and `async with` cleanup still pending. Nothing runs them at that point: finalization waits for garbage collection or the loop's `shutdown_asyncgens()` at teardown, where the cleanup executes late, on a loop that's shutting down, or surfaces as an unraisable-exception warning after the test that caused it has already passed. Locks held inside the generator stay held in the meantime.

**Incorrect (break abandons the generator; cleanup is deferred to GC):**

```python
async def find_header(path: str) -> Record | None:
    async for record in read_records(path):   # read_records holds a file + connection
        if record.is_header:
            return record                     # generator never finalized here
    return None
```

**Correct (`aclosing` ties cleanup to block exit):**

```python
from contextlib import aclosing

async def find_header(path: str) -> Record | None:
    async with aclosing(read_records(path)) as records:
        async for record in records:
            if record.is_header:
                return record                 # aclose() runs on exit — finally blocks included
    return None
```

`aclose()` throws `GeneratorExit` into the generator at its current `yield`, so its `finally` / `async with` cleanup runs now, in this task, on this loop.

The same applies to explicitly held iterators: code that obtains an `AsyncIterator` and stops early should call `await it.aclose()` in a `finally` (guard with `getattr(it, "aclose", None)` when the iterator may not be a generator). Stacked stream wrappers tear down LIFO — close the outermost wrapper first and the underlying source last, the reverse of construction order.

**When nothing is needed:** consumers that always run to exhaustion finalize the generator normally — `aclosing` there is harmless ceremony, not a requirement.
