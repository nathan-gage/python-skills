---
title: Consolidate try/except Blocks with the Same Handler
impact: LOW-MEDIUM
impactDescription: reduces duplication and simplifies control flow
tags: error, exceptions, duplication
---

## Consolidate `try/except` Blocks with the Same Handler

When multiple adjacent operations raise the same exception and need the same handling, merge them into one block. Separate blocks duplicate the handler — and if the handling logic ever changes, you now need to update N places.

**Incorrect (three blocks, three copies of the same handler):**

```python
def load_config(path: Path) -> Config | None:
    try:
        raw = path.read_text()
    except FileNotFoundError:
        logger.warning("config missing: %s", path)
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("config invalid json: %s", path)
        return None

    try:
        return Config(**data)
    except ValidationError:
        logger.warning("config validation failed: %s", path)
        return None
```

Three copies of "log and return None." Changing the log level, adding a metric, or switching return value means editing three places.

**Correct (one block, one handler):**

```python
def load_config(path: Path) -> Config | None:
    try:
        raw = path.read_text()
        data = json.loads(raw)
        return Config(**data)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError) as e:
        logger.warning("config load failed: %s (%s)", path, e)
        return None
```

One block, one handler, one place to change. The caller sees the same behavior; the implementation is simpler.

**Watch the scope you merge:** a single block makes every listed exception recoverable across *every* operation inside it. If a helper deep in one stage unexpectedly raises an exception type meant for a different stage, the merged handler converts a genuine defect into "config load failed." Merge only operations whose failures share one meaning and one recovery; when stages need distinct diagnostics but share the *policy*, deduplicate the handler body instead of widening the protected region — a small `_config_warning(path, stage, error)` helper called from three narrow blocks keeps stage attribution without three divergent handlers.

**When to keep blocks separate:**

- Different exceptions need **different** handling (log-and-return vs. retry vs. re-raise)
- Intermediate values matter for the handler (you want the partial result when the second step fails)
- The blocks are far apart in the function (folding them together would nest too much)
- A listed exception type could plausibly escape a *different* stage than intended (broad types like `ValueError` or `OSError`) — merging misattributes it

**Use `contextlib.suppress` for trivial "ignore the error" cases:**

```python
from contextlib import suppress

def try_cleanup(path: Path) -> None:
    with suppress(FileNotFoundError):
        path.unlink()
```

Cleaner than a full try/except for the "best effort, doesn't matter if it fails" pattern.
