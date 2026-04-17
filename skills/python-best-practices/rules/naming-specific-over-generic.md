---
title: Use Specific Parameter and Variable Names
impact: MEDIUM
impactDescription: prevents confusion when multiple instances are in scope
tags: naming, parameters, variables
---

## Use Specific Parameter and Variable Names

Generic names like `id`, `name`, `data`, `info` communicate nothing about what the value is. When you have multiple IDs or data objects in scope, they collide. Prefer names that convey the semantic role.

**Incorrect (generic names):**

```python
def transfer(id: str, id2: str, data: dict, info: dict) -> None:
    ...

def process_tools(id: str) -> None:
    config = load_config(id)
    memory = load_memory(id)  # is this the same id, or a different one?
    ...
```

Reading the call site: `transfer("u123", "t456", {...}, {...})` — which is the sender, which is the recipient, which dict is which?

**Correct (specific):**

```python
def transfer(sender_id: str, recipient_id: str, transfer_data: TransferRequest, audit_info: AuditContext) -> None:
    ...

def process_tools(toolset_id: str) -> None:
    config = load_config(toolset_id)
    memory = load_memory(toolset_id)
    ...
```

Every name describes what the value is. Call sites self-document.

**When generic is acceptable:**

- Truly generic helpers — `def first(items: list[T]) -> T`, `items` is fine
- Very short functions where the role is obvious from the body
- Following a convention (`self`, `cls`, `_` for ignored values, `i` / `j` for loop indices in math contexts)

**Generic with type annotations can be OK for one-off helpers:**

```python
def render(user: User) -> str:  # "user" is generic but context is clear
    return f"{user.first_name} {user.last_name}"
```

There's only one `User` here — no ambiguity.

**The red flag:** any time you end up with `id`, `id2`, `id3` — or `data`, `info`, `details`, `meta` all in the same scope — stop and rename. The number suffixes tell you the names aren't doing their job.

**Naming for loops:**

```python
# bad
for x in users:
    for y in x.posts:
        for z in y.comments:
            ...

# good
for user in users:
    for post in user.posts:
        for comment in post.comments:
            ...
```

Short variable names are fine when the type is obvious and the body is short. Three-letter variables in a three-level-deep loop is a readability problem.
