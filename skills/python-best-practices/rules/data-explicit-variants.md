---
title: Create Explicit Variants Instead of Mode Flags
impact: CRITICAL
impactDescription: eliminates conditional-logic sprawl
tags: data, api, architecture, variants
---

## Create Explicit Variants Instead of Mode Flags

When a class starts growing `is_thread`, `is_editing`, `is_forwarding` flags — or a mode parameter like `mode: Literal["thread", "edit", "forward"]` — stop. Each flag doubles the possible states; each mode check adds conditional logic at every call site. Split into explicit subclasses or sibling classes instead.

**Incorrect (one class, many modes, exponential conditionals):**

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class MessageComposer:
    on_submit: Callable[[str], None]
    mode: Literal["channel", "thread", "dm_thread", "edit", "forward"]
    channel_id: str | None = None
    dm_id: str | None = None
    message_id: str | None = None

    def render(self) -> Frame:
        if self.mode == "dm_thread":
            extra = AlsoSendToDMField(self.dm_id)
        elif self.mode == "thread":
            extra = AlsoSendToChannelField(self.channel_id)
        else:
            extra = None
        if self.mode == "edit":
            actions = EditActions()
        elif self.mode == "forward":
            actions = ForwardActions()
        else:
            actions = DefaultActions()
        return Frame(extra, actions)
```

What does this class actually render? Answer: it depends on which of five enum values and three optional IDs are set. The call sites look like `MessageComposer(mode="thread", channel_id=x)` — which is valid? Readers have to look at the implementation to know.

**Correct (explicit variants, each self-contained):**

```python
from dataclasses import dataclass

@dataclass
class ChannelComposer:
    channel_id: str
    on_submit: Callable[[str], None]

    def render(self) -> Frame:
        return Frame(extra=None, actions=DefaultActions())

@dataclass
class ThreadComposer:
    channel_id: str
    on_submit: Callable[[str], None]

    def render(self) -> Frame:
        return Frame(
            extra=AlsoSendToChannelField(self.channel_id),
            actions=DefaultActions(),
        )

@dataclass
class EditMessageComposer:
    message_id: str
    on_submit: Callable[[str], None]

    def render(self) -> Frame:
        return Frame(extra=None, actions=EditActions())
```

Each class declares exactly the fields its variant needs. Impossible combinations are unrepresentable. Call sites read `ChannelComposer(channel_id=x)` — immediately obvious.

**Shared structure:** when variants genuinely share logic, extract helpers or a base class that holds only the common interface — not a mega-class that mode-switches internally.
