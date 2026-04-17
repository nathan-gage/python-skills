---
title: Keep Old Names as Deprecated Aliases
impact: HIGH
impactDescription: enables gradual migration without breakage
tags: api, deprecation, compatibility
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

**Correct (deprecated alias):**

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

**For parameter renames, use `typing.deprecated` (Python 3.13+) or keyword handling:**

```python
def fetch_user(
    user_id: str,
    *,
    timeout: float = 30,
    user_id_alt: str | None = None,  # old name
) -> User:
    if user_id_alt is not None:
        warnings.warn(
            "user_id_alt is deprecated; pass user_id instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        user_id = user_id_alt
    ...
```

**Deprecation policy:**

1. Add the new name. Old name becomes an alias.
2. Emit a `DeprecationWarning` explaining the migration.
3. Document the deprecation in the changelog and docstrings.
4. Remove the alias in a later major version (follow your project's deprecation window — typically one or two releases).

**When you can skip the alias:** the function was never part of the documented public API (starts with `_`, not in `__all__`, not in published docs). Internal renames don't need deprecation.
