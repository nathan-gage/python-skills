---
title: Never Use Mutable Default Arguments
impact: CRITICAL
impactDescription: prevents shared-state bugs across calls and instances
tags: data, defaults, mutability, dataclass, pydantic
references: https://docs.python.org/3/tutorial/controlflow.html#default-argument-values, https://docs.python.org/3/library/dataclasses.html#mutable-default-values, https://docs.pydantic.dev/latest/concepts/fields/#using-pydanticfield-to-describe-fields
---

## Never Use Mutable Default Arguments

A default argument is evaluated **once**, when the `def` statement runs — not each call. A mutable default (`[]`, `{}`, `set()`, a dataclass instance) is therefore shared across every call that doesn't override it: appending to the "default" list on one call mutates the default for every subsequent call. Use `None` + body construction, or a factory. The same *syntax* behaves three different ways — plain functions share the one object (the bug), `@dataclass` refuses it outright, and Pydantic v2 deep-copies it per instance — so the fix differs by context; see below.

**Incorrect (the `[]` is one object, reused across calls):**

```python
def append_item(item: int, items: list[int] = []) -> list[int]:
    items.append(item)
    return items

append_item(1)  # [1]
append_item(2)  # [1, 2]   ← surprise: same list as before
```

**Correct (function — sentinel + per-call construction):**

```python
def append_item(item: int, items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    items.append(item)
    return items
```

**Correct (dataclass / Pydantic — `default_factory` calls the constructor per instance):**

```python
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

@dataclass
class User:
    tags: list[str] = field(default_factory=list)

class Config(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

**Scope — same syntax, three behaviors:** a plain `def` shares the single default object — the bug this rule exists for. `@dataclass` *rejects* bare mutable defaults with `ValueError`, steering you to `default_factory`. Pydantic v2 is not the same trap: it deep-copies unhashable mutable defaults per instance, so `tags: list[str] = []` on a model works — `Field(default_factory=list)` stays preferable for clarity and for hashable mutable defaults, and `Field(default_factory=list, validate_default=True)` when the generated default itself must be validated (default validation is opt-in, separate from the factory) — but none of that is a correctness fix there; don't flag model defaults as the function-argument bug. Safe to use directly as defaults anywhere: tuples, frozensets, strings, ints, `None`, and frozen dataclasses — provided their *contents* are immutable too; a tuple of lists shares the inner lists just the same. Transitive immutability, not surface type, is the property that matters.
