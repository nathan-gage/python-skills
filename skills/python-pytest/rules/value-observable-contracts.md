---
title: Commit Tests That Protect Observable Contracts
impact: HIGH
impactDescription: probe tests add runtime and maintenance cost while defending nothing
tags: value, contracts, coverage
references: https://docs.pytest.org/en/stable/explanation/goodpractices.html
---

## Commit Tests That Protect Observable Contracts

A committed test must protect a named, observable behavior with an assertion that fails for a plausible regression. Tests that merely *execute* code — call a function, assert the result "is not None", check no exception was raised — are development probes: useful while writing the code, weight once committed. They pass under almost any regression, so they defend nothing, while still costing runtime, maintenance, and reviewer attention.

**Incorrect (executes code; asserts nothing a regression would break):**

```python
def test_render_invoice():
    invoice = make_invoice(items=3)
    result = render_invoice(invoice)
    assert result is not None          # any non-crashing implementation passes
    assert isinstance(result, str)     # so does one that renders garbage
```

**Correct (names the contract; fails when the contract breaks):**

```python
def test_render_invoice_totals_include_tax():
    invoice = make_invoice(items=[Item(price=100, tax_rate=0.2)])
    result = render_invoice(invoice)
    assert "Total: 120.00" in result   # wrong tax math fails this line
```

Before committing a test, name the contract it defends in the test name. If the honest name is `test_render_invoice_runs`, delete the test — or find the real assertion. Probes written to exercise new code during development are fine as a workflow; the discipline is deleting them before commit instead of promoting them to `skip`, `xfail`, or a literal `assert True`.

One deliberate exception: an explicitly-named smoke contract — `test_all_modules_import`, `test_app_starts_with_default_config` — where "does not crash" *is* the observable contract (import cycles, missing deps, broken entry points are the regressions it defends). The bar is the same: the name states what surviving means, and the test exists on purpose, not as a leftover probe.
