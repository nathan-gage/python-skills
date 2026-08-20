---
title: Build Fixture Objects Through Production Constructors
impact: MEDIUM
impactDescription: hand-built partial data discovers required fields one failure at a time
tags: fixtures, factories, validation
references: https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures
---

## Build Fixture Objects Through Production Constructors

A fixture assembled as a raw dict or a partially-filled object encodes a guess about what the code under test requires. Each missing field surfaces as a separate test failure — fix `auth`, rerun, discover `region`, rerun — and the finished fixture is a private fork of the schema that silently rots when the real model gains a field. Build fixtures through the same constructor, validator, or factory production code uses, so a fixture that constructs is a fixture that's complete.

**Incorrect (hand-built dict; schema knowledge duplicated and partial):**

```python
@pytest.fixture
def deploy_config():
    return {                                # guessed shape
        "image": "app:1.2.3",
        "replicas": 2,
        # missing "auth" — first failure; missing "region" — second failure
    }
```

**Correct (canonical constructor; defaults centralized in one factory):**

```python
@pytest.fixture
def make_deploy_config():
    def _make(**overrides: object) -> DeployConfig:
        defaults: dict[str, object] = {
            "image": "app:1.2.3",
            "replicas": 2,
            "auth": AuthRef("deploy-bot"),
            "region": "us-east-1",
        }
        return DeployConfig.validate(defaults | overrides)   # production validator fills/checks the rest
    return _make

def test_scale_up(make_deploy_config):
    config = make_deploy_config(replicas=6)
    assert plan(config).action == "scale-up"
```

The factory-fixture pattern gives every test a *complete, valid* object and lets it name only the fields the behavior under test cares about. When the model grows a required field, one factory changes and the suite keeps compiling. Corollary: when a test's setup needs an elaborate web of unrelated-but-required subsystems, that's the fixture telling you the phases are coupled — stub the orthogonal phase behind its interface rather than feeding it ever-more-complete data.

**Exception — the constructor under test:** tests *of* the constructor or validator itself must not route their inputs through it. Feed raw inputs and assert against independently-derived expectations (see `value-independent-oracles`); a validator test whose fixture already passed the validator can only confirm that the validator agrees with itself.
