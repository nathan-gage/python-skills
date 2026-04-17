---
title: Remove Unused Imports
impact: LOW-MEDIUM
impactDescription: prevents accidental dependencies and reduces noise
tags: imports, dead-code, cleanup
---

## Remove Unused Imports

Every import is a declaration of "this module depends on X." Unused imports lie about dependencies, add reading noise, risk circular imports, and can mask refactoring errors (the import survives long after the only call site was deleted).

**Incorrect (imports for names that aren't used):**

```python
import json
import re
from typing import Any, Optional, Union

from .helpers import validate, format_date  # format_date never used

def compact(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"))
```

`re`, `Optional`, `Union`, `format_date` aren't used. Readers wonder if they're intentional. Linters flag them (eventually). `validate` is also unused here.

**Correct (just what's needed):**

```python
import json
from typing import Any


def compact(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"))
```

**Automate detection:**

`ruff check --select F401` flags unused imports. Add it to pre-commit or CI — manual review misses too many.

**The re-export exception:**

When a module intentionally re-exports names from elsewhere (common in `__init__.py`), declare the re-exports explicitly:

```python
# __init__.py
from .client import Client as Client        # explicit re-export — "as" form is F401-safe
from .errors import ClientError as ClientError
```

Or list them in `__all__`:

```python
# __init__.py
from .client import Client
from .errors import ClientError

__all__ = ["Client", "ClientError"]
```

Either form signals "this import is intentional, not forgotten."

**Type-only imports:**

If an import is used only in annotations, move it under `if TYPE_CHECKING:` (see `types-type-checking-imports`). That removes the runtime cost and keeps the checker happy.

**When you might keep an unused import:**

- Forces registration as a side effect (`import my_plugin_module` that self-registers). Document this clearly — `# noqa: F401 — registers handlers at import time`
- Part of a stable public API in `__init__.py` re-exports

Outside those cases: delete.
