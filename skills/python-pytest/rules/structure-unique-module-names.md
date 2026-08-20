---
title: Keep Test Module Import Identities Collision-Free
impact: LOW-MEDIUM
impactDescription: same-named test modules pass separately and fail when suites compose
tags: structure, collection, imports
references: https://docs.pytest.org/en/stable/explanation/pythonpath.html, https://docs.pytest.org/en/stable/explanation/goodpractices.html#tests-outside-application-code
---

## Keep Test Module Import Identities Collision-Free

Under pytest's default `prepend` import mode, a test module in a non-package directory imports under its bare filename: `service/tests/test_utils.py` and `scripts/tests/test_utils.py` both claim the import name `test_utils`. Collect either tree alone and it passes; collect both in one invocation and pytest raises `ImportPathMismatchError` (or one module shadows the other). The failure appears exactly when suites compose — the combined CI run breaks while every per-project run stays green.

**Incorrect (two non-package trees claim one import identity):**

```
service/tests/test_utils.py      # imports as "test_utils"
scripts/tests/test_utils.py      # also "test_utils" → ImportPathMismatchError when both collect
```

**Correct (unique identities — packaged trees, or unique filenames):**

```
service/tests/__init__.py        # modules import as "service.tests.*"
service/tests/test_service_utils.py
scripts/tests/__init__.py        # distinct package: "scripts.tests.*"
scripts/tests/test_script_utils.py
```

Three ways out, pick one per repository: add `__init__.py` so test trees are packages with distinct package-qualified names; keep flat un-packaged trees but give test modules globally-unique filenames; or set `--import-mode=importlib`, which pytest recommends for new projects and which removes the uniqueness requirement altogether. Per-directory `conftest.py` files are unaffected — many conftests with the same filename are normal, supported pytest design. Naming test modules after what they test (`test_billing_rounding.py`, not a third `test_utils.py`) sidesteps the collision and reads better in failure output anyway.
