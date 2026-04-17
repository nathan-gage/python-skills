---
title: Return Early to Flatten Control Flow
impact: MEDIUM
impactDescription: keeps the happy path unnested and readable
tags: simplify, control-flow, guard-clauses
---

## Return Early to Flatten Control Flow

When a function has preconditions to check, return as soon as one fails. Agents tend to write deeply nested "if valid, if authorized, if ..." pyramids — the happy path ends up buried five levels in. Guard clauses flatten the structure and make the happy path the most visible branch.

**Incorrect (pyramid of nesting):**

```python
def process_request(req: Request) -> Response:
    if req.authenticated:
        if req.authorized:
            if req.body is not None:
                if req.body.is_valid:
                    return do_process(req.body)
                else:
                    return error(400, "invalid body")
            else:
                return error(400, "missing body")
        else:
            return error(403, "forbidden")
    else:
        return error(401, "unauthenticated")
```

The actual work — `do_process(req.body)` — is the innermost line. Every error case has to be read to get there.

**Correct (guard clauses, happy path at the end):**

```python
def process_request(req: Request) -> Response:
    if not req.authenticated:
        return error(401, "unauthenticated")
    if not req.authorized:
        return error(403, "forbidden")
    if req.body is None:
        return error(400, "missing body")
    if not req.body.is_valid:
        return error(400, "invalid body")

    return do_process(req.body)
```

Each precondition is handled and dismissed. The happy path is unindented, at the bottom, easy to find.

**Works the same for loops:**

```python
# pyramid
for item in items:
    if item.active:
        if item.ready:
            process(item)

# flattened
for item in items:
    if not item.active:
        continue
    if not item.ready:
        continue
    process(item)
```

**When to keep the `else`:**

- The two branches do comparable work (not "error vs. success")
- The function is short enough that nesting doesn't obscure the structure

```python
# fine — short, parallel branches
def classify(n: int) -> str:
    if n > 0:
        return "positive"
    elif n < 0:
        return "negative"
    else:
        return "zero"
```

**Rule of thumb:** if you're checking "is this valid?" and returning an error on the no-branch, guard-clause it. If you're splitting between two equal outcomes, `if/else` is fine.
