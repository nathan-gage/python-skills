---
title: Place Imports at the Top of the File
impact: LOW-MEDIUM
impactDescription: makes dependencies visible at a glance
tags: imports, structure, conventions
references: https://peps.python.org/pep-0008/#imports
---

## Place Imports at the Top of the File

Imports belong at the top of the module, in conventional ordering (stdlib, third-party, local). Inline imports inside functions hide dependencies from readers, complicate static analysis, and surprise anyone debugging a `ModuleNotFoundError` raised in the middle of a call.

**Incorrect (imports scattered through the function bodies):**

```python
def fetch_user(user_id: str) -> User:
    import requests  # hidden dependency
    response = requests.get(f"/users/{user_id}")
    return User(**response.json())

def process():
    from .helpers import validate  # easily missed
    ...
    import json  # another one
    data = json.dumps(result)
```

Readers can't see the module's dependency graph without scanning every function. Tools that analyze imports (linters, bundle checkers) get confused. If a deferred import fails, the error surfaces far from the file's top.

**Correct (all imports at the top, grouped and ordered):**

```python
import json
from typing import Any

import requests

from .helpers import validate


def fetch_user(user_id: str) -> User:
    response = requests.get(f"/users/{user_id}")
    return User(**response.json())

def process():
    ...
```

The conventional order (PEP 8):

1. Standard library imports
2. Related third-party imports
3. Local application/library-specific imports

Blank lines separate the groups. `ruff` / `isort` automate this — run them.

**When inline imports are legitimate:**

**1. Breaking circular imports.** When two modules legitimately need each other and can't be merged, inline one import inside the function that uses it:

```python
def handle_event(event: Event) -> None:
    from .other_module import process  # breaks an import cycle
    process(event)
```

Add a comment explaining why — future readers might otherwise "fix" it.

**2. Optional dependencies with runtime gating.** When a feature requires a heavy or optional package that shouldn't be loaded unless the feature is used:

```python
def render_plot(data: list[float]) -> bytes:
    import matplotlib.pyplot as plt  # only imported when plotting is requested
    ...
```

This is the narrow exception — think twice before using it. See `imports-optional-dependencies` for a cleaner pattern with typed stubs.

**3. Avoiding module-level side effects.** Rare — if an import triggers side effects you specifically want to defer.

Outside these cases, top-of-file is the rule.
