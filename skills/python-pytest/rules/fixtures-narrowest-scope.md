---
title: Give Fixtures the Narrowest Safe Scope
impact: MEDIUM
impactDescription: shared fixture state makes test order a hidden input
tags: fixtures, scope, isolation
references: https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes, https://docs.pytest.org/en/stable/how-to/fixtures.html#higher-scoped-fixtures-are-instantiated-first
---

## Give Fixtures the Narrowest Safe Scope

A fixture's scope is a sharing contract: `session` scope means every test sees the same object, including mutations left by earlier tests. Widening scope for speed trades isolation for it — and the cost surfaces later as tests that pass alone but fail in suite order (or worse, pass only in suite order). Default to `function` scope; widen only when the fixture is expensive *and* the shared object is immutable or reset between uses.

**Incorrect (session-scoped mutable state — tests now interact):**

```python
@pytest.fixture(scope="session")
def db():
    return InMemoryDB()          # every test shares one instance

def test_create_user(db):
    db.insert(User(name="ada"))
    assert db.count(User) == 1   # passes alone; fails after any test that inserted
```

**Correct (function scope for mutable state; widen only immutable expensive setup):**

```python
@pytest.fixture
def db():
    return InMemoryDB()          # fresh per test — order stops mattering

@pytest.fixture(scope="session")
def compiled_schema() -> Schema:
    return Schema.compile(SCHEMA_PATH)   # expensive, read-only: safe to share
```

**When widening scope is safe:** a middle path for expensive-but-mutable resources is to acquire at `session` scope and reset at `function` scope (truncate tables, clear caches) — the sharing is of the *connection*, not the *state*. Declare fixtures as explicit parameters rather than `autouse=True` where possible; autouse hides a dependency every test silently carries, and hidden dependencies are how "why does this test need a database?" questions start.
