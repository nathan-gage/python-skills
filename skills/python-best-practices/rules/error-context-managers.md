---
title: Use with / async with for Resource Lifetimes
impact: HIGH
impactDescription: deterministic cleanup even on exceptions
tags: error, context-manager, resources, cleanup
references: https://docs.python.org/3/reference/compound_stmts.html#the-with-statement, https://docs.python.org/3/library/contextlib.html, https://peps.python.org/pep-0492/#asynchronous-context-managers-and-async-with
---

## Use `with` / `async with` for Resource Lifetimes

Any object that owns a finite resource — file handles, network sockets, database connections, locks, temporary directories, HTTP clients, GPU contexts — should be acquired with `with` (or `async with`). The context-manager protocol guarantees `__exit__` runs even when the body raises, so cleanup happens deterministically. Manual `close()` calls forget to fire on exceptions, leak resources under failure, and are easy to misorder during refactors.

The same applies to async resources: `async with` exists for `aiohttp` sessions, `httpx.AsyncClient`, `asyncio.Lock`, `anyio` task groups, and async DB drivers. Use it.

**Incorrect (manual close — leaks on exception):**

```python
def write_report(path: Path, rows: list[Row]) -> None:
    f = path.open("w")
    for row in rows:
        f.write(format_row(row))   # if this raises, f is never closed
    f.close()
```

If `format_row` raises midway, `f.close()` never runs. The handle leaks, the file may be left in a partially-written state, and on Windows the path is locked until garbage collection.

**Incorrect (try/finally — works but verbose; the language gave you `with` for a reason):**

```python
def write_report(path: Path, rows: list[Row]) -> None:
    f = path.open("w")
    try:
        for row in rows:
            f.write(format_row(row))
    finally:
        f.close()
```

`with` collapses this to one line and removes the chance of forgetting `try`/`finally` next time.

**Correct (`with` — close runs on success, exception, or early return):**

```python
def write_report(path: Path, rows: list[Row]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(format_row(row))
```

**Resources that must be acquired with a context manager:**

- **Files:** `open(...)`, `tempfile.TemporaryDirectory()`, `tempfile.NamedTemporaryFile()`
- **Locks:** `threading.Lock()`, `threading.RLock()`, `asyncio.Lock()`
- **Network clients:** `httpx.Client()`, `httpx.AsyncClient()`, `aiohttp.ClientSession()`
- **Database connections / sessions:** `sqlite3.connect()`, SQLAlchemy `Session()`, async DB drivers
- **Subprocess pipes:** `subprocess.Popen` (3.2+ supports `with`)
- **Anything from `contextlib`:** `redirect_stdout`, `suppress`, `chdir` (3.11+), `closing()`

**Async clients use `async with`:**

```python
import httpx

async def fetch_user(user_id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return User.model_validate_json(response.content)
```

`async with` runs `__aexit__` even if `await client.get(...)` raises or the task is cancelled.

**Stack multiple resources with `contextlib.ExitStack` (or one `with` statement):**

```python
from contextlib import ExitStack

def merge_files(inputs: list[Path], output: Path) -> None:
    with ExitStack() as stack:
        out = stack.enter_context(output.open("w"))
        ins = [stack.enter_context(p.open()) for p in inputs]
        for src in ins:
            for line in src:
                out.write(line)
```

`ExitStack` closes all resources in reverse order, even if one of the `enter_context` calls raises.

**Write your own with `@contextmanager`:**

```python
from contextlib import contextmanager
from collections.abc import Iterator

@contextmanager
def acquire_lease(resource_id: str) -> Iterator[Lease]:
    lease = lease_service.acquire(resource_id)
    try:
        yield lease
    finally:
        lease_service.release(lease.id)

with acquire_lease("worker-42") as lease:
    do_work(lease)
```

Use the async variant `@contextlib.asynccontextmanager` for resources awaited during acquisition or release.

**Heuristic:** if you find yourself writing `try` / `finally` to call `close()`, `release()`, `disconnect()`, or `unlink()`, you almost certainly want `with` instead.
