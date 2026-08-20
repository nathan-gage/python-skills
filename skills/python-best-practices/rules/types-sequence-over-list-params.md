---
title: Accept Sequence and Mapping for Read-Only Parameters
impact: MEDIUM
impactDescription: sidesteps invariance errors and documents non-mutation
tags: types, variance, collections, parameters
references: https://mypy.readthedocs.io/en/stable/common_issues.html#variance, https://docs.python.org/3/library/collections.abc.html
---

## Accept `Sequence` and `Mapping` for Read-Only Parameters

`list` and `dict` are invariant: a `list[Button]` is *not* a `list[Widget]` even when `Button` subclasses `Widget`, because a function taking `list[Widget]` could legally append a `Slider` into it. Annotating a read-only parameter as `list[T]` therefore rejects callers holding lists of subtypes — the checker even suggests the fix ("consider using Sequence instead, which is covariant"). The abstract types also document intent: `Sequence` promises the function won't mutate.

**Incorrect (invariant parameter rejects valid callers):**

```python
def render_all(widgets: list[Widget]) -> str:
    return "\n".join(w.render() for w in widgets)

buttons: list[Button] = load_buttons()
render_all(buttons)  # error: Argument 1 has incompatible type "list[Button]"; expected "list[Widget]"
```

**Correct (covariant read-only view):**

```python
from collections.abc import Mapping, Sequence

def render_all(widgets: Sequence[Widget]) -> str:
    return "\n".join(w.render() for w in widgets)

def apply_labels(labels: Mapping[str, str]) -> None: ...
```

`render_all(buttons)` now type-checks, and the signature guarantees the input comes back unmodified.

**Choosing the parameter type:** `Iterable[T]` when one pass is enough (also admits generators), `Sequence[T]` when you need `len()` / indexing / re-iteration, `Mapping[K, V]` for read-only dicts.

**Keep `list[T]` / `dict[K, V]` when the function genuinely mutates:** then the concrete type is the honest one. Return types go the other way: return the concrete type you actually built (`list[T]`), which gives callers the most capability.
