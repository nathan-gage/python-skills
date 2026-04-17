---
title: Use UPPER_CASE for Module Constants
impact: LOW-MEDIUM
impactDescription: signals immutability and public/private scope
tags: naming, constants, conventions
---

## Use `UPPER_CASE` for Module Constants

Module-level values that don't change during execution are constants. The `UPPER_CASE` convention signals "don't reassign this" and is widely recognized across Python codebases. Agents often leave constants as regular `lower_case` — the convention is cheap and the signal is strong.

**Incorrect (looks like a reassignable variable):**

```python
# mymodule.py
default_timeout = 30
max_retries = 3
allowed_hosts = frozenset({"localhost", "127.0.0.1"})

def fetch(url: str) -> Response:
    for attempt in range(max_retries):
        try:
            return http.get(url, timeout=default_timeout)
        except TimeoutError:
            continue
```

A reader sees `default_timeout` and can't tell at a glance whether it's a constant or a mutable module-level config someone might reassign.

**Correct (UPPER_CASE signals constant):**

```python
# mymodule.py
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1"})

def fetch(url: str) -> Response:
    for attempt in range(MAX_RETRIES):
        try:
            return http.get(url, timeout=DEFAULT_TIMEOUT)
        except TimeoutError:
            continue
```

**Private / internal constants start with `_`:**

```python
_DEFAULT_CACHE_SIZE = 512
_INTERNAL_HEADER = "x-mymodule-trace"
```

The underscore keeps them out of `from module import *` and signals they're not part of the public API.

**When a value isn't really a constant:**

- It's computed from other values at import time (a derived dict built from `os.environ`, etc.)
- It's mutable and intentionally reassignable (feature flags, test hooks)

For those, keep them `lower_case`. The convention is for *intentional constants* — values you commit to never reassigning.

**Enum members:** also UPPER_CASE by convention:

```python
from enum import Enum

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
```

**Class constants:** UPPER_CASE on the class body, same rule:

```python
class Cache:
    DEFAULT_SIZE = 1024
    _EVICTION_RATIO = 0.1
```

**`typing.Final` to enforce it:**

```python
from typing import Final

DEFAULT_TIMEOUT: Final[int] = 30  # checker flags any reassignment
```

Pair the convention with `Final` when you want the checker to enforce it.
