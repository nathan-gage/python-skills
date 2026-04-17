---
title: Trust Validated State Within the Same Trust Domain
impact: MEDIUM
impactDescription: removes clutter without losing real safety
tags: error, validation, defensive, trust-boundary
references: https://docs.pydantic.dev/latest/concepts/validators/, https://docs.python.org/3/library/dataclasses.html#frozen-instances
---

## Trust Validated State Within the Same Trust Domain

Once a value has been validated *and the validated object is immutable, locally constructed, and stays inside the same trust domain*, internal helpers can skip re-checking it. Outside that narrow case, defensive checks may still earn their keep — mutable objects can drift, plugin/untyped callers can construct bad instances, and rehydrated objects (from a cache, a queue, the database) cross a trust boundary even if the type name is the same.

This rule is the cousin of `types-trust-the-checker`. The principle is the same — don't duplicate guarantees the system already provides — but state requires more care than types because state can change after validation.

**Trust-domain checklist before deleting a defensive check:**

1. **Immutability** — the object is frozen, or the field cannot be reassigned after construction.
2. **Locally constructed** — built by code you control, in this process, since the last validation.
3. **No untyped/plugin caller** — no place can produce the type without going through the validator.
4. **No rehydration since validation** — not loaded from cache, queue, RPC, or DB without re-validating.

Meet all four → trust the invariant. Miss one → keep the check.

**Incorrect (re-checking validated immutable state inside the same module):**

```python
from pydantic import BaseModel, model_validator

class ValidatedOrder(BaseModel):
    model_config = {"frozen": True}
    items: list[Item]
    total: int

    @model_validator(mode="after")
    def _check(self) -> "ValidatedOrder":
        if not self.items:
            raise ValueError("order must have items")
        if self.total < 0:
            raise ValueError("total must be non-negative")
        return self


def fulfill_order(order: ValidatedOrder) -> None:
    if order is None:             # type already excludes None
        raise ValueError("order required")
    if not order.items:           # validator guarantees this
        raise ValueError("order must have items")
    if order.total < 0:           # validator guarantees this
        raise ValueError("total must be non-negative")

    for item in order.items:
        process(item)
```

Frozen + validated + local construction + no rehydration → the checks are noise.

**Correct (trust the invariant):**

```python
def fulfill_order(order: ValidatedOrder) -> None:
    for item in order.items:
        process(item)
```

**Keep defensive checks when any condition fails.** Concrete examples:

**Mutable object:**

```python
@dataclass  # not frozen
class Cart:
    items: list[Item]  # callers can mutate after construction

def checkout(cart: Cart) -> None:
    if not cart.items:                      # KEEP — caller could have cleared the list
        raise EmptyCartError()
    ...
```

**Rehydrated from external storage:**

```python
def replay_from_queue(payload: bytes) -> None:
    order = ValidatedOrder.model_validate_json(payload)
    # Validator just ran on this newly-constructed object → no extra check needed here.
    ...

def load_from_cache(key: str) -> ValidatedOrder:
    raw = cache.get(key)
    return ValidatedOrder.model_validate_json(raw)  # KEEP validation — cache crossed a boundary
```

**Untyped or plugin caller:**

```python
def run_user_plugin(plugin: Any) -> None:
    config = plugin.get_config()
    if not isinstance(config, ValidatedConfig):    # KEEP — plugin might return anything
        raise TypeError("plugin returned non-ValidatedConfig")
    ...
```

**Document the invariant once when you do trust it.** A single `assert` (with the caveats from `error-assert-debug-only`) at the entry point can serve as documentation for readers without sprinkling defensive `if` chains through the body:

```python
def fulfill_order(order: ValidatedOrder) -> None:
    assert order.items, "ValidatedOrder validator guarantees non-empty items"
    for item in order.items:
        process(item)
```

**Resilience vs. strictness.** When the goal is "keep running on bad input" rather than "catch a bug," reach for a default rather than a check-and-raise:

```python
# resilient — fall back when config is missing or malformed
timeout = config.timeout if config.timeout > 0 else DEFAULT_TIMEOUT
```

Pick one — fail or fall back — not both. Defensive checks belong where the four-item checklist above doesn't pass.
