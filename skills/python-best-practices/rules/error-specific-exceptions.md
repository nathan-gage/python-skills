---
title: Catch Specific Exception Types
impact: HIGH
impactDescription: prevents masking unrelated bugs
tags: error, exceptions, defensive
references: https://docs.python.org/3/tutorial/errors.html#handling-exceptions, https://docs.python.org/3/library/exceptions.html#exception-hierarchy
---

## Catch Specific Exception Types

Catch the specific exception types you actually intend to handle. A broad `except Exception:` catches every regular error in your codebase, including bugs you wanted to see. (For the even worse `except:` with no type at all — which also catches `KeyboardInterrupt` and `SystemExit` — see `error-no-bare-except`.) Agents default to broad handlers because "we should be resilient"; the cost is that `KeyError` from a typo in your own code gets silently swallowed alongside the network timeout you meant to handle.

**Incorrect (bare except catches unrelated errors):**

```python
def fetch_user(user_id: str) -> User | None:
    try:
        response = http.get(f"/users/{user_id}")
        return parse_user(response.json())
    except Exception:  # catches everything — including your own bugs
        return None
```

If `parse_user` has a `KeyError` bug, this returns `None` silently. Production sees "user not found" forever; the typo is invisible.

**Correct (catch what you actually handle):**

```python
def fetch_user(user_id: str) -> User | None:
    try:
        response = http.get(f"/users/{user_id}")
    except (HTTPError, TimeoutError):
        return None
    return parse_user(response.json())  # bugs here propagate as they should
```

Now only network failures return `None`. Parsing bugs crash loudly — which is what you want during development, and what surfaces real incidents in production.

**When a broad handler is appropriate:**

- At the top of a request handler or worker loop (last line of defense)
- When you will **log and re-raise** — not swallow
- Around explicitly unsafe boundaries (untrusted user code, plugins)

```python
def handle_request(req: Request) -> Response:
    try:
        return process(req)
    except Exception as e:
        logger.exception("unhandled error in request handler")
        raise  # don't swallow — let the framework return 500
```

**Create specific exception types for domain failures:**

```python
class ToolExecutionError(Exception): ...
class ToolTimeoutError(ToolExecutionError): ...
class ToolValidationError(ToolExecutionError): ...

try:
    result = run_tool(tool, args)
except ToolTimeoutError:
    retry()
except ToolValidationError as e:
    return report_invalid(e)
```

Specific exception classes make handlers self-documenting and enable different handling per failure mode.
