---
title: Flatten Nested if Statements Into and Conditions
impact: LOW-MEDIUM
impactDescription: reduces indentation and improves readability
tags: simplify, control-flow, conditionals
---

## Flatten Nested `if` Statements Into `and` Conditions

When nested `if` statements share the same body and have no intervening code, collapse them into a single `if` with `and`. The nested form implies the branches do something different; when they don't, the structure lies.

**Incorrect (nested if with no intervening code):**

```python
def should_notify(user: User, event: Event) -> bool:
    if user.is_active:
        if user.notifications_enabled:
            if event.priority >= user.notification_threshold:
                return True
    return False
```

Four indentation levels, three conditions, and nothing happening between them.

**Correct (combined into one condition):**

```python
def should_notify(user: User, event: Event) -> bool:
    return (
        user.is_active
        and user.notifications_enabled
        and event.priority >= user.notification_threshold
    )
```

One expression. The reader sees all conditions together.

**When nesting IS the right structure:**

- Each branch does genuinely different work
- Intermediate logging, validation, or early returns happen between checks
- The checks share a branch in only some cases

```python
# keep this nested — the branches do different things
if user.is_active:
    log_seen(user)
    if user.notifications_enabled:
        send_notification(user, event)
    else:
        queue_digest(user, event)
```

Not every chain of checks flattens. The rule is: *if every nested branch only holds another `if` until the final body, flatten*.

**Early-return flattening:**

```python
# also nested
def handle(request):
    if request.authenticated:
        if request.authorized:
            return process(request)

# flattened with guards
def handle(request):
    if not request.authenticated:
        return None
    if not request.authorized:
        return None
    return process(request)
```

Either form is fine; guard-clause style often reads cleaner when the happy path is the "bottom" of the function.
