# Python Best Practices

**Version 1.0.0**
Python Async Best Practices
August 2026

> **Note:**
> This document is optimized for AI agents and LLMs that maintain, generate,
> or refactor Python codebases. Humans may also find it useful, but the
> guidance, examples, and framing prioritize consistency and pattern-matching
> for AI-assisted workflows.

---

## Abstract

Async and concurrency guidelines for agent consumption. 5 rules covering event-loop discipline: blocking calls, task ownership and structured concurrency, bounded fan-out, preserved cancellation, and deterministic async generator cleanup. Each rule is observational — it describes the pattern and what it costs, shows incorrect and correct code, and cites primary sources where behavior is version-dependent. Rules assume Python 3.11+ (TaskGroup, asyncio.timeout); version splits such as the 3.13 executor sizing change are called out inline and verified by the repository's proofs harness. These failure modes share a signature: they pass single-request smoke tests and surface under load.

---

## Table of Contents

1. [Concurrency & Async](#1-concurrency-async) — **MEDIUM-HIGH**
   - 1.1 [Bound Fan-Out Concurrency](#11-bound-fan-out-concurrency)
   - 1.2 [Close Abandoned Async Generators Deterministically](#12-close-abandoned-async-generators-deterministically)
   - 1.3 [Don't Block the Event Loop](#13-dont-block-the-event-loop)
   - 1.4 [Every Task Needs an Owner](#14-every-task-needs-an-owner)
   - 1.5 [Re-Raise Cancellation After Cleanup](#15-re-raise-cancellation-after-cleanup)

---

## 1. Concurrency & Async

**Impact: MEDIUM-HIGH**

Event-loop discipline. Blocking calls, task ownership, bounded fan-out, deterministic stream cleanup. These failures pass single-request smoke tests and surface under load.

### 1.1 Bound Fan-Out Concurrency

**Impact: MEDIUM (unbounded gather becomes a memory or rate-limit incident under real load)**

`gather` over a per-item coroutine starts *everything at once*. For 10 items that's concurrency; for 10,000 it's 10,000 open sockets, 10,000 in-flight payloads, and a thundering herd against whatever sits downstream. The smoke test with five items passes; production input sizes don't. Concurrent fan-out that scales with input needs an explicit bound sized to the real limit — connection pool, rate limit, memory per item.

**Incorrect (concurrency equals input size):**

```python
async def thumbnail_all(image_urls: list[str]) -> list[Thumbnail]:
    return await asyncio.gather(*(make_thumbnail(url) for url in image_urls))
```

**Correct (semaphore caps in-flight work; the bound is visible and tunable):**

```python
async def thumbnail_all(image_urls: list[str], *, max_concurrent: int = 8) -> list[Thumbnail]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded(url: str) -> Thumbnail:
        async with semaphore:
            return await make_thumbnail(url)

    return await asyncio.gather(*(bounded(url) for url in image_urls))
```

Same interface, but at most eight thumbnails are in flight regardless of input size.

For streaming producers, bound the buffer too: an unbounded queue between a fast producer and a slow consumer just relocates the pile-up — `asyncio.Queue(maxsize=...)` makes the producer wait, which is the backpressure you want.

**Scope:** a fixed handful of coroutines needs no ceremony — the rule triggers when fan-out scales with input size (user-supplied lists, query results, directory walks). Pick bounds from downstream capacity, not from thin air, and expose them as parameters; libraries typically default to unlimited because they can't know the deployment's limits, which makes setting the bound the application's job. Related: `async-own-your-tasks` covers who supervises spawned work; this rule covers how much of it may run at once.

### 1.2 Close Abandoned Async Generators Deterministically

**Impact: MEDIUM (abandoned generators finalize late, on a dying loop, or never)**

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

The same applies to explicitly held iterators: code that obtains an `AsyncIterator` and stops early should call `await it.aclose()` in a `finally` (guard with `getattr(it, "aclose", None)` when the iterator may not be a generator). Stacked stream wrappers tear down LIFO — close the outermost wrapper first and the underlying source last, the reverse of construction order. Consumers that always run to exhaustion don't need any of this — exhaustion finalizes the generator normally.

### 1.3 Don't Block the Event Loop

**Impact: HIGH (one blocking call stalls every task on the loop)**

An event loop runs one callback at a time. A synchronous call inside `async def` — `time.sleep`, a sync HTTP client, a big `pickle.loads`, file I/O on a slow disk — freezes *every* task on the loop until it returns: heartbeats stop, timeouts can't fire, concurrent requests queue behind it. The single-request smoke test passes; the incident happens under load.

**Incorrect (sync work on the loop):**

```python
async def get_report(report_id: str) -> Report:
    raw = cache.get(report_id)                  # sync network round-trip
    if raw is None:
        raw = requests.get(f"{API}/reports/{report_id}").content   # blocks the loop
        time.sleep(0.1)                         # blocks the loop — not just this task
    return pickle.loads(raw)                    # large payloads block for real milliseconds
```

**Correct (async clients for I/O; `to_thread` for blocking calls):**

```python
async def get_report(report_id: str) -> Report:
    raw = await cache.get(report_id)
    if raw is None:
        response = await http_client.get(f"{API}/reports/{report_id}")
        raw = response.content
        await asyncio.sleep(0.1)
    return await asyncio.to_thread(pickle.loads, raw)
```

**What `to_thread` does and doesn't buy:** it passes object references (no copying), and it unblocks the loop — it does not make the work faster. Pure-Python CPU-bound work still serializes on the GIL, so it gains nothing from a thread — reach for a process pool or, better, less work on the hot path (skip re-validating data you already validated). Extension code that releases the GIL (hashing, compression, numeric kernels) does parallelize in threads, and free-threaded 3.13+ builds (PEP 703) can execute Python code in parallel. The default executor behind `asyncio.to_thread` is sized for the machine, not your workload — `min(32, cpu + 4)` threads, counting the *host's* CPUs before 3.13 (even inside a CPU-limited container) and the affinity-aware `process_cpu_count()` on 3.13+. Long-running servers pushing sustained sync work through it should configure a bounded executor deliberately.

**A running thread can't be interrupted.** Offload APIs differ only in what happens to *your await* on cancellation — `asyncio.to_thread` abandons the thread and lets the awaiting task unwind; some offload utilities instead shield the await until the thread returns — but the thread itself always runs to completion. Side effects in offloaded sync code must be safe to finish unobserved, and a deadline around offloaded work bounds the wait, not the work. One subtler blocker: importing a module that does I/O at import time (see `imports-no-side-effects` in python-best-practices) blocks the loop when the first import happens inside async code — another reason imports stay cheap and top-of-file.

### 1.4 Every Task Needs an Owner

**Impact: HIGH (orphan tasks die silently, leak, and outlive their callers)**

A task someone spawns and nobody awaits has three failure modes. The event loop keeps only a weak reference, so a fire-and-forget task can be garbage-collected mid-flight (the `create_task` docs warn about exactly this). Its exception is reported only when the task is collected — "Task exception was never retrieved," long after the cause. And when the spawning code errors out, the task keeps running against torn-down state. `asyncio.gather` has the same orphan problem on failure: the first exception propagates while sibling coroutines keep running unsupervised.

**Incorrect (fire-and-forget; siblings orphaned on error):**

```python
async def handle_order(order: Order) -> None:
    asyncio.create_task(notify_warehouse(order))   # may be GC'd; errors surface at GC time
    results = await asyncio.gather(                # charge fails → refund keeps running, unowned
        charge_card(order),
        reserve_stock(order),
    )
```

**Correct (TaskGroup: block exit awaits everything; one failure cancels the rest):**

```python
async def handle_order(order: Order) -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(notify_warehouse(order))
        tg.create_task(charge_card(order))
        tg.create_task(reserve_stock(order))
```

**When a task must outlive the block** (a background pump, a subscription), ownership becomes explicit bookkeeping: hold a strong reference, and tear the task down where the owner exits —

```python
self._pump = asyncio.create_task(self._pump_events(), name="event-pump")
...
async def aclose(self) -> None:
    self._pump.cancel()
    await asyncio.gather(self._pump, return_exceptions=True)   # drain: let finally blocks finish
```

Cancel-then-drain matters: `cancel()` only *requests* cancellation; awaiting the task afterwards lets its `finally` cleanup complete before the owner leaves. For a pool of short-lived background tasks, the docs-blessed variant is a strong-reference set — `tasks.add(task)` plus a done callback that discards the task and observes its exception. Naming fan-out tasks (`name=...`) pays off the first time a stack dump shows twelve anonymous `Task-17`s. On 3.11+, reach for `TaskGroup` first and treat bare `create_task` as the escape hatch for genuinely longer-lived work.

### 1.5 Re-Raise Cancellation After Cleanup

**Impact: HIGH (a swallowed cancellation turns shutdown and timeouts into hangs)**

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


## References

- https://docs.python.org/3/library/asyncio-dev.html
- https://docs.python.org/3/library/asyncio-task.html
- https://docs.python.org/3/library/asyncio-sync.html
- https://docs.python.org/3/library/asyncio-queue.html
- https://docs.python.org/3/library/contextlib.html#contextlib.aclosing
- https://peps.python.org/pep-0525/
- https://peps.python.org/pep-0703/
