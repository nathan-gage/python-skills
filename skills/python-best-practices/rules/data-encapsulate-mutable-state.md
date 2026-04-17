---
title: Encapsulate Mutable State in the Narrowest Clear Scope
impact: HIGH
impactDescription: limits the blast radius of state mutations
tags: data, state, encapsulation, scope
references: https://docs.python.org/3/reference/executionmodel.html#naming-and-binding
---

## Encapsulate Mutable State in the Narrowest Clear Scope

If mutable state must exist, give it the narrowest scope where the code that needs it is still **clear**. The principle is "narrowest *clear* scope," not "always closures over instance attributes." A closure can be the right answer when the state is small, the interface is one or two callables, and there's nothing else to inspect or test. An instance attribute is the right answer when the state belongs to a domain object with identity, when multiple methods need to share it, or when you want it to be easy to inspect, type, serialize, or mock in tests.

**Pick the smallest scope where the surrounding code still reads naturally:**

| Scope | Use when |
|-------|----------|
| Local variable | State lives entirely inside one function call |
| Closure | A small handle of 1–2 callables; state must outlive a single call but doesn't need identity |
| Private instance attribute (`_name`) | State belongs to a domain object; multiple methods read/write it; you want introspection, typing, and serialization |
| Module-level global | Genuinely process-wide state — caches, registries (rare; prefer dependency injection) |

Module-level globals deserve the most pushback. Closures and instance attributes are both legitimate; the choice depends on whether the state has identity worth naming.

**Incorrect (state visible to every method on the class — too wide):**

```python
from typing import Callable

class DebouncedWriter:
    def __init__(self, callback: Callable[[], None], delay_ms: int = 300):
        self._callback = callback
        self._delay_ms = delay_ms
        self._timeout_handle: TimerHandle | None = None  # touched by every method

    def queue_send(self, text: str) -> None: ...
    def flush_now(self) -> None: ...
    def something_else(self) -> None: ...  # nothing prevents a bug here
```

If only `queue_send` and `flush_now` need `_timeout_handle`, every other method is a potential source of a state bug.

**Correct option A (closure — state trapped behind a small handle):**

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class DebouncedAction:
    trigger: Callable[[], None]
    clear: Callable[[], None]

def create_debounced_action(callback: Callable[[], None], delay_ms: int = 300) -> DebouncedAction:
    timeout: TimerHandle | None = None

    def trigger() -> None:
        nonlocal timeout
        if timeout is not None:
            timeout.cancel()
        timeout = schedule_after(delay_ms, _fire)

    def _fire() -> None:
        nonlocal timeout
        timeout = None
        callback()

    def clear() -> None:
        nonlocal timeout
        if timeout is not None:
            timeout.cancel()
            timeout = None

    return DebouncedAction(trigger=trigger, clear=clear)
```

Good fit when the only surface is `trigger` and `clear`, and nothing else needs to inspect `timeout`.

**Correct option B (small focused class — when identity, inspection, or tests matter):**

```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class DebouncedAction:
    callback: Callable[[], None]
    delay_ms: int = 300
    _timeout: TimerHandle | None = field(default=None, init=False, repr=False)

    def trigger(self) -> None:
        if self._timeout is not None:
            self._timeout.cancel()
        self._timeout = schedule_after(self.delay_ms, self._fire)

    def _fire(self) -> None:
        self._timeout = None
        self.callback()

    def clear(self) -> None:
        if self._timeout is not None:
            self._timeout.cancel()
            self._timeout = None
```

Good fit when:

- Tests want to assert on `_timeout` being `None`
- A debugger should be able to print the object meaningfully
- Subclassing or replacing `_fire` matters
- The object will be serialized, logged, or compared

Both versions are *narrower* than the original — neither lets unrelated methods touch the timer. The closure isn't categorically better; it's the right call when the surface is tiny and identity is irrelevant.

**Heuristics for picking:**

- One or two callables in the public interface, no introspection needed → closure
- Several methods sharing state, identity matters, tests want to peek → focused class with `_private` attributes
- State spans modules → reconsider the design before reaching for a module global

**The wrong answer is a wide-open class.** Mutable state on a class that lets every method touch it is how invariants rot — regardless of whether the alternative is a closure or a smaller class.
