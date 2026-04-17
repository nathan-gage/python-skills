---
title: Stream with Generators When Memory or First-Result Latency Matters
impact: MEDIUM
impactDescription: bounded memory and lazy evaluation for large or infinite sequences
tags: perf, generators, memory, streaming
references: https://docs.python.org/3/glossary.html#term-generator, https://docs.python.org/3/library/itertools.html
---

## Stream with Generators When Memory or First-Result Latency Matters

Generators trade materialization for laziness: they yield one value at a time, hold no intermediate list, and let the caller stop early. This is a **memory and streaming** rule, not a "generators are categorically better than lists" rule. When you need every result anyway, iterate the sequence more than once, want random access, or want to sort it — a list comprehension is the right tool, often clearer and sometimes faster (no `next()` overhead per element).

**Reach for a generator when:**

- The input is large enough that holding it twice in memory is a problem
- The input is unbounded (infinite stream, line-by-line file read)
- The consumer can stop early (`any()`, `next()`, `break`)
- The pipeline has multiple stages that would otherwise materialize between each

**Reach for a list (or list comprehension) when:**

- You need `len()` before iterating
- You iterate the same sequence more than once
- You need random access (`items[5]`)
- You'll sort the whole sequence anyway (sort materializes)
- The data is small and a list comprehension reads more clearly

**Incorrect (materializes a multi-GB file for a count — OOMs at scale):**

```python
def count_errors(path: Path) -> int:
    lines = path.read_text().splitlines()                    # full file in memory
    parsed = [parse_line(line) for line in lines]            # second full copy
    matching = [p for p in parsed if p.level == "ERROR"]     # third full copy
    return len(matching)
```

For a 10GB log file, this OOMs. Three copies of the same data are alive at once.

**Correct (streaming — constant memory regardless of file size):**

```python
def count_errors(path: Path) -> int:
    with path.open() as f:
        return sum(1 for line in f if parse_line(line).level == "ERROR")
```

One line at a time. Constant memory.

**Generator expressions for pipelines:**

```python
with path.open() as f:
    parsed = (parse_line(line) for line in f)
    errors = (p for p in parsed if p.level == "ERROR")
    count = sum(1 for _ in errors)
```

Each stage yields one value at a time; nothing is held in memory.

**Lists are the right call when you'll re-iterate:**

```python
# Generator would be wrong here — `users` is iterated twice.
users = [u for u in load_users() if u.active]
print(f"{len(users)} active users")
for user in users:
    notify(user)
```

A generator would exhaust on the first iteration and the second loop would run zero times — a real bug, not a performance issue.

**Lists are also fine when the data is small:**

```python
# 50 config entries, used once. A generator buys nothing here.
ports = [c.port for c in configs if c.enabled]
```

Don't replace small list comprehensions with generators on stylistic grounds.

**`itertools` for streaming pipelines:**

`chain`, `islice`, `takewhile`, `dropwhile`, `tee`, `groupby` — all yield lazily. Reach for them when a pipeline is naturally streaming; skip them when the data already fits in memory and a comprehension is clearer.

**Heuristic:** ask "what's the worst-case size of this sequence, and does the consumer touch each element exactly once?" If the answer is "large" and "yes," use a generator. Otherwise, write whichever reads more clearly — usually a list comprehension.
