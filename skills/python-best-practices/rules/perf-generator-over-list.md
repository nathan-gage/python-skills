---
title: Use Generators for Streaming Iteration
impact: MEDIUM
impactDescription: constant memory instead of O(n)
tags: perf, generators, memory
---

## Use Generators for Streaming Iteration

When you're iterating through values and only need them one at a time, a generator uses constant memory. Materializing to a list holds every intermediate value in memory — fine for 100 items, a problem for 100 million.

**Incorrect (materializes a full list just to iterate):**

```python
def process_log_lines(path: Path) -> int:
    lines = path.read_text().splitlines()        # loads entire file
    parsed = [parse_line(line) for line in lines]  # and a second full list
    matching = [p for p in parsed if p.level == "ERROR"]  # and a third
    return len(matching)
```

Three full copies of the data in memory at once. For a 10GB log file, this OOMs.

**Correct (streaming):**

```python
def process_log_lines(path: Path) -> int:
    with path.open() as f:
        count = 0
        for line in f:                          # iterator over lines
            parsed = parse_line(line)
            if parsed.level == "ERROR":
                count += 1
        return count
```

One line at a time. Constant memory regardless of file size.

**Generator expressions for pipelines:**

```python
with path.open() as f:
    parsed = (parse_line(line) for line in f)           # generator
    errors = (p for p in parsed if p.level == "ERROR")  # generator
    count = sum(1 for _ in errors)                       # reduces without materializing
```

Each stage yields one value at a time; nothing is held in memory.

**When to materialize:**

- You need `len()` before iterating (generators don't have a length)
- You iterate the same sequence multiple times (generators exhaust)
- You need random access (`items[5]`) — generators are sequential only
- You need to sort the whole sequence (sort requires materialization anyway)

**`yield` in functions for custom generators:**

```python
def read_chunks(path: Path, size: int = 8192) -> Iterator[bytes]:
    with path.open("rb") as f:
        while chunk := f.read(size):
            yield chunk
```

`yield` builds a generator function — the caller iterates lazily.

**`itertools` is your friend:**

`chain`, `islice`, `takewhile`, `dropwhile`, `tee`, `groupby` — all streaming. Use them instead of slicing/filtering materialized lists.
