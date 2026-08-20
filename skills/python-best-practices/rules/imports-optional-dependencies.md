---
title: Handle Optional Dependencies Explicitly
impact: LOW-MEDIUM
impactDescription: clear, correctly-scoped errors instead of cryptic failures far from the cause
tags: imports, optional-dependencies, packaging
references: https://docs.python.org/3/library/exceptions.html#ModuleNotFoundError
---

## Handle Optional Dependencies Explicitly

Optional dependencies have two import surfaces, and the guard belongs on the right one. The package's *shared* modules must not import an optional dep at all — otherwise it isn't optional (see `imports-lightweight-init`). The *integration-specific* module, which only users of that integration import, may fail at import — but with an actionable message, not a `None` placeholder that crashes with `AttributeError` far from the cause, and not a broad catch that misdiagnoses a broken install as a missing one.

**Incorrect (placeholder crashes later; broad catch misdiagnoses):**

```python
try:
    import anthropic
except ImportError:          # also catches anthropic's own broken transitive imports
    anthropic = None         # downstream code crashes with AttributeError later

class AnthropicProvider:
    def __init__(self):
        client = anthropic.Client()  # AttributeError: 'NoneType' has no 'Client'
```

**Correct (integration module guards its own import; distinguishes missing from broken):**

```python
# providers/anthropic_provider.py — imported only by users of this integration
try:
    import anthropic
except ModuleNotFoundError as e:
    if e.name != "anthropic":
        raise                        # installed but broken — surface the real failure
    raise ImportError(
        "anthropic is required for AnthropicProvider. "
        "Install with: pip install 'mylib[anthropic]'"
    ) from e

class AnthropicProvider:
    ...
```

`ModuleNotFoundError.name` identifies *which* module was missing — a transitive import failing inside an installed `anthropic` should propagate as itself, not as "please install anthropic."

**When the dependency is optional at the feature level rather than the module level:** defer the import into the function that needs it — users who never call it never pay the cost. Pair module-scope optional imports with a `TYPE_CHECKING` block (see `types-type-checking-imports`) when type hints should resolve without requiring the runtime dep.
