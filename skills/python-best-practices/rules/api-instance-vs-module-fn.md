---
title: Choose the Simplest Namespace That Matches Ownership and Polymorphism
impact: MEDIUM
impactDescription: avoids unnecessary coupling without forcing a binary choice
tags: api, methods, functions, design, namespace
references: https://docs.python.org/3/tutorial/classes.html
---

## Choose the Simplest Namespace That Matches Ownership and Polymorphism

Python lets the same logic live as a module-level function, an instance method, a `@classmethod`, a `@staticmethod`, a method on a `Protocol`, or a method on a `dataclass`. None of these is universally right. Pick the smallest namespace that captures **ownership** (does this operation belong to one object?) and **polymorphism** (will multiple types provide their own version?).

A useful decision order, from simplest to most coupled:

1. **Module-level function** — when the logic is a pure utility that operates on its arguments and doesn't need to be overridden.
2. **Instance method** — when the logic naturally reads as "this object does X" and uses `self`, *or* when subclasses / Protocol implementations need to provide their own version.
3. **`@classmethod`** — alternative constructors, factory methods, things that need the class but not an instance.
4. **`@staticmethod`** — namespace grouping when the helper is conceptually tied to the class but takes no `self`/`cls`. Often a sign a module-level function would do.
5. **Protocol** — when several unrelated types need to provide the same interface and you want structural typing.

There is no "correct" tier; pick the simplest one that fits.

**Incorrect (module-level function awkwardly threading state through `user`):**

```python
def update_user_preferences(user: User, key: str, value: object) -> None:
    user.prefs[key] = value
    user.last_modified = now()

def get_user_display_name(user: User) -> str:
    return f"{user.first_name} {user.last_name}"
```

These mutate or read `user` state, name `user` in their parameter list, and have no second caller type. They belong on `User`.

**Correct (instance methods — ownership matches the object):**

```python
class User:
    def update_preference(self, key: str, value: object) -> None:
        self.prefs[key] = value
        self.last_modified = now()

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**Incorrect (instance method that doesn't need `self` and isn't overridden):**

```python
class DateFormatter:
    def format_iso(self, d: date) -> str:
        return d.isoformat()  # `self` is unused
```

**Correct (module-level function):**

```python
def format_iso(d: date) -> str:
    return d.isoformat()
```

If five subclasses of `DateFormatter` are about to override `format_iso` with locale-specific behavior, the method form is correct after all — polymorphism justifies the coupling.

**`@classmethod` for alternative constructors:**

```python
class Event:
    def __init__(self, kind: str, payload: dict[str, Any]) -> None:
        self.kind = kind
        self.payload = payload

    @classmethod
    def from_json(cls, raw: str) -> "Event":
        data = json.loads(raw)
        return cls(kind=data["kind"], payload=data["payload"])
```

`from_json` doesn't need an instance, but it does need the class for subclass-friendly construction.

**`@staticmethod` is the rarest tier.** If the function takes no `self` and no `cls`, the only reason to attach it to a class is namespacing — and a module-level function is usually cleaner. Reserve `@staticmethod` for cases where the class genuinely makes the helper more discoverable (a small private validator on a model, for example).

**Protocols when the consumer doesn't need to know the producer:**

```python
from typing import Protocol

class JSONSerializable(Protocol):
    def to_json(self) -> str: ...

def write(obj: JSONSerializable, path: Path) -> None:
    path.write_text(obj.to_json())
```

Now any type with `to_json` works — no shared base class, no inheritance.

**Heuristic:** start at module scope. Promote to a method only when ownership or polymorphism *actually* demand it. The cost of starting too coupled (everything on a class) is harder to undo than the cost of starting too loose (a free function you later move).
