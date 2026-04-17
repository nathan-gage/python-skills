---
title: Use Tuple Syntax in isinstance() Checks
impact: LOW
impactDescription: tuple syntax is measurably faster than union syntax
tags: perf, isinstance, micro-optimization
---

## Use Tuple Syntax in `isinstance()` Checks

`isinstance(x, (A, B, C))` and `isinstance(x, A | B | C)` both work. The tuple form is faster at runtime because the union form constructs a `types.UnionType` every call. For hot paths, prefer the tuple.

**Incorrect (union syntax has allocation overhead):**

```python
def is_primitive(x: object) -> bool:
    return isinstance(x, int | float | str | bool)  # builds a union type each call
```

**Correct (tuple has no per-call overhead):**

```python
def is_primitive(x: object) -> bool:
    return isinstance(x, (int, float, str, bool))
```

Both forms are semantically equivalent. The tuple version is faster because Python constructs the union type on every call (in older versions) or does extra work comparing against it (in newer versions).

**When the difference matters:**

- Called many times per second in a hot path
- Inside a tight inner loop

**When it doesn't matter:**

- Called a few times per request
- Rare code paths

**Note on annotations vs. runtime checks:** the union syntax (`X | Y`) is idiomatic in type annotations and has zero cost there (annotations aren't evaluated at runtime with `from __future__ import annotations`). The tuple form is only better for the specific case of `isinstance()` calls — other places `X | Y` appears, prefer the union syntax.

**Apply consistently** — it's a simple swap, and codebases that use both forms interchangeably make profiling results less predictable. Pick the tuple form once for all `isinstance` checks and move on.
