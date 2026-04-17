---
title: Use TypedDict or Dataclass Instead of dict[str, Any]
impact: CRITICAL
impactDescription: restores type-checker coverage over config and payloads
tags: types, typeddict, dataclass, any
---

## Use TypedDict or Dataclass Instead of `dict[str, Any]`

When the shape of a dict is known (config objects, API payloads, structured event data), `dict[str, Any]` is a lie — the structure exists, it's just not declared. Every access becomes a runtime gamble. `TypedDict` or `dataclass` restores type-checker coverage.

**Incorrect (dict[str, Any] erases structure):**

```python
from typing import Any

def create_user(config: dict[str, Any]) -> User:
    name = config["name"]          # what type?
    age = config.get("age", 0)     # what type? what's the default type?
    prefs = config.get("prefs", {})  # dict or None or the passed-in value?
    return User(name=name.upper(), age=age + 1, prefs=prefs)
```

The checker can't tell you that `config["name"]` should be a `str`, that `age` should be an `int`, or that `prefs` has its own structure. Every `.upper()` call is unchecked.

**Correct (TypedDict — dict-shaped but typed):**

```python
from typing import TypedDict, NotRequired

class UserPreferences(TypedDict):
    theme: NotRequired[str]
    notifications: NotRequired[bool]

class UserConfig(TypedDict):
    name: str
    age: NotRequired[int]
    prefs: NotRequired[UserPreferences]

def create_user(config: UserConfig) -> User:
    name = config["name"]                     # str
    age = config.get("age", 0)                # int
    prefs = config.get("prefs", {})           # UserPreferences
    return User(name=name.upper(), age=age + 1, prefs=prefs)
```

**Correct (dataclass — when this is an in-memory value, not JSON):**

```python
from dataclasses import dataclass, field

@dataclass
class UserPreferences:
    theme: str = "light"
    notifications: bool = True

@dataclass
class UserConfig:
    name: str
    age: int = 0
    prefs: UserPreferences = field(default_factory=UserPreferences)

def create_user(config: UserConfig) -> User:
    return User(name=config.name.upper(), age=config.age + 1, prefs=config.prefs)
```

**When to pick which:**
- `TypedDict` — for serialization boundaries where the value genuinely is a `dict` (JSON APIs, `**kwargs`)
- `dataclass` — for in-memory values with behavior, defaults, and ergonomics
- `pydantic.BaseModel` — when you also need runtime validation

`dict[str, Any]` is only the right answer for *truly* unstructured data — log context, free-form metadata. If you know the fields, declare them.
