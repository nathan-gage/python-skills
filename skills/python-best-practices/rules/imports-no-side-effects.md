---
title: Keep Modules Cheap to Import
impact: MEDIUM
impactDescription: faster CLIs, faster tests, faster worker startup
tags: imports, side-effects, startup, performance
references: https://docs.python.org/3/reference/import.html, https://docs.python.org/3/library/importlib.html
---

## Keep Modules Cheap to Import

Anything at module top-level — opening files, reading env vars, building large data structures, connecting to databases, registering handlers, hitting the network — runs every time anything in that module is imported. That cost compounds across CLI cold-starts, test collection, worker pools, and serverless functions. It also makes modules hard to mock. Push side effects into functions, factories, or lazy properties that callers invoke explicitly.

**Incorrect (network call, heavy init, and env read at import):**

```python
# config.py
import requests

CONFIG = requests.get("https://config.example.com/v1").json()  # network at import
DB_URL = CONFIG["db_url"]

# embeddings.py
MODEL = SentenceTransformer("all-MiniLM-L6-v2")                # 90 MB download + GPU init

# keys.py
API_KEY = os.environ["MY_API_KEY"]                             # KeyError on import if unset

# settings.py — env-validating settings object built at import
class Settings:
    def __init__(self) -> None:
        self.database_url = os.environ["DATABASE_URL"]
        self.api_key = os.environ["API_KEY"]

settings = Settings()                # any import of this module now requires a full environment
```

Importing any of these for a type or constant triggers the work. A CLI's `--help` takes seconds; offline CI breaks; reading the module docstring fails without the env var set.

**Correct (lazy — pay only when the feature runs):**

```python
from functools import cache

@cache
def get_config() -> dict[str, object]:
    return requests.get("https://config.example.com/v1").json()

@cache
def get_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

def api_key() -> str:
    key = os.environ.get("MY_API_KEY")
    if not key:
        raise RuntimeError("MY_API_KEY is required to call this API")
    return key

@cache
def get_settings() -> Settings:
    return Settings()                    # constructed at first use, at the composition boundary
```

`@cache` gives you "once per process" semantics without the "every import" cost.

Fine at import time: pure-Python constants, `re.compile` for a static pattern, class and function definitions, stdlib imports, cheap registrations. Push out of import time: network/disk I/O, subprocess launches, large model loads, env-var reads that may fail, DB/queue connections, heavy third-party imports the module doesn't unconditionally use. If `uv run python -c "import yourpackage"` takes more than ~100 ms or hits the network, something at module scope should be deferred.

The settings-object variant is the most common in practice: a module-scope `Settings()` — hand-rolled or from a settings library — makes every importer (test collection, docs builds, unrelated CLIs) require a fully-populated environment, and the failure surfaces as a validation error blaming the importer rather than the missing variable. Construct settings at the composition boundary and inject them.
