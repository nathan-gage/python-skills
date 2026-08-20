---
title: Synchronize on Events, Not Sleeps
impact: HIGH
impactDescription: sleeps prove timing luck, and the flakes arrive with CI load
tags: determinism, concurrency, async, synchronization
references: https://docs.python.org/3/library/asyncio-sync.html#asyncio.Event, https://docs.python.org/3/library/threading.html#threading.Event
---

## Synchronize on Events, Not Sleeps

A sleep in a concurrency test encodes a bet about scheduling: "0.1 s is enough for the worker to finish." On a loaded CI runner the bet loses, and the test flakes; on every other run the bet wins, and the suite still pays the sleep. Ordering and completion are facts the code under test can expose — synchronize on events, barriers, or observable state transitions, with a bounded timeout as the failure path.

**Incorrect (timing bet):**

```python
async def test_worker_processes_job():
    worker.submit(job)
    await asyncio.sleep(0.1)                 # hope the worker ran
    assert job.id in worker.completed
```

**Correct (synchronize on the observable transition):**

```python
async def test_worker_processes_job():
    done = asyncio.Event()
    worker.on_complete(lambda _: done.set())
    worker.submit(job)
    async with asyncio.timeout(5):           # bound the wait, not the assertion
        await done.wait()
    assert job.id in worker.completed
```

The timeout is generous because it's a *failure bound*, not a performance claim — it only matters when the test is already broken. The same applies to threads (`threading.Event`, `Barrier`) and to polling an observable condition with a deadline when no hook exists. Never assert on elapsed-time thresholds to prove ordering ("the second task finished within 50 ms") — host speed is not part of the contract. If the code under test offers no way to observe completion, that's missing design, and the test just found it.

**When time itself is under test** (a debouncer's quiescence window, a TTL), inject a controllable clock and advance it deterministically — that tests the time logic without betting on the scheduler. If the component can't take a clock, one bounded real-time wait on its observable output is the fallback: a deadline, never a proof of ordering.
