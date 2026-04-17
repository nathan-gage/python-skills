---
title: Use assert_never for Exhaustiveness Checks
impact: HIGH
impactDescription: turns "missing variant" into a type-check error
tags: error, exhaustiveness, typing, assert-never
references: https://docs.python.org/3/library/typing.html#typing.assert_never, https://peps.python.org/pep-0702/, https://typing.python.org/en/latest/spec/narrowing.html#assert-never-and-exhaustiveness-checking
---

## Use `assert_never` for Exhaustiveness Checks

`typing.assert_never()` (Python 3.11+) is the right tool for "I've handled every variant of this union." Static checkers treat the call site as unreachable — if the union grows a new member, the checker reports the missed branch as a type error *before* the code ships. At runtime it raises `AssertionError`, so a missed case still fails loudly even if the checker is bypassed.

This is **separate from** `assert` (the statement). `assert` is debug-only and can be stripped under `-O`; `assert_never` is a function call that always runs and is purpose-built for exhaustiveness narrowing.

**Incorrect (RuntimeError for unreachable branch — checker doesn't help):**

```python
from dataclasses import dataclass

@dataclass
class InitStep: ...
@dataclass
class RunStep: ...
@dataclass
class DoneStep: ...

Step = InitStep | RunStep | DoneStep

def process_step(step: Step) -> Result:
    if isinstance(step, InitStep): return init()
    if isinstance(step, RunStep):  return run()
    if isinstance(step, DoneStep): return done()
    raise RuntimeError(f"unexpected step: {step!r}")  # checker can't tell this is exhaustive
```

If a future change adds `PausedStep` to the union, this function silently falls through to the `RuntimeError` at runtime. The type checker cannot see the gap because `RuntimeError` is not understood as an exhaustiveness assertion.

**Incorrect (plain `assert False` — vanishes under `-O`):**

```python
def process_step(step: Step) -> Result:
    if isinstance(step, InitStep): return init()
    if isinstance(step, RunStep):  return run()
    if isinstance(step, DoneStep): return done()
    assert False, f"unhandled: {step!r}"  # stripped under -O; checker doesn't narrow
```

Under `python -O`, the assertion compiles to nothing and the function falls off the end with `None` (a worse failure). Type checkers also do not treat plain `assert False` as a guaranteed-unreachable signal in the same way as `assert_never`.

**Correct (`assert_never` — type error if the union grows, runtime error if reached):**

```python
from typing import assert_never

def process_step(step: Step) -> Result:
    if isinstance(step, InitStep): return init()
    if isinstance(step, RunStep):  return run()
    if isinstance(step, DoneStep): return done()
    assert_never(step)  # pyright/mypy: error if Step grows a new variant
```

If `Step` later becomes `InitStep | RunStep | DoneStep | PausedStep`, the checker reports that `step` is `PausedStep` at the `assert_never` call — the build breaks before the code ships.

**Use with `match`/`case` the same way:**

```python
from typing import assert_never

def process_step(step: Step) -> Result:
    match step:
        case InitStep(): return init()
        case RunStep():  return run()
        case DoneStep(): return done()
        case _:
            assert_never(step)
```

**Where `assert_never` belongs:**

- Closed sums: `Literal` unions, sealed dataclass hierarchies, discriminated unions
- Enum dispatch where every member must be handled
- Any place where "we covered every case" is a property the checker should enforce

**Backport:** `typing.assert_never` is available from Python 3.11. On older versions, import from `typing_extensions` instead — the semantics are identical and both static checkers recognize either source.
