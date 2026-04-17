---
title: Use assert for Invariants, Not RuntimeError
impact: MEDIUM-HIGH
impactDescription: documents assumptions and fails fast in development
tags: error, assert, invariants
---

## Use `assert` for Invariants, Not `RuntimeError('internal error')`

`assert` documents "this can't happen" — and fails loudly in development if it does. `RuntimeError("internal error")` obscures the intent and fires the same in production, making programming errors look like runtime issues. Reserve exceptions for conditions the caller can reasonably respond to.

**Incorrect (RuntimeError for impossible state):**

```python
def process_step(step: Step) -> Result:
    match step:
        case InitStep():  return init()
        case RunStep():   return run()
        case DoneStep():  return done()

    raise RuntimeError("unexpected step")  # shouldn't be reachable if types are right
```

If a new `Step` variant is added and this function isn't updated, `RuntimeError("unexpected step")` fires in production. It looks like a runtime problem — but it's a coding error the type system should have caught.

**Correct (assert_never for exhaustiveness; assert for invariants):**

```python
from typing import assert_never

def process_step(step: Step) -> Result:
    match step:
        case InitStep(): return init()
        case RunStep():  return run()
        case DoneStep(): return done()
        case _: assert_never(step)  # type error at check time if new variant added
```

`assert_never(step)` is specifically designed for this — the checker will raise a type error if `Step` grows a new variant and the match isn't updated.

**Use `assert` for preconditions the checker can't express:**

```python
def binary_search(items: list[int], target: int) -> int:
    assert items == sorted(items), "binary_search requires sorted input"
    ...
```

This fails fast in development; in production with `-O`, asserts are stripped — which is appropriate because by then the invariant is trusted.

**When to raise an exception instead:**

- The caller could reasonably recover (`FileNotFoundError`, `ValidationError`)
- The input came from an untrusted boundary (user input, external API)
- The failure mode is meaningful to the caller (`PermissionError`, `TimeoutError`)

**When to `assert`:**

- "This can't happen if the rest of the code is correct"
- Internal invariants the checker can't fully enforce
- Sanity checks during development

If the condition *can* happen, make it a real exception with a meaningful type. If it genuinely shouldn't happen, `assert` it.
