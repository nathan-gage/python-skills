---
title: Use Modern Typing Syntax
impact: MEDIUM
impactDescription: one spelling per concept; readers and tools stop translating
tags: types, syntax, unions, generics
references: https://peps.python.org/pep-0604/, https://peps.python.org/pep-0585/, https://peps.python.org/pep-0695/, https://docs.astral.sh/ruff/rules/non-pep604-annotation-union/
---

## Use Modern Typing Syntax

On 3.11+, `Optional[X]`, `Union[X, Y]`, and `typing.List` / `Dict` / `Tuple` are legacy spellings. The modern forms — `X | None`, `X | Y`, and builtin generics `list[str]` / `dict[str, int]` — mean the same thing with fewer imports and one consistent style. Mixing both styles in one module forces readers to translate between them and invites duplicate imports.

**Incorrect (legacy spellings on a modern baseline):**

```python
from typing import Dict, List, Optional, Union

def merge_tags(
    base: List[str],
    extra: Optional[List[str]] = None,
) -> Dict[str, Union[int, str]]:
    ...
```

**Correct (builtin generics and `|` unions):**

```python
def merge_tags(
    base: list[str],
    extra: list[str] | None = None,
) -> dict[str, int | str]:
    ...
```

`ruff`'s `UP` (pyupgrade) rules rewrite these automatically — enable them so the style never regresses.

**Version notes:** builtin generics are 3.9+ (PEP 585); `|` unions are 3.10+ (PEP 604). The `type X = ...` alias statement and `class Foo[T]:` generic syntax are 3.12+ (PEP 695) — on a 3.11 baseline, keep `TypeAlias` and `TypeVar` for those two jobs. When editing a file that consistently uses the legacy style, match it or convert the whole file — don't leave a mix.
