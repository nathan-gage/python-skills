---
title: Keep Package __init__ Imports Light
impact: LOW-MEDIUM
impactDescription: importing one symbol shouldn't load the whole package tree
tags: imports, packages, init, lazy
references: https://docs.python.org/3/reference/import.html#regular-packages, https://peps.python.org/pep-0562/
---

## Keep Package `__init__` Imports Light

Importing any submodule executes every parent package's `__init__.py` first. An `__init__.py` that eagerly imports all its submodules turns `from pkg.core import parse` into "load the entire package" — including integrations that pull heavy or optional dependencies. The symptom is an `ImportError` for a dependency the importing code never mentions, or a cold start that pays for subsystems it doesn't use.

**Incorrect (barrel drags an optional dep into every import):**

```python
# pkg/__init__.py
from .core import parse, render
from .exporters.excel import ExcelExporter    # imports openpyxl
from .exporters.charts import ChartExporter   # imports matplotlib

# elsewhere — a consumer that only wants parse():
from pkg.core import parse   # ImportError: No module named 'openpyxl'
```

**Correct (cheap re-exports stay; heavy ones become lazy via PEP 562):**

```python
# pkg/__init__.py
from .core import parse, render

def __getattr__(name: str):
    if name == "ExcelExporter":
        from .exporters.excel import ExcelExporter
        return ExcelExporter
    if name == "ChartExporter":
        from .exporters.charts import ChartExporter
        return ChartExporter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

`pkg.ExcelExporter` still works for users who want it — but only they pay for `openpyxl`.

A deferred import inside the factory function that needs it achieves the same without `__getattr__`: a dispatch function that imports its integration in the matching branch keeps the optional dependency out of the import graph until that branch runs (one of the documented exceptions in `imports-top-of-file`). Type checkers resolve lazy attributes via a `TYPE_CHECKING` import block or a `.pyi` stub.

**Scope:** Re-exporting the public API from `__init__.py` is a fine, mainstream pattern; the failure mode is *heavy or optional* imports riding along with it. Related: `imports-no-side-effects` covers work at import time; this rule covers import *fan-out* — both decide what `import pkg` costs.
