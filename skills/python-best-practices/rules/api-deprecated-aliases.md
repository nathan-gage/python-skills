---
title: Keep Old Names as Deprecated Aliases
impact: HIGH
impactDescription: enables gradual migration without breakage
tags: api, deprecation, compatibility
references: https://peps.python.org/pep-0702/, https://docs.python.org/3/library/warnings.html#warnings.deprecated, https://docs.python.org/3/library/warnings.html#warnings.warn
---

## Keep Old Names as Deprecated Aliases

Renaming a public function, class, or parameter is a breaking change. Users upgrade at their own pace; if the old name vanishes, they can't. Keep the old name as a deprecated alias for at least one release, pointing at the new name.

**Incorrect (rename breaks existing code immediately):**

```python
# v1.0
def get_user(user_id: str) -> User: ...

# v1.1
def fetch_user(user_id: str) -> User: ...  # renamed — v1.0 callers now crash
```

**Correct (deprecated alias with `warnings.warn`):**

```python
import warnings

def fetch_user(user_id: str) -> User:
    ...

def get_user(user_id: str) -> User:
    warnings.warn(
        "get_user is deprecated; use fetch_user instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return fetch_user(user_id)
```

Old callers keep working with a warning; new callers use the new name.

**On Python 3.13+, prefer `warnings.deprecated()` for whole functions, classes, and overloads.** PEP 702 added a standard decorator that emits the warning, marks the symbol so static checkers can flag callers, and surfaces the deprecation in IDE tooling. The decorator lives in `warnings`, **not** `typing`:

```python
import warnings  # Python 3.13+

@warnings.deprecated("get_user is deprecated; use fetch_user instead.")
def get_user(user_id: str) -> User:
    return fetch_user(user_id)


@warnings.deprecated("LegacyClient is deprecated; use Client instead.")
class LegacyClient(Client): ...
```

Type checkers that implement PEP 702 (mypy, pyright) report calls to deprecated names without you having to wire `warnings.warn` by hand.

**For renamed parameters, `warnings.deprecated()` does not apply** — it decorates whole symbols, not individual parameters. Use a compatibility keyword path plus a runtime warning inside the function:

```python
import warnings
from typing import Any

_MISSING: Any = object()

def fetch_user(
    user_id: str = _MISSING,
    *,
    timeout: float = 30,
    user_id_alt: str = _MISSING,  # old name; remove in next major
) -> User:
    if user_id_alt is not _MISSING:
        warnings.warn(
            "the user_id_alt parameter is deprecated; pass user_id instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if user_id is _MISSING:
            user_id = user_id_alt
    if user_id is _MISSING:
        raise TypeError("fetch_user() missing required argument: 'user_id'")
    ...
```

The compatibility shim (the old keyword still accepted, then forwarded) is what preserves callers; the `warnings.warn(..., DeprecationWarning, stacklevel=2)` call is what surfaces the migration.

**Deprecation policy:**

1. Add the new name. Old name becomes an alias.
2. Emit a `DeprecationWarning` (via `warnings.warn` or `@warnings.deprecated`) explaining the migration.
3. Document the deprecation in the changelog and docstrings.
4. Remove the alias in a later major version (follow your project's deprecation window — typically one or two releases).

**When you can skip the alias:** the function was never part of the documented public API (starts with `_`, not in `__all__`, not in published docs). Internal renames don't need deprecation.
