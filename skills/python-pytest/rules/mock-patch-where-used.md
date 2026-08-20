---
title: Patch Where the Name Is Looked Up, Not Where It's Defined
impact: MEDIUM-HIGH
impactDescription: a patch at the definition site silently misses the import already taken
tags: mock, patch, imports
references: https://docs.python.org/3/library/unittest.mock.html#where-to-patch
---

## Patch Where the Name Is Looked Up, Not Where It's Defined

`from payments.gateway import charge` copies the function reference into the importing module's namespace at import time. Patching `payments.gateway.charge` afterwards rebinds the *original* module's name — the copy in the module under test still points at the real function, and the test either hits the network or asserts against a mock that was never called. Patch the name in the namespace where the code under test looks it up.

**Incorrect (patched the definition site; the copy is untouched):**

```python
# app/checkout.py
from payments.gateway import charge

def submit_order(order: Order) -> Receipt:
    return charge(order.total)

# tests/test_checkout.py
def test_submit_order(mocker):
    fake = mocker.patch("payments.gateway.charge")   # checkout.charge still the real one
    submit_order(make_order())
    fake.assert_called_once()                        # AssertionError: not called
```

**Correct (patch the lookup site):**

```python
def test_submit_order(mocker):
    fake = mocker.patch("app.checkout.charge", return_value=Receipt(ok=True))
    submit_order(make_order())
    fake.assert_called_once()
```

The rule falls out of Python's name binding, so the *code style* determines the patch target: code that does `import payments.gateway` and calls `payments.gateway.charge(...)` looks the name up on the module object at call time, so patching `payments.gateway.charge` works from anywhere. Either way, the question to ask is "which namespace does the code under test read this name from at call time?" — patch that one. (This is the mechanics rule; whether the boundary *should* be mocked at all is `mock-stable-boundaries`.)

**When patching isn't the fix:** a test that needs a stack of patches to reach its subject is measuring the code's wiring, not its behavior — the code is saying its dependencies aren't injectable. Pass the collaborator as a parameter and patch nothing (see `mock-stable-boundaries`); reserve `patch` for names that genuinely can't be injected.
