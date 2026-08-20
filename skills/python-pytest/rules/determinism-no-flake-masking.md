---
title: Fix Nondeterminism, Don't Mask It
impact: HIGH
impactDescription: every masking mechanism converts a diagnosable bug into a permanent tax
tags: determinism, flaky, retries
references: https://docs.pytest.org/en/stable/how-to/flaky.html
---

## Fix Nondeterminism, Don't Mask It

A flaky test is evidence: a race, an order dependency, leaked state, or a timing assumption — in the test or in the code under test. Rerun plugins, widened timeouts, `flaky` markers, and intermittent `xfail` all convert that evidence into permanent noise: the bug stays, the suite slows, and every future flake hides behind the masking already in place. Masking also inverts the incentive — once retries are normal, nobody investigates the first failure.

**Incorrect (each mechanism hides the same unfixed race):**

```python
@pytest.mark.flaky(reruns=3)                    # passes on the third try ≠ passes
def test_cache_eviction(): ...

@pytest.mark.xfail(reason="sometimes fails on CI")   # non-strict: quietly ignores both outcomes
def test_concurrent_writes(): ...

# conftest.py
FLAKY_TIMEOUT = 30  # was 5; raised until CI stopped failing
```

**Correct (make the failure reproducible, then fix the cause):**

```python
def test_cache_eviction():
    clock = FakeClock()                          # control the time the race depended on
    cache = Cache(max_age=60, clock=clock)
    cache.set("k", "v")
    clock.advance(61)
    assert cache.get("k") is None
```

The repair toolkit: control the sources of nondeterminism (inject clocks, seed RNGs, synchronize on events per `determinism-sync-not-sleep`), isolate leaked state (`fixtures-restore-global-state`), and reproduce order dependence by running the failing test alone and with `-p no:randomly` / a fixed seed to bisect. When a fix genuinely can't land now, a *strict, linked* skip is the honest parking spot: `pytest.mark.skip(reason="racy: see ISSUE-123")` — visible, tracked, and not silently consuming retries on every run.
