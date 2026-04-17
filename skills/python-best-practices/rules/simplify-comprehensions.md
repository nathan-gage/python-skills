---
title: Use Comprehensions Over for+append Loops
impact: MEDIUM-HIGH
impactDescription: more concise, often faster, and idiomatic Python
tags: simplify, comprehensions, idioms
---

## Use Comprehensions Over for+append Loops

Comprehensions express "build a collection from an iterable" in one line. Agents often write C-style loops with `append()` — more code, more variables, more places for off-by-one and wrong-list bugs. Reach for a comprehension by default.

**Incorrect (imperative loop + append):**

```python
def active_usernames(users: list[User]) -> list[str]:
    result = []
    for user in users:
        if user.is_active:
            result.append(user.name)
    return result

def name_to_id(users: list[User]) -> dict[str, str]:
    mapping = {}
    for user in users:
        mapping[user.name] = user.id
    return mapping
```

**Correct (comprehensions):**

```python
def active_usernames(users: list[User]) -> list[str]:
    return [user.name for user in users if user.is_active]

def name_to_id(users: list[User]) -> dict[str, str]:
    return {user.name: user.id for user in users}
```

**Also:**

```python
# set comprehension
unique_tags = {tag for post in posts for tag in post.tags}

# generator expression (lazy — doesn't build a list in memory)
total = sum(item.price for item in items)
```

**When NOT to use a comprehension:**

- Multi-step logic that doesn't fit on one line cleanly — readability beats brevity
- Side effects (use a plain loop; comprehensions are for building collections)
- Complex conditionals with intermediate variables

```python
# too dense to read — use a loop
result = [
    process(x, key=compute_key(x, config))
    for x in items
    if x.valid and (x.priority > threshold or x.override)
]
```

Break it up when the comprehension stops reading like English.

**`any()` and `all()` over comprehensions that just reduce to a bool:**

```python
# overkill
has_admin = [u.is_admin for u in users] != []  # wrong shape entirely
has_admin = any([u.is_admin for u in users])   # builds a list first

# right
has_admin = any(u.is_admin for u in users)     # generator, short-circuits
```
