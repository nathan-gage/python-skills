---
title: Derive Expected Values Independently of the Implementation
impact: HIGH
impactDescription: a test that recomputes the code under test proves only self-consistency
tags: value, oracles, assertions
references: https://docs.pytest.org/en/stable/how-to/assert.html
---

## Derive Expected Values Independently of the Implementation

A test whose expected value is computed by the same logic it's testing proves the code equals itself. When the implementation is wrong, the expectation is wrong the same way, and the test passes. Expected values must come from an independent source: a hand-derived constant, a fixture with known semantics, an invariant that holds regardless of the answer, or a reference implementation that won't share the bug.

**Incorrect (oracle mirrors the implementation):**

```python
def test_shipping_cost():
    order = make_order(weight_kg=12, zone="B")
    expected = BASE_RATE[order.zone] + order.weight_kg * PER_KG[order.zone]  # same formula as the code
    assert shipping_cost(order) == expected
```

If `PER_KG["B"]` is wrong, both sides are wrong together — the test can't notice.

**Correct (hand-derived constant; invariants for the general case):**

```python
def test_shipping_cost_zone_b():
    order = make_order(weight_kg=12, zone="B")
    assert shipping_cost(order) == Decimal("41.80")   # 5.80 base + 12 × 3.00, derived by hand

def test_shipping_cost_monotonic_in_weight():
    light = make_order(weight_kg=1, zone="B")
    heavy = make_order(weight_kg=30, zone="B")
    assert shipping_cost(heavy) > shipping_cost(light)  # holds whatever the rates are
```

The constant came from working the example on paper; the invariant survives rate changes. When a hand-derived value would be brittle (large outputs), assert properties instead: length, ordering, round-trip (`parse(serialize(x)) == x`), or comparison against a trivially-correct reference implementation. Snapshot assertions are a last resort for structured output — they catch *change*, not *correctness*, and every intentional change costs a snapshot review.
