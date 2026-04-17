---
title: Never Use Mutable Default Arguments
impact: CRITICAL
impactDescription: prevents shared-state bugs across calls and instances
tags: data, defaults, mutability, dataclass, pydantic
references: https://docs.python.org/3/tutorial/controlflow.html#default-argument-values, https://docs.python.org/3/library/dataclasses.html#mutable-default-values, https://docs.pydantic.dev/latest/concepts/fields/#using-pydanticfield-to-describe-fields
---

## Never Use Mutable Default Arguments

A default argument is evaluated **once**, when the `def`/class statement runs — not each call. A mutable default (`[]`, `{}`, `set()`, a dataclass instance) is therefore **shared across every call** that doesn't override it. The result is a footgun where appending to the "default" list on one call mutates the default for every subsequent call. The same trap exists for dataclass and Pydantic field defaults.

Always use `None` (or a sentinel) and construct the mutable inside the body, or use `default_factory` for dataclasses / Pydantic fields.

**Incorrect (function default — list shared across calls):**

```python
def append_item(item: int, items: list[int] = []) -> list[int]:
    items.append(item)
    return items

append_item(1)  # [1]
append_item(2)  # [1, 2]   ← surprise: same list as before
append_item(3)  # [1, 2, 3]
```

The `[]` was evaluated once at function-definition time. Every call without an explicit `items=` mutates the same object.

**Correct (sentinel + per-call construction):**

```python
def append_item(item: int, items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    items.append(item)
    return items

append_item(1)  # [1]
append_item(2)  # [2]   ← fresh list per call
```

**Incorrect (dataclass — bare mutable default raises `ValueError`, but tempting alternatives are bugs):**

```python
from dataclasses import dataclass

@dataclass
class User:
    tags: list[str] = []   # ValueError: mutable default ... is not allowed: use default_factory
```

The dataclass decorator catches the obvious case. The dangerous variant is sneaking the same list past the check via a class attribute or a shared object — both of which produce the same shared-state bug at runtime.

**Correct (dataclass — `default_factory`):**

```python
from dataclasses import dataclass, field

@dataclass
class User:
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
```

`field(default_factory=list)` calls `list()` once per instance, giving each `User` its own list.

**Incorrect (Pydantic — sharing a list across instances):**

```python
from pydantic import BaseModel

class Config(BaseModel):
    tags: list[str] = []   # Pydantic deep-copies, but rely on intent, not accident
```

Pydantic v2 actually deep-copies the default for each instance, so this happens to work — but the intent is unclear, and the behavior depends on the Pydantic version. Make the factory explicit so future readers (and the type checker) see what you meant.

**Correct (Pydantic — `Field(default_factory=...)`):**

```python
from pydantic import BaseModel, Field

class Config(BaseModel):
    tags: list[str] = Field(default_factory=list)
    settings: dict[str, str] = Field(default_factory=dict)
```

**Heuristic:** if the default value would compare `==` to itself across calls only because it's the *same object*, it's mutable — use `None` + body construction (functions) or `default_factory` (dataclasses, Pydantic). Tuples, frozensets, strings, ints, `None`, and `frozen=True` dataclasses are safe to use directly because they can't be mutated.

**`from __future__ import annotations` does not help here.** The default-value evaluation rule is unrelated to annotation evaluation; the trap fires either way.
