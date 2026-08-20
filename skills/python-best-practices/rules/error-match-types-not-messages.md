---
title: Classify Errors by Type, Not Message Text
impact: MEDIUM
impactDescription: wording is not a contract; types and codes are
tags: error, exceptions, retries, classification
references: https://docs.python.org/3/library/exceptions.html#exception-hierarchy
---

## Classify Errors by Type, Not Message Text

Branching on exception message substrings turns prose into a control-flow API. Messages change between library versions, vary by locale, and collide with legitimate content — an error that merely *mentions* "timeout" gets retried as if it were one. Exception types, status codes, and structured attributes are the contract; match on those.

**Incorrect (substring sniffing):**

```python
TRANSIENT_MARKERS = ("timeout", "connection reset", "temporarily unavailable")

def is_retryable(e: Exception) -> bool:
    return any(marker in str(e).lower() for marker in TRANSIENT_MARKERS)
    # "invalid config: timeout must be positive" → retried forever
```

**Correct (types and status codes):**

```python
RETRYABLE_STATUS = frozenset({429, 502, 503, 504})

def is_retryable(e: Exception) -> bool:
    if isinstance(e, (TimeoutError, ConnectionError)):
        return True
    if isinstance(e, HTTPStatusError):
        return e.response.status_code in RETRYABLE_STATUS
    return False
```

The classifier now survives library upgrades and can't false-positive on message content.

**When a library gives you nothing but a message:** isolate the string match in one named function with a comment linking the upstream issue asking for typed errors — one quarantined hack beats substring checks scattered through handlers. Related: `error-specific-exceptions` is the same principle at the `except` clause; this rule covers classification logic that receives an already-caught exception.
