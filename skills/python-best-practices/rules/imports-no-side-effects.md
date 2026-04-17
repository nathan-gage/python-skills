---
title: Keep Modules Cheap to Import
impact: MEDIUM
impactDescription: faster CLIs, faster tests, faster worker startup
tags: imports, side-effects, startup, performance
references: https://docs.python.org/3/reference/import.html, https://docs.python.org/3/library/importlib.html
---

## Keep Modules Cheap to Import

Importing a module should do as little as possible. Anything at module top-level — opening files, reading environment variables, building large data structures, connecting to databases, registering global handlers, hitting the network — runs every time *anything* in that module is imported. That cost compounds across CLIs (cold-start latency users feel), tests (collection time), worker pools (per-process startup), and serverless functions (cold-start time billed). Heavy import-time side effects also make modules hard to mock and hard to import in the wrong environment.

Push side effects out of module scope into **functions, factories, lazy properties, or `__init__` methods** that callers invoke explicitly.

**Incorrect (network call at import time):**

```python
# config.py
import requests

CONFIG = requests.get("https://config.example.com/v1").json()  # runs on import
DB_URL = CONFIG["db_url"]
```

Importing `config` (or anything that imports it transitively) makes a network call. Tests that don't need config still pay. Offline CI breaks. Cold starts add a request worth of latency.

**Incorrect (heavy initialization at import):**

```python
# embeddings.py
import torch
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("all-MiniLM-L6-v2")  # 90 MB download + GPU init
```

Anyone who imports `embeddings` for a type, a constant, or a single helper triggers a 90 MB download and GPU init. The `--help` of a CLI takes seconds to render.

**Incorrect (env-dependent failures at import):**

```python
import os

API_KEY = os.environ["MY_API_KEY"]   # KeyError on import if unset
```

Now you cannot import this module to read its docstring without `MY_API_KEY` set.

**Correct (lazy — pay only when the feature runs):**

```python
# config.py
from functools import cache
import requests

@cache
def get_config() -> dict[str, object]:
    return requests.get("https://config.example.com/v1").json()

def db_url() -> str:
    return get_config()["db_url"]
```

`@cache` makes the first call do the work and subsequent calls hit the cache — same effective behavior as a module constant, but only when something actually asks for it.

**Correct (lazy — model loaded on first use):**

```python
# embeddings.py
from functools import cache

@cache
def get_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> list[float]:
    return get_model().encode(text).tolist()
```

The heavy import lives inside the function (see `imports-top-of-file` for when inline imports are okay). The model loads on first `embed`, not on `import`.

**Correct (env read at use, with a clear error):**

```python
import os

def api_key() -> str:
    key = os.environ.get("MY_API_KEY")
    if not key:
        raise RuntimeError("MY_API_KEY is required to call this API")
    return key
```

Now the module imports anywhere, and the missing env variable surfaces with a useful message at the call site.

**What is fine to do at import time:**

- Pure-Python constants: `MAX_RETRIES = 5`, `_NAME_RE = re.compile(r"...")` (compile is cheap and amortizes)
- Class and function definitions
- Cheap, deterministic, in-process work (registering a dataclass, creating a small lookup dict)
- Standard-library imports

**What to push out of import time:**

- Network or disk I/O
- Subprocess launches
- Loading large models, datasets, ML weights
- Reading environment variables that may be missing
- Connecting to databases or message queues
- Registering signal handlers, atexit hooks, observability sinks
- Heavy third-party imports the module doesn't use unconditionally

**Test for it.** Run `python -c "import yourpackage"` with `--time` or in `cProfile`. If a single import takes more than ~100 ms or makes any network call, find what's running at module scope and defer it.

**Heuristic:** if the work needs to happen *exactly once* per process, write a `@cache`-decorated function and call it on demand. If it needs to happen *every* call, write a regular function. Module-scope side effects are almost never the right choice — they're "every import" by accident, not "once per process" by design.
