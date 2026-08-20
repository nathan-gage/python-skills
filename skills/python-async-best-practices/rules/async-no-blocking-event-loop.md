---
title: Don't Block the Event Loop
impact: HIGH
impactDescription: one blocking call stalls every task on the loop
tags: async, asyncio, blocking, threads
references: https://docs.python.org/3/library/asyncio-dev.html#running-blocking-code, https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread, https://peps.python.org/pep-0703/
---

## Don't Block the Event Loop

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
