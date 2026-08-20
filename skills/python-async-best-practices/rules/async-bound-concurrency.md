---
title: Bound Fan-Out Concurrency
impact: MEDIUM
impactDescription: unbounded gather becomes a memory or rate-limit incident under real load
tags: async, asyncio, semaphore, backpressure
references: https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore, https://docs.python.org/3/library/asyncio-queue.html
---

## Bound Fan-Out Concurrency

`gather` over a per-item coroutine starts *everything at once*. For 10 items that's concurrency; for 10,000 it's 10,000 open sockets, 10,000 in-flight payloads, and a thundering herd against whatever sits downstream. The smoke test with five items passes; production input sizes don't. Concurrent fan-out that scales with input needs an explicit bound sized to the real limit — connection pool, rate limit, memory per item.

**Incorrect (concurrency equals input size):**

```python
async def thumbnail_all(image_urls: list[str]) -> list[Thumbnail]:
    return await asyncio.gather(*(make_thumbnail(url) for url in image_urls))
```

**Correct (semaphore caps in-flight work; the bound is visible and tunable):**

```python
async def thumbnail_all(image_urls: list[str], *, max_concurrent: int = 8) -> list[Thumbnail]:
    if max_concurrent < 1:
        raise ValueError(f"max_concurrent must be >= 1, got {max_concurrent}")
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded(url: str) -> Thumbnail:
        async with semaphore:
            return await make_thumbnail(url)

    return await asyncio.gather(*(bounded(url) for url in image_urls))
```

Same interface, but at most eight thumbnails are in flight regardless of input size. The eager bound check matters: a zero-permit semaphore is a deadlock, not a limit.

**In-flight is not admission.** The semaphore bounds concurrent *work*, but `gather` still creates one task per item up front and retains every argument and every result — the task population, the backlog parked on the semaphore, and the result list all scale with input. Fine for bounded lists; for very large or streaming inputs, bound admission too: a fixed pool of workers reading from a bounded queue, windowed scheduling (process a chunk, then the next), or an async iterator that yields results instead of accumulating them. An unbounded queue between a fast producer and a slow consumer just relocates the pile-up — `asyncio.Queue(maxsize=...)` makes the producer wait, which is the backpressure you want.

**Scope:** a fixed handful of coroutines needs no ceremony — the rule triggers when fan-out scales with input size (user-supplied lists, query results, directory walks). Pick bounds from downstream capacity, not from thin air, and expose them as parameters; libraries typically default to unlimited because they can't know the deployment's limits, which makes setting the bound the application's job. Related: `async-own-your-tasks` covers who supervises spawned work; this rule covers how much of it may run at once.
