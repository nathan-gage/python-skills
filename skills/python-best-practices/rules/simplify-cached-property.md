---
title: Use @cached_property Only When the Instance Supports It
impact: MEDIUM
impactDescription: defers work safely; misuse causes races and silent staleness
tags: simplify, cached-property, performance, threading
references: https://docs.python.org/3/library/functools.html#functools.cached_property
---

## Use `@cached_property` Only When the Instance Supports It

`@cached_property` is the right tool when the cached value is **derived from effectively immutable inputs**, the getter is **idempotent**, the class **has a writable `__dict__`**, and the instance is not shared across threads racing on first access. Outside that envelope, the convenience masks real bugs: stale caches when inputs mutate, `TypeError` on `__slots__` classes that omit `__dict__`, and duplicated computation when two threads hit the property simultaneously.

The standard library docs are explicit about all of this. Read them once before adding the decorator.

**Incorrect (plain method — recomputes on every call):**

```python
from dataclasses import dataclass

@dataclass
class Report:
    rows: list[Row]

    def summary_stats(self) -> Stats:  # expensive, called many times
        return compute_stats(self.rows)
```

Every call re-walks `self.rows`. If a caller invokes `report.summary_stats()` ten times, you pay ten times.

**Incorrect (eager computation in `__post_init__`):**

```python
@dataclass
class Report:
    rows: list[Row]

    def __post_init__(self) -> None:
        self.stats = compute_stats(self.rows)  # paid even if stats never used
```

You pay at construction time whether or not the caller ever reads `stats`.

**Incorrect (`@cached_property` on mutable inputs — silent staleness):**

```python
from functools import cached_property
from dataclasses import dataclass, field

@dataclass
class Report:
    rows: list[Row] = field(default_factory=list)  # mutable; callers can append

    @cached_property
    def summary_stats(self) -> Stats:
        return compute_stats(self.rows)

r = Report()
r.summary_stats          # caches based on empty rows
r.rows.append(new_row)   # mutates input
r.summary_stats          # still the old cached Stats — stale, no warning
```

The cache lives in `r.__dict__["summary_stats"]`. Mutating `rows` does not invalidate it.

**Incorrect (`@cached_property` on a `__slots__` class with no `__dict__`):**

```python
from functools import cached_property

class Point:
    __slots__ = ("x", "y")  # no __dict__

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @cached_property
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

Point(3, 4).magnitude
# TypeError: cannot use cached_property instance without the underlying attribute
# (no '__dict__' attribute on 'Point' to cache 'magnitude')
```

`cached_property` writes the result into `instance.__dict__`. If the class doesn't have one, the call raises at first access. Either add `"__dict__"` to `__slots__` or use a different caching strategy (`@functools.lru_cache` on a top-level function, an explicit `_cache` field, etc.).

**Correct (lazy and cached, with the inputs effectively immutable):**

```python
from dataclasses import dataclass, field
from functools import cached_property

@dataclass(frozen=True)
class Report:
    rows: tuple[Row, ...]  # immutable container; cannot be mutated after construction

    @cached_property
    def summary_stats(self) -> Stats:
        return compute_stats(self.rows)
```

First access runs `compute_stats`; subsequent accesses return the cached result. Because `rows` is a frozen field of an immutable container, the cache cannot go stale.

**Caveats to keep in mind:**

- **Threading:** the docs warn that `cached_property` is not thread-safe. If two threads access the property for the first time at the same time, the getter may run twice. Use a lock, `functools.lru_cache` on a module-level function, or a one-shot `__post_init__` if the work must happen exactly once.
- **Mutability:** if any input the getter reads can change after first access, the cache is wrong. Make the inputs frozen, or stick with a plain method/`@property`.
- **Idempotency:** the getter must produce the same value for the same instance every time. No randomness, no time-dependence, no I/O whose result varies.
- **`__slots__`:** the class must keep `__dict__` available. Slot-only classes need `"__dict__"` in `__slots__`, or skip the decorator.
- **Equality / hashing:** the cached value lands in `__dict__`. Dataclass `eq=True` won't include it (only declared fields), but `copy.copy` carries the cache over — clear it manually if the copy's inputs differ.
- **`@property` is still right for cheap derivations** — accessor-like computations (`full_name`, `is_valid`) don't need caching.

**For module-level pure functions, use `functools.lru_cache` / `functools.cache` instead** (see `perf-lru-cache-pure-fns`). `@cached_property` is the per-instance equivalent — and only a good fit when the instance meets every condition above.
