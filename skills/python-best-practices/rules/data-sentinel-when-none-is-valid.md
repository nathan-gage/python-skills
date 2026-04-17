---
title: Use a Sentinel Object When None Is a Real Domain Value
impact: MEDIUM-HIGH
impactDescription: distinguishes "no value passed" from "None passed deliberately"
tags: data, sentinel, none, optional, defaults
references: https://peps.python.org/pep-0661/, https://docs.python.org/3/library/typing.html#typing.Optional
---

## Use a Sentinel Object When `None` Is a Real Domain Value

When `None` carries semantic meaning in your domain — "the user explicitly cleared this field," "no parent," "no assignee" — you can no longer use `None` as a "not provided" default. Reach for a private sentinel object instead. This complements `types-remove-redundant-optional`: that rule says drop `| None` when `None` is impossible; this rule says use a sentinel when `None` is meaningfully different from "not passed."

PEP 661 documents the pattern (it didn't standardize a syntax, but the idiom is universal). The sentinel is a unique object you compare with `is`, never with `==`.

**Incorrect (using `None` as both "absent" and "explicitly cleared"):**

```python
def update_user(user_id: str, nickname: str | None = None) -> User:
    user = db.get(user_id)
    user.nickname = nickname        # was the caller clearing the nickname,
    db.save(user)                   # or did they just not pass it?
    return user

update_user("u1")                   # didn't touch nickname? cleared it?
update_user("u1", nickname=None)    # same call — same ambiguity
update_user("u1", nickname="bob")   # this one is clear
```

There is no way for the function to tell "the caller didn't mention nickname" from "the caller wants to clear it." That ambiguity has bitten every PATCH-style API ever written.

**Correct (sentinel default + `None` meaning "clear"):**

```python
from typing import Final

class _Unset:
    def __repr__(self) -> str:
        return "<unset>"

UNSET: Final = _Unset()

def update_user(
    user_id: str,
    nickname: str | None | _Unset = UNSET,
) -> User:
    user = db.get(user_id)
    if nickname is not UNSET:
        user.nickname = nickname     # may be None (cleared) or a real string
    db.save(user)
    return user

update_user("u1")                    # nickname untouched
update_user("u1", nickname=None)     # nickname cleared
update_user("u1", nickname="bob")    # nickname set to "bob"
```

Compare with `is`, not `==`, so callers can't accidentally pass an object that compares equal.

**For Pydantic models — same pattern, same payoff.** Distinguishing "field omitted from PATCH payload" vs. "field set to null" is the canonical use case:

```python
from typing import Any
from pydantic import BaseModel, Field

class _Unset:
    def __repr__(self) -> str:
        return "<unset>"

UNSET: Any = _Unset()  # Any so it satisfies any field annotation

class UserPatch(BaseModel):
    nickname: str | None = Field(default=UNSET)
    email: str = Field(default=UNSET)

    def changes(self) -> dict[str, object]:
        return {k: v for k, v in self.model_dump().items() if v is not UNSET}
```

Now `UserPatch(nickname=None).changes() == {"nickname": None}` (clear) and `UserPatch().changes() == {}` (untouched).

**`typing` exposes `Sentinel` (3.13+, PEP 661 follow-up).** When available, you can shorten the boilerplate:

```python
# Python 3.13+ (proposed; check your interpreter)
from typing import Sentinel

UNSET = Sentinel("UNSET")
```

Until that lands universally, the small `_Unset` class above is the portable form.

**Don't use generic objects as sentinels.** `_UNSET = object()` works, but it gives no help to readers, type checkers, or debuggers. A small named class with a `__repr__` makes tracebacks readable.

**Don't reach for sentinels when `None` is fine.** If `None` already means "absent" and there's no separate "explicitly cleared" state to distinguish, plain `nickname: str | None = None` is the right answer. The sentinel earns its complexity only when both meanings need to coexist.

**Heuristic:** if your function or model needs to distinguish three states — "not provided," "provided as None," "provided as a real value" — you need a sentinel. Two states (`None` vs. value) is just `Optional`.
