---
title: Parametrize Contract-Distinct Partitions
impact: MEDIUM
impactDescription: cases that differ only in data restate one partition; cases that hide logic obscure many
tags: structure, parametrize, partitions
references: https://docs.pytest.org/en/stable/how-to/parametrize.html, https://docs.pytest.org/en/stable/reference/reference.html#confval-empty_parameter_set_mark
---

## Parametrize Contract-Distinct Partitions

`parametrize` earns its keep when each case is a distinct partition of the input space with an independently-derived expected result — boundary, typical, degenerate, error. Ten cases that exercise the same partition with different literals add runtime and noise, not protection; and a parametrized test whose body branches on the case (`if expected_error: ... else: ...`) has grown two tests wearing one name.

**Incorrect (same partition five times; body branches per case):**

```python
@pytest.mark.parametrize("a, b", [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])  # all "two positives"
def test_add(a, b):
    assert add(a, b) == a + b            # oracle mirrors the implementation, too

@pytest.mark.parametrize("value, should_raise", [(5, False), (-1, True)])
def test_set_limit(value, should_raise):
    if should_raise:                     # two contracts sharing a name
        with pytest.raises(ValueError):
            set_limit(value)
    else:
        assert set_limit(value) == 5
```

**Correct (named partitions, independent expecteds; error cases stand alone):**

```python
@pytest.mark.parametrize(
    "quantity, expected",
    [
        pytest.param(1, Decimal("9.99"), id="single-item"),
        pytest.param(12, Decimal("107.89"), id="dozen-crosses-discount-threshold"),
        pytest.param(0, Decimal("0"), id="empty-order"),
    ],
)
def test_order_total(quantity, expected):
    assert order_total(make_order(quantity=quantity)) == expected

def test_set_limit_rejects_negative():
    with pytest.raises(ValueError, match="must be positive"):
        set_limit(-1)
```

`id=` names make a failing case self-describing in the report. When case lists are generated, guard the degenerate outcome: an accidentally-empty parameter set skips silently by default — set `empty_parameter_set_mark = fail_at_collect` so a filter bug that produces zero cases fails collection instead of green-lighting nothing.
