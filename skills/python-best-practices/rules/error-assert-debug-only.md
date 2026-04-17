---
title: Use assert Only for Debug-Only Internal Invariants
impact: HIGH
impactDescription: prevents production checks from silently disappearing under -O
tags: error, assert, invariants, debug
references: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
---

## Use `assert` Only for Debug-Only Internal Invariants

`assert` is a **debug-only** statement. The Python language reference is explicit: assertions emit no code when Python is run with `-O` (or `PYTHONOPTIMIZE`), so the check disappears in optimized builds. That makes `assert` the right tool for "this can never happen if my code is correct" — and the *wrong* tool for any check that must run in production.

**Incorrect (using `assert` to enforce a runtime contract that must hold):**

```python
def transfer_funds(account_id: str, amount: int) -> None:
    assert amount > 0, "amount must be positive"  # vanishes under -O
    assert account_id, "account_id required"      # vanishes under -O
    ...
```

If this module is imported into a service deployed with `python -O`, both checks compile to nothing. A negative `amount` will sail through and corrupt state; the contract is gone.

**Incorrect (using `assert` for input validation):**

```python
def parse_request(payload: bytes) -> Request:
    data = json.loads(payload)
    assert "user_id" in data, "missing user_id"  # never trust user input via assert
    ...
```

User-supplied input must be validated with real exceptions — assertions can be optimized away, and even when present they raise `AssertionError`, which is a poor signal at a system boundary.

**Correct (use `assert` only for "this is impossible if the rest of the code is correct"):**

```python
def process_step(step: Step) -> Result:
    # Step is a closed union; reaching the default branch is a programmer error.
    if isinstance(step, InitStep): return init()
    if isinstance(step, RunStep):  return run()
    if isinstance(step, DoneStep): return done()
    assert False, f"unhandled Step variant: {step!r}"  # debug aid only
```

The assertion documents the invariant. In development it fires loudly if the union grows a new variant; in production with `-O` it's gone, but at that point you're trusting the type system to have caught the gap. (For exhaustiveness specifically, `typing.assert_never` is sharper — see `error-assert-never-exhaustiveness`.)

**Correct (use real exceptions for anything that must hold in production):**

```python
def transfer_funds(account_id: str, amount: int) -> None:
    if not account_id:
        raise ValueError("account_id required")
    if amount <= 0:
        raise ValueError("amount must be positive")
    ...
```

`ValueError` (or a domain-specific exception) is meaningful to callers, can be caught and handled, and survives `-O`.

**Use `assert` when:**

- The condition is a programmer-error invariant the type system can't fully express ("this list is sorted," "this counter is non-negative by construction")
- You want a sanity check during development that's free in production
- A `# noqa`-style "I know this can't happen" comment would otherwise be tempting

**Use a real exception when:**

- The check guards against caller mistakes (`ValueError`, `TypeError`)
- The input crosses a trust boundary (user input, external API, deserialized data)
- The failure mode is meaningful to the caller (`PermissionError`, `TimeoutError`, custom domain types)
- The check must run in production no matter how the interpreter is invoked

If you can't articulate why losing the check under `-O` is acceptable, it shouldn't be an `assert`.
