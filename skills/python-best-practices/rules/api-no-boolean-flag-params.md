---
title: Avoid Boolean Flag Parameters in Public APIs
impact: HIGH
impactDescription: prevents call sites that read like "do_thing(thing, True, False)"
tags: api, parameters, booleans, literal, enum
references: https://docs.python.org/3/library/typing.html#typing.Literal, https://docs.python.org/3/library/enum.html
---

## Avoid Boolean Flag Parameters in Public APIs

A boolean parameter is a binary mode switch hiding behind a generic type. The call site `download(url, True, False, True)` is unreadable, the function body branches on the flag with two near-duplicate code paths, and adding a third mode later requires breaking the API. This is the function-level cousin of `data-explicit-variants`: when behavior meaningfully changes on a flag, prefer split functions or a `Literal`/`Enum` parameter.

**Incorrect (boolean flags — call sites lose meaning):**

```python
def export_report(rows: list[Row], to_csv: bool = True, compress: bool = False) -> bytes:
    if to_csv:
        data = render_csv(rows)
    else:
        data = render_json(rows)
    if compress:
        data = gzip.compress(data)
    return data

export_report(rows, True, False)   # what does True/False mean here?
export_report(rows, False, True)   # JSON, compressed? CSV, compressed? Reader can't tell.
```

The function body is two if-branches stacked, the call sites carry no information, and any third format (Parquet, XML) means another bool — `to_csv: bool, to_json: bool, to_parquet: bool` is incoherent.

**Correct option A (split into separate functions when bodies barely overlap):**

```python
def export_csv(rows: list[Row]) -> bytes: ...
def export_json(rows: list[Row]) -> bytes: ...

def with_compression(data: bytes) -> bytes:
    return gzip.compress(data)

# call site
data = with_compression(export_csv(rows))
```

Each function does one thing. Adding `export_parquet` is additive, not breaking. Compression composes orthogonally.

**Correct option B (`Literal` parameter when the modes share most of the body):**

```python
from typing import Literal

Format = Literal["csv", "json", "parquet"]

def export_report(rows: list[Row], format: Format, *, compress: bool = False) -> bytes:
    match format:
        case "csv":     data = render_csv(rows)
        case "json":    data = render_json(rows)
        case "parquet": data = render_parquet(rows)
    return gzip.compress(data) if compress else data

export_report(rows, format="csv", compress=True)
```

Adding a fourth format is a one-line change to the `Literal`; the call sites read meaningfully (`format="parquet"` instead of `True, False, True`).

**Correct option C (`Enum` when the modes carry behavior or constants):**

```python
from enum import Enum

class CompressionLevel(Enum):
    NONE = 0
    FAST = 1
    BEST = 9

def export_report(rows: list[Row], *, level: CompressionLevel = CompressionLevel.NONE) -> bytes:
    data = render_csv(rows)
    if level is CompressionLevel.NONE:
        return data
    return gzip.compress(data, compresslevel=level.value)
```

The enum gives each variant a name *and* a meaningful value. Type checkers narrow on `is` comparisons.

**`bool` parameters that are genuinely binary toggles are still okay** — but only when:

- The flag is keyword-only (use `*` per `api-keyword-only-params`)
- The name clearly answers "what does True mean?" (`include_archived=True`, `strict=True`, `dry_run=True`)
- There's no plausible third mode coming
- The body doesn't fork into two near-duplicate paths

```python
def list_users(*, include_archived: bool = False) -> list[User]:
    if include_archived:
        return query_all_users()
    return query_active_users()
```

`include_archived=True` reads at the call site. The body is genuinely a small branch on a single SQL filter.

**Heuristic:** read your call sites out loud. `export_report(rows, True, False)` fails the test. `export_report(rows, format="csv", compress=True)` passes. If you hear positional booleans, the API needs splitting or a `Literal`.
