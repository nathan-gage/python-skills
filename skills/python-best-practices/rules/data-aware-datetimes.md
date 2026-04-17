---
title: Use Timezone-Aware Datetimes at Boundaries
impact: HIGH
impactDescription: prevents off-by-hours bugs across timezones, daylight saving, and storage
tags: data, datetime, timezone, boundaries
references: https://docs.python.org/3/library/datetime.html#aware-and-naive-objects, https://docs.python.org/3/library/zoneinfo.html, https://peps.python.org/pep-0615/
---

## Use Timezone-Aware Datetimes at Boundaries

A `datetime` with no `tzinfo` is **naive**: it has no opinion about which timezone it represents. Two naive datetimes that look identical may refer to different absolute moments. Naive datetimes leak into databases, JSON payloads, log lines, and inter-service messages and cause off-by-hours bugs that surface during DST transitions, on a different host, or when a user travels.

The rule: at any boundary the value crosses (HTTP, DB, queue, file format, log line, comparison with another datetime), the datetime must be **timezone-aware**. Inside a tight piece of business logic, naive is acceptable only if every value in scope shares the same explicit assumption — and even then, attaching the timezone is usually clearer.

**Default to UTC for storage and transport. Convert to local timezones only at display.**

**Incorrect (`datetime.utcnow()` returns a naive datetime — silently loses the "UTC" claim):**

```python
from datetime import datetime

def stamp() -> datetime:
    return datetime.utcnow()              # naive! DeprecationWarning in 3.12+
```

`datetime.utcnow()` is deprecated in Python 3.12 precisely because it returns a *naive* datetime that callers misuse as if it were UTC-aware. A serializer that interprets naive as local time will write the wrong value to the database.

**Incorrect (`datetime.now()` is naive and host-local):**

```python
from datetime import datetime

start = datetime.now()                    # naive, in the host's local timezone
log.info("started", start=start)           # serializes ambiguously
```

The same code on two hosts in different timezones records different timestamps for the same event.

**Incorrect (mixing naive and aware in comparisons — `TypeError`):**

```python
from datetime import datetime, timezone

stored = datetime(2026, 4, 17, 12, 0)                        # naive
now = datetime.now(timezone.utc)                              # aware
if stored < now:                                              # TypeError!
    ...
```

The interpreter refuses to compare naive and aware datetimes — a guard against a class of bugs that would otherwise be silent.

**Correct (UTC at every boundary):**

```python
from datetime import datetime, timezone

def stamp() -> datetime:
    return datetime.now(timezone.utc)     # aware, unambiguous

start = datetime.now(timezone.utc)
log.info("started", start=start.isoformat())  # "2026-04-17T12:00:00+00:00"
```

`datetime.now(timezone.utc)` is the modern replacement for `datetime.utcnow()`. The result is aware and round-trips through `isoformat()` / `fromisoformat()` cleanly.

**Correct (named local timezone via `zoneinfo` for display):**

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

stored = datetime.now(timezone.utc)                       # store in UTC
display = stored.astimezone(ZoneInfo("America/Los_Angeles"))  # convert at display
print(display.strftime("%Y-%m-%d %H:%M %Z"))
```

`zoneinfo` (Python 3.9+, PEP 615) reads from the system tzdata; it handles DST and historical offsets correctly. Use named zones (`"America/Los_Angeles"`), not raw offsets (`-08:00`), so DST transitions resolve.

**Correct (parsing user/API input — fail loudly on missing timezone):**

```python
from datetime import datetime, timezone

def parse_iso(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        raise ValueError(f"datetime {s!r} is missing a timezone offset")
    return dt.astimezone(timezone.utc)
```

If your callers can send naive datetimes, decide once whether to reject them or to assume a fixed zone — but never *silently* treat naive as UTC.

**Pydantic / dataclasses:**

```python
from datetime import datetime, timezone
from pydantic import BaseModel, AwareDatetime

class Event(BaseModel):
    occurred_at: AwareDatetime    # Pydantic v2: rejects naive datetimes at validation
```

`pydantic.AwareDatetime` enforces the rule at the model boundary. The standard library doesn't ship a "must be aware" annotation; encode the constraint with a validator or rely on Pydantic.

**Database guidance:**

- PostgreSQL: use `TIMESTAMPTZ` (stores UTC). Driver returns aware datetimes.
- SQLite / MySQL: store ISO-8601 strings with `+00:00`, or store epoch milliseconds.
- ORMs: configure timezone-aware columns explicitly; defaults vary.

**When naive is acceptable:**

- Pure date arithmetic where time-of-day doesn't matter (`date`, not `datetime`)
- A small block of business logic where every value is naive and the timezone is documented in scope
- Integrating with a legacy system whose contract is naive — but convert at the boundary on the way out

**Heuristic:** if the datetime is going to live longer than the function it's created in, it should be aware. Naive datetimes are a sharp local tool, never a transport format.
