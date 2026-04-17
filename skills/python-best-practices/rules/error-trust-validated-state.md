---
title: Trust Validated State — Skip Redundant Defensive Checks
impact: MEDIUM
impactDescription: removes clutter and improves resilience
tags: error, validation, defensive
---

## Trust Validated State — Skip Redundant Defensive Checks

Once a value has been validated at the boundary, internal code should trust it. Agents tend to add defensive checks "just in case" deep inside the call chain — the cost is noise, false branches, and the impression that validation elsewhere isn't reliable.

**Incorrect (re-checking already-validated state):**

```python
def fulfill_order(order: ValidatedOrder) -> None:
    if order is None:             # already enforced by type
        raise ValueError("order required")
    if not order.items:           # already enforced by Pydantic validator
        raise ValueError("order must have items")
    if order.total < 0:           # already enforced by validator
        raise ValueError("total must be non-negative")

    for item in order.items:
        process(item)
```

Every one of these checks was already done when `ValidatedOrder` was constructed. Repeating them says "I don't trust the validation."

**Correct (trust the invariants):**

```python
def fulfill_order(order: ValidatedOrder) -> None:
    for item in order.items:
        process(item)
```

Cleaner, faster, and if the validator changes, this function doesn't need updating.

**When defensive checks are appropriate:**

- At trust boundaries (first function to touch external data)
- Around code paths that can bypass the validator (direct construction in tests, deserialization shortcuts)
- When the invariant is load-bearing and a bug elsewhere could silently violate it (use `assert` to document)

```python
def fulfill_order(order: ValidatedOrder) -> None:
    assert order.items, "ValidatedOrder must have items (validator guarantees this)"
    # assertion documents the invariant; runs in dev, stripped in production
    for item in order.items:
        process(item)
```

**Use defaults instead of assertions** when the goal is resilience rather than catching bugs:

```python
# defensive, resilient — use when the system should keep running
timeout = config.timeout if config.timeout > 0 else DEFAULT_TIMEOUT

# defensive, strict — use when a zero timeout means someone messed up
assert config.timeout > 0, "timeout must be positive"
```

Pick based on whether you want the system to fail or to fall back. Don't do both.
