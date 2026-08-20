---
title: Every Task Needs an Owner
impact: HIGH
impactDescription: orphan tasks die silently, leak, and outlive their callers
tags: async, asyncio, tasks, structured-concurrency
references: https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task, https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup
---

## Every Task Needs an Owner

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

`TaskGroup` couples fates: one failure cancels the siblings. That's right when the tasks are one unit of work, and wrong when items are independent and each failure needs its own accounting — then supervise tasks individually, or use `gather(return_exceptions=True)` with explicit `BaseException` handling per result (see `async-preserve-cancellation`).

**When a task must outlive the block** (a background pump, a subscription), ownership becomes explicit bookkeeping: hold a strong reference, and tear the task down where the owner exits — observing what it died of:

```python
self._pump = asyncio.create_task(self._pump_events(), name="event-pump")
...
async def aclose(self) -> None:
    self._pump.cancel()
    try:
        await self._pump                   # lets finally-cleanup finish; a pre-cancellation failure raises here
    except asyncio.CancelledError:
        if not self._pump.cancelled():     # not the pump's cancellation — it's ours; keep propagating
            raise
```

Awaiting after `cancel()` matters twice over: `cancel()` only *requests* cancellation, and the await both lets the task's `finally` blocks finish and surfaces a real exception if the task had already failed before the cancel. Draining with `gather(..., return_exceptions=True)` and ignoring the result silently discards exactly those failures — reserve that for tearing down many tasks whose errors are observed elsewhere (e.g. a done callback). For a pool of short-lived background tasks, the docs-blessed variant is a strong-reference set — `tasks.add(task)` plus a done callback that discards the task and observes its exception. Naming fan-out tasks (`name=...`) pays off the first time a stack dump shows twelve anonymous `Task-17`s. On 3.11+, reach for `TaskGroup` first and treat bare `create_task` as the escape hatch for genuinely longer-lived work.
