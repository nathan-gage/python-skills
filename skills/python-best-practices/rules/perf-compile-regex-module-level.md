---
title: Compile Static Regex Patterns at Module Level
impact: MEDIUM
impactDescription: avoids recompilation overhead on every call
tags: perf, regex, module-level
---

## Compile Static Regex Patterns at Module Level

`re.compile()` builds a pattern object once; `re.match()` / `re.search()` on a string call it every time. For regexes that don't change, compile at module scope. The cost of recompilation in a hot loop can dwarf the actual match.

**Incorrect (recompiled on every call):**

```python
import re

def extract_version(text: str) -> str | None:
    match = re.search(r"v(\d+\.\d+\.\d+)", text)  # compiled every call
    return match.group(1) if match else None
```

`re.search` caches recent patterns internally, but for any pattern complex enough to matter, you're paying compilation cost on every invocation.

**Correct (compiled once at import):**

```python
import re

_VERSION_RE = re.compile(r"v(\d+\.\d+\.\d+)")

def extract_version(text: str) -> str | None:
    match = _VERSION_RE.search(text)
    return match.group(1) if match else None
```

The pattern is built once when the module imports; every call just uses it.

**Naming:**

- `_UPPER_CASE` for module-level private regex constants (or whatever your project's constant convention is)
- Descriptive names — `_VERSION_RE`, `_EMAIL_RE`, not `_PATTERN1`

**When compilation isn't worth hoisting:**

- The pattern is built from a runtime value (different per call)
- The function is called a small number of times total
- The pattern is truly one-shot (startup-only parsing)

Even for the truly-one-shot case, a module-level constant is usually clearer than an inline string — so the performance argument isn't the only reason to hoist.

**Related:** same pattern applies to other "build once, use many" objects — `TypeAdapter`, `json.JSONDecoder` with custom hooks, precompiled templates. Build at module scope; use at call time.
