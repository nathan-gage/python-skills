---
title: Remember bool Is an int Subtype
impact: MEDIUM
impactDescription: keeps True out of numeric validation, keys, and arithmetic
tags: data, validation, bool, int
references: https://peps.python.org/pep-0285/, https://docs.python.org/3/library/functions.html#bool
---

## Remember `bool` Is an `int` Subtype

`bool` subclasses `int`: `isinstance(True, int)` is `True`, `True == 1`, and `hash(True) == hash(1)`. Any numeric validation, dict key, or arithmetic that should exclude booleans must reject `bool` explicitly — and the check must come *first*, because the `int` check accepts booleans. This bites hardest on deserialized input, where JSON `true` arrives as Python `True` and sails through an `isinstance(..., int)` gate.

**Incorrect (`True` passes as a valid count):**

```python
def set_page_size(value: object) -> int:
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"page size must be a positive integer, got {value!r}")
    return value

set_page_size(True)   # returns True — later arithmetic treats it as 1
{1: "a", True: "b"}   # one entry: True collides with key 1
```

**Correct (reject bool before accepting int):**

```python
def set_page_size(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"page size must be a positive integer, got {value!r}")
    return value
```

Static checkers won't flag any of this — `bool` is a valid `int` to them by design. The discipline lives in runtime validation. Coercing validators may convert rather than reject; use a strict integer type at the model boundary when `true`-as-`1` must not slip through.

**When the subtyping is the feature:** `sum(flags)` counting `True`s, boolean indexing, and arithmetic on comparison results are idiomatic uses of the same relationship — reject bools at *validation* boundaries; don't blanket-ban them from arithmetic.
