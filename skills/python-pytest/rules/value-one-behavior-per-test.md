---
title: One Cohesive Behavior Per Test
impact: MEDIUM
impactDescription: a failure names its cause; unrelated phases don't hide behind the first assert
tags: value, structure, granularity
references: https://docs.pytest.org/en/stable/explanation/goodpractices.html
---

## One Cohesive Behavior Per Test

A test that bundles independently-failing behaviors reports only the first break: everything after the failing assert is unexercised, so one regression masks another. And the test name stops describing what failed. Split when the phases can fail independently; keep a single test when the asserts describe one cohesive outcome.

**Incorrect (three contracts in a trench coat):**

```python
def test_user_service():
    user = service.create(name="ada")
    assert user.id is not None
    service.rename(user.id, "grace")
    assert service.get(user.id).name == "grace"     # if this fails...
    service.delete(user.id)
    assert service.get(user.id) is None             # ...deletion is never exercised
```

**Correct (each behavior fails under its own name):**

```python
def test_create_assigns_id():
    assert service.create(name="ada").id is not None

def test_rename_persists():
    user = service.create(name="ada")
    service.rename(user.id, "grace")
    assert service.get(user.id).name == "grace"

def test_delete_removes_user():
    user = service.create(name="ada")
    service.delete(user.id)
    assert service.get(user.id) is None
```

Multiple asserts are fine when they describe one outcome (`status == 200` and body shape of the same response). The test is too big when its name needs "and". The inverse discipline: merge tests that assert the *same* contract twice, and delete tests obsoleted by a behavior change — keeping them for test-count or coverage optics preserves numbers, not protection.
