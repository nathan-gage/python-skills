---
title: Restore Every Mutated Global, Including Absent Ones
impact: MEDIUM-HIGH
impactDescription: leaked env vars and registries corrupt every test that runs after
tags: fixtures, isolation, monkeypatch, environment
references: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
---

## Restore Every Mutated Global, Including Absent Ones

Environment variables, the working directory, module-level registries, class attributes, random seeds — anything process-global that a test mutates outlives the test unless something restores it. The next casualty is whichever test runs after, in an order that varies by `-k` filter and parallel worker, which is how "passes alone, fails in CI" is born. Restoration must also cover the *absent* case: a variable that didn't exist before the test must be deleted after, not left set. And it must run on failure, not just success — teardown in the test body after the asserts doesn't.

**Incorrect (manual mutation; leaks on failure; absent var left set):**

```python
def test_uses_staging_endpoint():
    os.environ["API_ENDPOINT"] = "https://staging.example.com"   # never removed
    os.chdir("/tmp/scratch")                                     # leaks to every later test
    assert client().endpoint.startswith("https://staging")
    del os.environ["API_ENDPOINT"]                               # skipped when the assert fails
```

**Correct (`monkeypatch` — undone automatically, on success and failure alike):**

```python
def test_uses_staging_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("API_ENDPOINT", "https://staging.example.com")
    monkeypatch.chdir(tmp_path)
    assert client().endpoint.startswith("https://staging")
```

`monkeypatch` records prior state — including "was not set" — and restores it in teardown regardless of outcome; `tmp_path` gives an isolated directory instead of a shared scratch location. The same applies to registries and class attributes (`monkeypatch.setattr`, `monkeypatch.setitem`) and to hand-rolled fixtures: put the restore in the fixture's teardown (`yield` + `finally`), never in the test body. If a test needs a *clean* environment rather than one extra variable, `monkeypatch.delenv(..., raising=False)` each variable the code reads — inheriting the developer's shell into assertions is its own order dependency.

**Scope:** the rule targets state tests *mutate*. Process-global state that is immutable for the suite's lifetime — a compiled schema loaded once, a read-only settings snapshot — needs no per-test restoration; wrapping it in teardown machinery is ceremony without isolation value.
