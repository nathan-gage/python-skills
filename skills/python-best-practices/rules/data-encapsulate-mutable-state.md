---
title: Encapsulate Mutable State in the Smallest Possible Scope
impact: HIGH
impactDescription: limits the blast radius of state mutations
tags: data, state, encapsulation, closures
---

## Encapsulate Mutable State in the Smallest Possible Scope

If mutable state must exist, trap it where only the code that needs it can see it. A closure is better than an instance attribute; an instance attribute is better than a module-level global. Agents default to the loosest scope — push back.

**Incorrect (state visible to every method on the class):**

```python
from typing import Callable

class DebouncedWriter:
    def __init__(self, callback: Callable[[], None], delay_ms: int = 300):
        self._callback = callback
        self._delay_ms = delay_ms
        self._timeout_handle: TimerHandle | None = None  # visible to all methods

    def queue_send(self, text: str) -> None:
        # can touch _timeout_handle
        ...

    def flush_now(self) -> None:
        # can touch _timeout_handle
        ...

    def something_else(self) -> None:
        # can also touch _timeout_handle — and nothing prevents a bug here
        ...
```

Any method — including new ones added later — can read or mutate `_timeout_handle`. That's how invariants rot.

**Correct (state trapped in a closure):**

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class DebouncedAction:
    trigger: Callable[[], None]
    clear: Callable[[], None]

def create_debounced_action(callback: Callable[[], None], delay_ms: int = 300) -> DebouncedAction:
    timeout: TimerHandle | None = None

    def trigger() -> None:
        nonlocal timeout
        if timeout is not None:
            timeout.cancel()
        timeout = schedule_after(delay_ms, lambda: _fire(callback))

    def _fire(cb: Callable[[], None]) -> None:
        nonlocal timeout
        timeout = None
        cb()

    def clear() -> None:
        nonlocal timeout
        if timeout is not None:
            timeout.cancel()
            timeout = None

    return DebouncedAction(trigger=trigger, clear=clear)
```

Nothing outside the closure can reach `timeout`. The interface is two functions; the state is invisible.

**When a class is the right tool:** when state belongs to a domain object with identity (a `User`, a `Session`), or when you need multiple methods to share state as a coherent unit. Then the state belongs on the instance — but still as `_private` attributes, not public ones.
