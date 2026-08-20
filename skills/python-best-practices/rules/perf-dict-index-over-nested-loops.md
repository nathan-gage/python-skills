---
title: Build a Dict Index Instead of Nested Loops
impact: MEDIUM
impactDescription: O(n) instead of O(n²)
tags: perf, dict, index, nested-loops
---

## Build a Dict Index Instead of Nested Loops

When code says "for each item in A, find the matching item in B," the naive pattern is nested `for` + `if x.id == y.id` — that's O(n × m). Build a dict from B once, then it's O(n + m) with each lookup O(1).

**Incorrect (nested scan — 100M comparisons for 10k × 10k):**

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

**Correct (dict index — O(n + m); duplicate policy stated):**

```python
def attach_profiles(users: list[User], profiles: list[Profile]) -> list[EnrichedUser]:
    profiles_by_user: dict[str, Profile] = {}
    for profile in profiles:
        profiles_by_user.setdefault(profile.user_id, profile)   # first match wins, like the scan
    return [
        EnrichedUser(user=user, profile=profiles_by_user.get(user.id))
        for user in users
    ]
```

For one-to-many grouping, `collections.defaultdict(list)` avoids the "check-then-create" dance: `posts_by_author[post.author_id].append(post)`. `itertools.groupby` groups already-sorted inputs without building a dict. Nested loops stay fine for small collections (under ~50 × 50), for one-off operations, or when the inner loop has rich logic that doesn't reduce to a key lookup.

An index is a drop-in replacement only when the duplicate-key policy matches: the scan finds the *first* match, while a plain `{p.user_id: p for p in profiles}` keeps the *last*. Decide and say so in the code — first wins (`setdefault`), last wins (comprehension), duplicates are an error (check while building), one-to-many (`defaultdict(list)`). The ~50 × 50 threshold is a heuristic, not a law: element cost, call frequency, key construction, and memory pressure move it in both directions.
