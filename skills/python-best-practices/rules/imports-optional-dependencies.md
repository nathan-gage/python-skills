---
title: Handle Optional Dependencies Explicitly
impact: MEDIUM
impactDescription: clear error messages instead of cryptic ImportError
tags: imports, optional-dependencies, packaging
---

## Handle Optional Dependencies Explicitly

When a package has optional integrations (e.g., Anthropic support in a multi-provider library), importing the module should not require every optional dep. Handle `ImportError` at module scope with a helpful message pointing to the install extra.

**Incorrect (bare import crashes if the dep isn't installed):**

```python
import anthropic

class AnthropicProvider:
    ...
```

A user who installed just `pip install mylib` and never wanted Anthropic support still gets a crash if any code path accidentally imports this module.

**Incorrect (silently swallowing the ImportError):**

```python
try:
    import anthropic
except ImportError:
    anthropic = None  # downstream code randomly breaks

class AnthropicProvider:
    def __init__(self):
        client = anthropic.Client()  # AttributeError: 'NoneType' has no 'Client'
```

The failure surfaces as a bizarre `AttributeError` far from the root cause.

**Correct (raise with an actionable install hint):**

```python
try:
    import anthropic
except ImportError as e:
    raise ImportError(
        "anthropic is required for AnthropicProvider. "
        "Install with: pip install 'mylib[anthropic]'"
    ) from e

class AnthropicProvider:
    ...
```

The error message tells the user exactly how to fix it. The original `ImportError` is preserved via `from e` for debugging.

**Pairing with `TYPE_CHECKING` for type hints** (see `types-type-checking-imports`):

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import anthropic

try:
    import anthropic as _anthropic_runtime
except ImportError as e:
    raise ImportError(
        "anthropic is required. Install with: pip install 'mylib[anthropic]'"
    ) from e

class AnthropicProvider:
    def __init__(self, client: anthropic.Client) -> None:  # type-hint works
        self._client = client
```

**When to import inside functions instead:**

If the dependency is truly optional at the *feature* level (not the *module* level), defer the import into the function that needs it. Users who never call that function never pay the import cost, and missing the dep only fails if the feature is actually used.

```python
def export_to_parquet(data: list[dict], path: Path) -> None:
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise ImportError(
            "pyarrow is required for Parquet export. "
            "Install with: pip install 'mylib[parquet]'"
        ) from e
    ...
```

Use module-scope for deps the module's public classes require. Use function-scope for features gated behind specific function calls.
