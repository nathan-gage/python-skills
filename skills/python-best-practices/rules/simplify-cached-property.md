---
title: Use @cached_property for Expensive Derived Attributes
impact: MEDIUM
impactDescription: defers computation and avoids recomputation
tags: simplify, cached-property, performance
---

## Use `@cached_property` for Expensive Derived Attributes

When an attribute is computed from other fields, is expensive, and doesn't change over the object's lifetime, `@cached_property` is the right tool. It defers computation until first access and caches the result — avoiding both wasted work when the attribute is never used and repeated work when it's used many times.

**Incorrect (plain method — recomputes on every call):**

```python
from dataclasses import dataclass

@dataclass
class Report:
    rows: list[Row]

    def summary_stats(self) -> Stats:  # expensive, called many times
        return compute_stats(self.rows)
```

Every call re-walks `self.rows`. If the caller invokes `report.summary_stats()` ten times in a function, you pay ten times.

**Incorrect (eager computation in `__post_init__`):**

```python
@dataclass
class Report:
    rows: list[Row]

    def __post_init__(self) -> None:
        self.stats = compute_stats(self.rows)  # paid even if stats never used
```

You pay at construction time whether or not the caller ever reads `stats`.

**Correct (`@cached_property` — lazy and cached):**

```python
from functools import cached_property
from dataclasses import dataclass

@dataclass
class Report:
    rows: list[Row]

    @cached_property
    def summary_stats(self) -> Stats:
        return compute_stats(self.rows)
```

First access runs `compute_stats`; subsequent accesses return the cached result from `self.__dict__`. If no caller reads `summary_stats`, no work happens.

**Caveats:**

- **Mutability:** if `self.rows` changes after the property is accessed, the cached value is stale. Use `@cached_property` only when the dependencies are effectively immutable.
- **Equality / hashing:** the cache lives in `__dict__`, so it persists across `copy()` unless you clear it. Include `compare=False` on the cache field if using dataclass comparisons.
- **`@property` is still right for cheap derivations** — accessor-like computations (`full_name`, `is_valid`) don't need caching and shouldn't use it.

**Use `functools.lru_cache` for module-level pure functions:**

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def parse_version(s: str) -> Version:
    ...
```

`@cached_property` is the instance-method equivalent.
