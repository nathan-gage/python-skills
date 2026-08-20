---
title: Keep Test Module Import Identities Collision-Free
impact: LOW-MEDIUM
impactDescription: same-named test modules pass separately and fail when suites compose
tags: structure, collection, imports
references: https://docs.pytest.org/en/stable/explanation/pythonpath.html, https://docs.pytest.org/en/stable/explanation/goodpractices.html#tests-outside-application-code
---

## Keep Test Module Import Identities Collision-Free

Under pytest's default `prepend` import mode, a test module's import identity is derived by walking up from the file through consecutive `__init__.py` directories: a module in a non-package directory imports under its bare filename, and a `tests/` package whose *parent* is not a package imports as `tests.<module>`. Two trees can therefore claim the same identity — `service/tests/test_utils.py` and `scripts/tests/test_utils.py` collide as `test_utils` (no packages) *and still collide* as `tests.test_utils` if only the `tests/` directories carry `__init__.py`. Either tree passes alone; collecting both in one invocation raises `ImportPathMismatchError`. The failure appears exactly when suites compose.

**Incorrect (same identity — with or without a lone `tests/__init__.py`):**

```
service/tests/test_utils.py      # "test_utils"        — collides with:
scripts/tests/test_utils.py      # "test_utils"
# adding only service/tests/__init__.py and scripts/tests/__init__.py
# renames both to "tests.test_utils" — still one identity, still colliding
```

**Correct (globally-unique filenames — simplest; or importlib mode):**

```
service/tests/test_service_utils.py
scripts/tests/test_script_utils.py
```

```toml
[tool.pytest.ini_options]
addopts = "--import-mode=importlib"   # pytest's recommendation for new projects;
                                      # removes the uniqueness requirement entirely
```

Three ways out, pick one per repository: globally-unique test module filenames (naming modules after what they test — `test_billing_rounding.py`, not a third `test_utils.py` — does this as a side effect and reads better in failure output); `--import-mode=importlib`, recommended for new projects, with the caveat that test modules then can't import *each other* by bare name; or full package chains — `__init__.py` from a uniquely-named root all the way down (`service/__init__.py` + `service/tests/__init__.py` → `service.tests.test_utils`), not just in the `tests/` directory.

**Scope:** per-directory `conftest.py` files with the same filename are normal, supported pytest design and are not what collides here.
