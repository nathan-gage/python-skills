---
title: Use Strict xfail So Unexpected Passes Fail
impact: MEDIUM
impactDescription: non-strict xfail silently absorbs both outcomes forever
tags: determinism, xfail, skip
references: https://docs.pytest.org/en/stable/how-to/skipping.html#strict-parameter
---

## Use Strict xfail So Unexpected Passes Fail

`xfail` marks a test that *should* fail today — a known bug, an unimplemented case. Without `strict=True`, an xfail that unexpectedly passes reports `XPASS` and the run stays green: when the bug gets fixed (or the test stops testing anything), nobody is told, and the marker outlives its reason indefinitely. Strict mode makes the marker self-expiring — the moment reality diverges from the annotation, the suite says so.

**Incorrect (non-strict; both outcomes accepted forever):**

```python
@pytest.mark.xfail(reason="negative quantities not supported yet")
def test_refund_negative_quantity():
    assert refund(make_order(), quantity=-1).status == "rejected"
```

If negative-quantity handling ships, this silently flips to `XPASS` and keeps flipping — the marker never gets cleaned up.

**Correct (strict; an unexpected pass fails the run):**

```python
@pytest.mark.xfail(strict=True, reason="negative quantities not supported yet — ISSUE-482")
def test_refund_negative_quantity():
    assert refund(make_order(), quantity=-1).status == "rejected"
```

When the feature lands, the run fails with `[XPASS(strict)]`, and the fix is to delete the marker — the test graduates to a normal regression test. Set `xfail_strict = true` in project config to make strict the default.

**Scope:** `xfail` documents a *deterministic* known failure, never an intermittent one (that's flake-masking — see `determinism-no-flake-masking`); neither `xfail` nor `skip` is a parking spot for development probes that never asserted anything (see `value-observable-contracts`). Non-strict has one honest, time-boxed use: a compatibility matrix where a case is *expected* to vary across platform or dependency versions and both outcomes are informative while support lands — with an owner and an exit date, not as a permanent state.
