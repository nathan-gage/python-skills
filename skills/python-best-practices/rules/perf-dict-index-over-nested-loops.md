---
title: Build a Dict Index Instead of Nested Loops
impact: MEDIUM
impactDescription: O(n) instead of O(n²)
tags: perf, dict, index, nested-loops
---

## Build a Dict Index Instead of Nested Loops

When code says "for each item in A, find the matching item in B," agents default to nested `for` + `if x.id == y.id`. That's O(n × m). Build a dict from B once, then it's O(n + m) total with the body of the loop becoming a single lookup.

**Incorrect (nested scan):**

```python
def attach_profiles(users: list[User], profiles: list[Profile]) -> list[EnrichedUser]:
    result = []
    for user in users:
        matching = None
        for profile in profiles:
            if profile.user_id == user.id:
                matching = profile
                break
        result.append(EnrichedUser(user=user, profile=matching))
    return result
```

If both lists have 10k entries, that's 100M comparisons in the worst case.

**Correct (dict index):**

```python
def attach_profiles(users: list[User], profiles: list[Profile]) -> list[EnrichedUser]:
    profiles_by_user = {p.user_id: p for p in profiles}
    return [
        EnrichedUser(user=user, profile=profiles_by_user.get(user.id))
        for user in users
    ]
```

Dict build is O(m). Each lookup is O(1). Total: O(n + m).

**For grouping (one-to-many):**

```python
from collections import defaultdict

posts_by_author: dict[str, list[Post]] = defaultdict(list)
for post in posts:
    posts_by_author[post.author_id].append(post)
```

`defaultdict` avoids the "check if key exists, create empty list if not" dance.

**`itertools.groupby` for consecutive grouping:**

```python
from itertools import groupby

# groupby requires sorted input on the key
events.sort(key=lambda e: e.session_id)
for session_id, session_events in groupby(events, key=lambda e: e.session_id):
    handle_session(session_id, list(session_events))
```

Useful when the input is already sorted or when order matters.

**When nested loops are fine:**

- Both collections are small (under ~50 × 50)
- The inner loop has rich logic that doesn't reduce to a key lookup
- You only do the operation once (not in a hot path)

For anything called repeatedly on non-trivial input, index first, loop second.
