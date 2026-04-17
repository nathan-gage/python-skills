---
title: Scope Helpers and Constants to Their Usage Site
impact: LOW-MEDIUM
impactDescription: reduces namespace pollution and clarifies intent
tags: structure, scope, helpers
---

## Scope Helpers and Constants to Their Usage Site

When a helper function or constant is only used in one function or class, define it there — not at module level "just in case" someone else needs it later. Module-level scope is a commitment to every future reader: "this is part of the module's surface."

**Incorrect (module-level helper used only inside one function):**

```python
# somewhere in a 500-line module
def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())

def _DEFAULT_MAX_LENGTH() -> int:
    return 280

def summarize(text: str) -> str:
    text = _normalize_whitespace(text)
    return text[: _DEFAULT_MAX_LENGTH()]

# ... 400 more lines, no other use of _normalize_whitespace or _DEFAULT_MAX_LENGTH
```

`_normalize_whitespace` lives in the module namespace forever, visible to everything else in the file. A future reader sees it and wonders if it's meant to be used elsewhere. If not, why is it out here?

**Correct (scope to the function that uses it):**

```python
def summarize(text: str) -> str:
    DEFAULT_MAX_LENGTH = 280
    normalized = " ".join(text.split())
    return normalized[:DEFAULT_MAX_LENGTH]
```

Or, if the helper has enough logic to want a name:

```python
def summarize(text: str) -> str:
    def _normalize(s: str) -> str:
        return " ".join(s.split())

    return _normalize(text)[:280]
```

**When module-level is the right scope:**

- Used by multiple functions within the module
- Genuinely part of the module's API surface
- A constant that needs to be patched in tests (module-level constants are easy to monkeypatch)
- A pattern that would be expensive to rebuild per call (compiled regex, module constant, `TypeAdapter`)

**When class-level is right:**

- Used by multiple methods on the same class
- Part of the class's contract (constants referenced by name, e.g., `MyClass.DEFAULT_TIMEOUT`)

**The rule, reversed:** ask "does this helper need to be at this scope?" If a narrower scope works, use it.

**Imports follow the same principle** (see `imports-top-of-file`): default to top-of-module because imports-at-function-scope is the narrower version of the same instinct. Imports are the exception; helpers and constants are not.
