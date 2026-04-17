# Python Best Practices

**Version 1.0.0**
Python Best Practices
April 2026

> **Note:**
> This document is optimized for AI agents and LLMs that maintain, generate,
> or refactor Python codebases. Humans may also find it useful, but the
> guidance, examples, and framing prioritize consistency and pattern-matching
> for AI-assisted workflows.

---

## Abstract

Comprehensive Python software engineering guidelines designed for AI agents. Contains 50+ rules across 8 categories, prioritized by impact from critical (data modeling, type safety) to low (import hygiene). Each rule names the failure mode agents tend toward, shows incorrect and correct code, and explains the payoff. Rules are derived from real PR review patterns and production experience.

---

## Table of Contents

1. [Data Modeling](#1-data-modeling) — **CRITICAL**
   - 1.1 [Brand Primitive IDs With NewType](#11-brand-primitive-ids-with-newtype)
   - 1.2 [Create Explicit Variants Instead of Mode Flags](#12-create-explicit-variants-instead-of-mode-flags)
   - 1.3 [Delete Dead Variants](#13-delete-dead-variants)
   - 1.4 [Derive, Don't Store](#14-derive-dont-store)
   - 1.5 [Encapsulate Mutable State in the Smallest Possible Scope](#15-encapsulate-mutable-state-in-the-smallest-possible-scope)
   - 1.6 [Phase Related Optional Fields Into Nested Structs](#16-phase-related-optional-fields-into-nested-structs)
   - 1.7 [Pick a Mutation Contract](#17-pick-a-mutation-contract)
   - 1.8 [Use Discriminated Unions Over Optional Bags](#18-use-discriminated-unions-over-optional-bags)
2. [Type Safety](#2-type-safety) — **CRITICAL**
   - 2.1 [Avoid Any Annotations](#21-avoid-any-annotations)
   - 2.2 [Fix Type Definitions Instead of cast()](#22-fix-type-definitions-instead-of-cast)
   - 2.3 [Fix Type Errors, Don't Ignore Them](#23-fix-type-errors-dont-ignore-them)
   - 2.4 [Narrow Type Signatures to Runtime Reality](#24-narrow-type-signatures-to-runtime-reality)
   - 2.5 [Remove Redundant Optional Annotations](#25-remove-redundant-optional-annotations)
   - 2.6 [Trust the Type Checker — Remove Redundant Runtime Checks](#26-trust-the-type-checker-remove-redundant-runtime-checks)
   - 2.7 [Use Literal Types for Fixed String Sets](#27-use-literal-types-for-fixed-string-sets)
   - 2.8 [Use TYPE_CHECKING for Optional Dependencies](#28-use-typechecking-for-optional-dependencies)
   - 2.9 [Use TypedDict or Dataclass Instead of dict[str, Any]](#29-use-typeddict-or-dataclass-instead-of-dictstr-any)
   - 2.10 [Use isinstance() for Type Checking, Not hasattr/getattr](#210-use-isinstance-for-type-checking-not-hasattrgetattr)
3. [API Design](#3-api-design) — **HIGH**
   - 3.1 [Don't Access Private Attributes](#31-dont-access-private-attributes)
   - 3.2 [Instance Methods for State, Module Functions for Pure Logic](#32-instance-methods-for-state-module-functions-for-pure-logic)
   - 3.3 [Keep Data Models Flat and Non-Redundant](#33-keep-data-models-flat-and-non-redundant)
   - 3.4 [Keep Old Names as Deprecated Aliases](#34-keep-old-names-as-deprecated-aliases)
   - 3.5 [Order Required Fields Before Optional Fields](#35-order-required-fields-before-optional-fields)
   - 3.6 [Return New Collections from Transforms](#36-return-new-collections-from-transforms)
   - 3.7 [Underscore Prefix for Private Names](#37-underscore-prefix-for-private-names)
   - 3.8 [Use Keyword-Only Parameters for Optional Config](#38-use-keyword-only-parameters-for-optional-config)
4. [Error Handling](#4-error-handling) — **HIGH**
   - 4.1 [Catch Specific Exception Types](#41-catch-specific-exception-types)
   - 4.2 [Consolidate try/except Blocks with the Same Handler](#42-consolidate-tryexcept-blocks-with-the-same-handler)
   - 4.3 [Inherit New Exceptions from Existing Base Exceptions](#43-inherit-new-exceptions-from-existing-base-exceptions)
   - 4.4 [Trust Validated State — Skip Redundant Defensive Checks](#44-trust-validated-state-skip-redundant-defensive-checks)
   - 4.5 [Use !r Format for Identifiers in Error Messages](#45-use-r-format-for-identifiers-in-error-messages)
   - 4.6 [Use assert for Invariants, Not RuntimeError](#46-use-assert-for-invariants-not-runtimeerror)
   - 4.7 [Use raise ... from to Preserve Exception Causality](#47-use-raise-from-to-preserve-exception-causality)
   - 4.8 [Validate Input at System Boundaries](#48-validate-input-at-system-boundaries)
5. [Code Simplification](#5-code-simplification) — **MEDIUM-HIGH**
   - 5.1 [Extract Helpers After 2+ Occurrences](#51-extract-helpers-after-2-occurrences)
   - 5.2 [Flatten Nested if Statements Into and Conditions](#52-flatten-nested-if-statements-into-and-conditions)
   - 5.3 [Inline Single-Use Intermediate Variables](#53-inline-single-use-intermediate-variables)
   - 5.4 [Remove Commented-Out and Dead Code](#54-remove-commented-out-and-dead-code)
   - 5.5 [Return Early to Flatten Control Flow](#55-return-early-to-flatten-control-flow)
   - 5.6 [Use @cached_property for Expensive Derived Attributes](#56-use-cachedproperty-for-expensive-derived-attributes)
   - 5.7 [Use Comprehensions Over for+append Loops](#57-use-comprehensions-over-forappend-loops)
   - 5.8 [Use any() / all() Over Boolean-Flag Loops](#58-use-any-all-over-boolean-flag-loops)
   - 5.9 [Use x or default for Fallback Values](#59-use-x-or-default-for-fallback-values)
6. [Performance](#6-performance) — **MEDIUM**
   - 6.1 [Build a Dict Index Instead of Nested Loops](#61-build-a-dict-index-instead-of-nested-loops)
   - 6.2 [Combine Filter and Map Into One Pass](#62-combine-filter-and-map-into-one-pass)
   - 6.3 [Compile Static Regex Patterns at Module Level](#63-compile-static-regex-patterns-at-module-level)
   - 6.4 [Define TypeAdapter Instances at Module Level](#64-define-typeadapter-instances-at-module-level)
   - 6.5 [Use Generators for Streaming Iteration](#65-use-generators-for-streaming-iteration)
   - 6.6 [Use Tuple Syntax in isinstance() Checks](#66-use-tuple-syntax-in-isinstance-checks)
   - 6.7 [Use functools.lru_cache for Pure Functions](#67-use-functoolslrucache-for-pure-functions)
   - 6.8 [Use set for Repeated Membership Checks](#68-use-set-for-repeated-membership-checks)
7. [Naming](#7-naming) — **MEDIUM**
   - 7.1 [Avoid Redundant Type Suffixes in Names](#71-avoid-redundant-type-suffixes-in-names)
   - 7.2 [Drop Redundant Prefixes When Context Is Clear](#72-drop-redundant-prefixes-when-context-is-clear)
   - 7.3 [Rename When Behavior Changes](#73-rename-when-behavior-changes)
   - 7.4 [Use Consistent Terminology Across Code and Docs](#74-use-consistent-terminology-across-code-and-docs)
   - 7.5 [Use Specific Parameter and Variable Names](#75-use-specific-parameter-and-variable-names)
   - 7.6 [Use UPPER_CASE for Module Constants](#76-use-uppercase-for-module-constants)
8. [Imports & Structure](#8-imports-structure) — **LOW-MEDIUM**
   - 8.1 [Handle Optional Dependencies Explicitly](#81-handle-optional-dependencies-explicitly)
   - 8.2 [No Duplicate Imports](#82-no-duplicate-imports)
   - 8.3 [Place Imports at the Top of the File](#83-place-imports-at-the-top-of-the-file)
   - 8.4 [Remove Unused Imports](#84-remove-unused-imports)
   - 8.5 [Scope Helpers and Constants to Their Usage Site](#85-scope-helpers-and-constants-to-their-usage-site)

---

## 1. Data Modeling

**Impact: CRITICAL**

The architectural foundation. Deriving values instead of storing them, using discriminated unions instead of optional bags, making mutation contracts explicit. Mistakes here compound into state nobody intended.

### 1.1 Brand Primitive IDs With NewType

**Impact: MEDIUM (catches ID-confusion bugs at type-check time)**

When `user_id` and `team_id` are both `str`, a function accepting `UserId` will happily take a `TeamId` and fail at runtime — or worse, silently return wrong data. `NewType` makes them distinct at the type level without runtime overhead.

**Incorrect (interchangeable strings):**

```python
UserId = str
TeamId = str

def fetch_user(user_id: UserId) -> User: ...

team_id: TeamId = "team_xyz"
fetch_user(team_id)  # type checker is fine with this — runtime crash
```

`UserId = str` is a type *alias*, not a new type. The checker treats them identically.

**Correct (NewType creates a distinct nominal type):**

```python
from typing import NewType

UserId = NewType("UserId", str)
TeamId = NewType("TeamId", str)

def fetch_user(user_id: UserId) -> User: ...

team_id = TeamId("team_xyz")
fetch_user(team_id)  # type error: TeamId is not UserId
```

At runtime, `UserId("abc")` is just the string `"abc"` — no wrapper, no overhead. At type-check time, the checker refuses to confuse them.

**Construct at the boundary:** wrap raw strings as soon as they enter the system (API deserialization, DB rows). Once wrapped, they flow through the codebase as the branded type, and the checker enforces correctness.

**When NOT to brand:** short-lived local variables, truly interchangeable strings (raw log message bodies, arbitrary user text). Reserve branding for domain identifiers that must not be mixed up.

### 1.2 Create Explicit Variants Instead of Mode Flags

**Impact: CRITICAL (eliminates conditional-logic sprawl)**

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

### 1.3 Delete Dead Variants

**Impact: MEDIUM (removes code paths that can't be reached)**

If a type has a variant that is never constructed — a `status: Literal["open", "closed", "archived"]` where `"archived"` is never set — delete the variant. Agents leave them behind "in case we need them later." The result is defensive branches in every consumer for a state that cannot occur.

**Incorrect ("archived" variant is declared but never produced):**

```python
from typing import Literal

OrderStatus = Literal["open", "paid", "shipped", "archived"]

def render_status(status: OrderStatus) -> str:
    match status:
        case "open": return "Awaiting payment"
        case "paid": return "Preparing to ship"
        case "shipped": return "In transit"
        case "archived": return "Archived"  # when does this branch ever run?
```

Grep the codebase: nothing assigns `"archived"`. That branch is unreachable, yet every consumer must handle it. It's a ghost.

**Correct (delete it):**

```python
from typing import Literal

OrderStatus = Literal["open", "paid", "shipped"]

def render_status(status: OrderStatus) -> str:
    match status:
        case "open": return "Awaiting payment"
        case "paid": return "Preparing to ship"
        case "shipped": return "In transit"
```

One fewer imaginary case. When "archived" actually becomes a requirement, add it then — tied to the real code that creates it.

**When NOT to delete:** if the variant exists in serialized data (old database rows, historical JSON) you still need to parse, keep it — but mark the non-canonical variants clearly (e.g., with a comment pointing to the migration that will remove them).

### 1.4 Derive, Don't Store

**Impact: CRITICAL (eliminates flag-sync bugs and halves the state space)**

Every boolean you add doubles the theoretical state space. When a value can be computed from data you already have, do not store it. Agents are tempted to cache derived values "for performance" — the cost is multiple mutation sites that must stay in sync, and they won't.

**Incorrect (four flags that must be kept in sync):**

```python
from dataclasses import dataclass

@dataclass
class ThreadState:
    was_interrupted: bool
    did_assistant_finish: bool
    did_assistant_error: bool
    was_tool_call_only: bool

def should_show_footer(state: ThreadState) -> bool:
    return (
        state.did_assistant_finish
        and not state.was_interrupted
        and not state.did_assistant_error
        and not state.was_tool_call_only
    )
```

Four fields to answer one question. Four mutation sites elsewhere that must keep them synchronized. One missed update and the footer lies.

**Correct (derive from the event log):**

```python
def should_show_footer(events: list[SessionEvent]) -> bool:
    latest = get_latest_assistant_message(events)
    if latest is None:
        return False
    return (
        latest.completed
        and not latest.error
        and latest.finish_reason != "tool_calls"
    )
```

The answer is now computed from evidence that already exists. No sync required — one source of truth.

**When NOT to derive:**

- The domain genuinely has a state machine with ordered transitions (a checkout step *is* the state, not a cached conclusion)
- Temporal or external data that cannot be re-derived (timestamps from async processes, API responses needed downstream)
- The derivation is meaningfully more expensive than the stored value *and* you've measured the cost

**The debugging payoff:** pure derivation means tests become data-in, answer-out. Load fixtures, call the function, assert the result. No mocks, no timing reproduction.

### 1.5 Encapsulate Mutable State in the Smallest Possible Scope

**Impact: HIGH (limits the blast radius of state mutations)**

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

### 1.6 Phase Related Optional Fields Into Nested Structs

**Impact: HIGH (one optional check instead of eight)**

When fields are "all present or all absent" in practice, don't model them as eight independent optionals at the top level. Agents tend to flatten everything into one class with `firstName: str | None`, `lastName: str | None`, etc. — which means every consumer writes `profile.first_name or defaults.first_name` eight times, and the type says nothing about which fields co-occur.

**Incorrect (twelve independent optionals):**

```python
from dataclasses import dataclass

@dataclass
class UserProfile:
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    job_title: str | None = None
    billing_address: str | None = None
    billing_city: str | None = None
    billing_zip: str | None = None
    card_last4: str | None = None
    card_brand: str | None = None
    card_expires: str | None = None
```

Consumers write `profile.first_name or ""` twelve times. When billing exists, is `billing_address` guaranteed? The type says no. Someone will hit `profile.card_last4` with `billing_address = None` and either crash or silently produce garbage.

**Correct (grouped into phases):**

```python
from dataclasses import dataclass

@dataclass
class Identity:
    first_name: str
    last_name: str
    email: str
    phone: str | None = None

@dataclass
class Employment:
    company: str
    job_title: str

@dataclass
class Billing:
    address: str
    city: str
    zip_code: str
    card_last4: str
    card_brand: str
    card_expires: str

@dataclass
class UserProfile:
    identity: Identity | None = None
    employment: Employment | None = None
    billing: Billing | None = None
```

Now consumers check one optional: `if profile.billing is not None: use profile.billing.card_last4`. When `identity` exists, every identity field is guaranteed. The type system enforces the co-occurrence that was always true in practice.

**Heuristic:** if three or more optional fields are always set or always unset together, they belong in a nested struct.

### 1.7 Pick a Mutation Contract

**Impact: HIGH (prevents ambiguous caller expectations)**

A function that mutates its input *and* returns the same reference gives callers no way to tell whether to use the return value or the original. Pick one: mutate and return `None`, or clone and return the new value. Never both.

**Incorrect (mutates and returns — callers can't tell which to use):**

```python
def with_pending_action(state: AppState, action: str) -> AppState:
    state.pending_action = action  # mutation
    return state                   # and return
```

A caller reading `new_state = with_pending_action(state, "confirm")` reasonably assumes `state` is unchanged. It isn't. Another caller reads `with_pending_action(state, "confirm")` (ignoring the return) and assumes that's fine. It is — but only because the mutation happened. Two callers, two wrong mental models.

**Correct (mutate, return None):**

```python
def apply_pending_action(state: AppState, action: str) -> None:
    state.pending_action = action
```

The `None` return and the imperative verb (`apply_`) signal that this is a command. Caller knows the input was modified.

**Also correct (clone, return new):**

```python
from dataclasses import replace

def with_pending_action(state: AppState, action: str) -> AppState:
    return replace(state, pending_action=action)
```

`with_` naming signals a functional transform. The input is untouched; the caller must use the returned value.

**Naming conventions:**
- `apply_*`, `set_*`, `update_*_inplace` — mutate, return `None`
- `with_*`, `update_*`, `derive_*` — return a new value, leave input alone

The contract should be obvious from the name and signature without reading the body.

### 1.8 Use Discriminated Unions Over Optional Bags

**Impact: CRITICAL (makes impossible states unrepresentable)**

Every optional field is a question the rest of the codebase must answer every time it touches the data. Agents tend to add optional fields as features grow, creating models where half the combinations are semantically invalid. Use a tagged (discriminated) union so the type system enforces which fields travel together.

**Incorrect (optional fields create impossible state combinations):**

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class PaymentState:
    status: Literal["idle", "processing", "settled"]
    gateway: Literal["stripe", "paypal"] | None = None
    transaction_id: str | None = None
    initiated_at: str | None = None
    settled_at: str | None = None
```

When `status == "idle"`, should `gateway` exist? The type says maybe. When `status == "settled"`, is `settled_at` guaranteed? The type says no. Every consumer defensively checks for `None` on fields that must be present, or forgets to check fields that might not be.

**Correct (each variant carries exactly the fields it needs):**

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class PaymentIdle:
    status: Literal["idle"] = "idle"

@dataclass
class PaymentProcessing:
    gateway: Literal["stripe", "paypal"]
    transaction_id: str
    initiated_at: str
    status: Literal["processing"] = "processing"

@dataclass
class PaymentSettled:
    gateway: Literal["stripe", "paypal"]
    transaction_id: str
    settled_at: str
    status: Literal["settled"] = "settled"

PaymentState = PaymentIdle | PaymentProcessing | PaymentSettled
```

Now `match payment.status:` narrows exactly, `transaction_id` is non-optional on the variants that have it, and impossible combinations (idle with a transaction ID, settled without a timestamp) are unrepresentable.

**With Pydantic:** use `Field(discriminator="status")` and a `status: Literal[...]` tag on each variant — Pydantic will validate and narrow automatically.

**Null over sentinels:** don't invent `"none"` action values. `pending_action: PendingAction | None` beats `pending_action: Literal["none", "confirm-address", "select-shipping"]`. Absence is not an action.

## 2. Type Safety

**Impact: CRITICAL**

Precise types catch bugs at type-check time and keep IDE autocomplete useful. The type checker is load-bearing — keep it that way. No `Any` drift, no `# type: ignore` without justification.

### 2.1 Avoid Any Annotations

**Impact: CRITICAL (preserves type-checker coverage)**

`Any` turns off the type checker for that value — it accepts anything, produces anything, and propagates silently into every call site that consumes it. Agents reach for `Any` when the right type feels hard; almost always, a `Protocol`, `TypeVar`, or `Union` is available.

**Incorrect (Any leaks through the system):**

```python
from typing import Any

def process_items(items: Any) -> Any:
    return [transform(item) for item in items]

def transform(item: Any) -> Any:
    return item.value.upper()
```

The checker cannot help here. A caller passing a `dict` instead of a list silently walks into runtime errors. `item.value.upper()` is unchecked — a typo in `value` would never be caught.

**Correct (precise types; Protocol for duck-typed inputs):**

```python
from typing import Protocol

class HasValue(Protocol):
    value: str

def process_items(items: list[HasValue]) -> list[str]:
    return [transform(item) for item in items]

def transform(item: HasValue) -> str:
    return item.value.upper()
```

The checker now verifies that every call site passes a list of objects with a `.value: str` attribute. Typos in `.value` get caught. Return types propagate.

**Correct (TypeVar for truly generic containers):**

```python
from typing import TypeVar

T = TypeVar("T")

def first_or_none(items: list[T]) -> T | None:
    return items[0] if items else None
```

Generic, not unchecked.

**When `Any` is genuinely unavoidable** (interop with dynamically typed libraries, some JSON boundaries), restrict its scope to one line, narrow to a concrete type immediately, and document the invariant in a comment.

### 2.2 Fix Type Definitions Instead of cast()

**Impact: HIGH (surfaces structural mismatches instead of hiding them)**

`cast(T, value)` tells the checker to pretend `value` is a `T` with no runtime check. When called to paper over a structural mismatch, it hides a design problem. Reach for it only when runtime logic genuinely narrows in a way the checker can't express.

**Incorrect (cast masks an unnecessarily wide return type):**

```python
from typing import cast

def load_config() -> dict[str, object]:
    return json.loads(CONFIG_PATH.read_text())

def get_timeout() -> int:
    config = load_config()
    return cast(int, config["timeout"])  # we're just telling the checker to trust us
```

The real issue: `load_config` returns `dict[str, object]` because `json.loads` does. But this project's config has a known shape — fix the source type.

**Correct (declare the real structure):**

```python
from typing import TypedDict

class Config(TypedDict):
    timeout: int
    retries: int

def load_config() -> Config:
    return json.loads(CONFIG_PATH.read_text())  # validate or cast here, once

def get_timeout() -> int:
    config = load_config()
    return config["timeout"]  # known to be int from Config
```

Now every downstream consumer benefits from the typed shape.

**When `cast()` is the right tool:** when runtime logic narrows beyond what the checker can prove — e.g., after a literal tag check, a custom predicate, or a known invariant enforced elsewhere.

```python
from typing import cast

def handle_success(result: ApiResponse) -> str:
    # An earlier check already verified result.status == "success"
    # but the checker can't propagate that narrowing here
    assert result.status == "success"
    return cast(SuccessResponse, result).data  # ok; narrowing is real
```

Even then, `isinstance` or a `TypeGuard` function is usually cleaner. Reserve `cast` for cases where those don't fit.

**Rule of thumb:** if you're tempted to `cast`, first ask whether the source type should be narrower. 8 times out of 10, yes.

### 2.3 Fix Type Errors, Don't Ignore Them

**Impact: HIGH (prevents masked errors from compounding)**

`# type: ignore` and `# pyright: ignore` silence the checker — but the underlying problem stays. Agents reach for ignore comments when a type looks hard; each one degrades the signal from every future run. Fix the error properly, and when a suppression is genuinely unavoidable, document why.

**Incorrect (ignore comment masks the real problem):**

```python
def compute(items: list[int] | None) -> int:
    return sum(items)  # type: ignore  # noqa
```

The checker flagged this because `sum(None)` crashes at runtime. The ignore hides a real bug.

**Correct (handle the None case):**

```python
def compute(items: list[int] | None) -> int:
    if items is None:
        return 0
    return sum(items)
```

The type system caught a real bug; fixing it is the right answer.

**When a suppression is genuinely required** (a complex generic the checker can't handle, a known checker limitation, an external library with bad stubs), include:

1. The specific error code (e.g., `# type: ignore[arg-type]`)
2. A comment explaining the safety reasoning

```python
# mypy cannot narrow through the factory's return type, but the
# registry guarantees adapters[cls] returns cls instances.
# See: https://github.com/python/mypy/issues/XXXX
adapter = adapters[cls]  # type: ignore[assignment]
```

A reviewer should be able to read the comment and confirm the suppression is justified without re-deriving the reasoning.

**Escape hatches to prefer before ignoring:**
- `cast(T, value)` with a comment (see `types-fix-types-not-cast` for when it's appropriate)
- `assert isinstance(x, T)` — runtime check plus narrowing
- `TypeGuard` functions for reusable narrowing
- Actually fixing the type signatures upstream

Reach for `# type: ignore` last, not first.

### 2.4 Narrow Type Signatures to Runtime Reality

**Impact: MEDIUM (eliminates unreachable branches and false permissiveness)**

If control flow (a `match` statement, an API contract, an earlier `isinstance` check) guarantees that only a subset of a union reaches a code path, the annotation should reflect that — not the wider union. Over-broad annotations create dead branches and suggest possibilities the code can't actually handle.

**Incorrect (signature wider than reality):**

```python
def render_tool_result(part: MessagePart) -> str:
    # by contract this is only called with ToolResultPart or ToolCallPart
    if isinstance(part, ToolResultPart):
        return f"Result: {part.content}"
    if isinstance(part, ToolCallPart):
        return f"Call: {part.tool_name}"
    if isinstance(part, TextPart):
        return part.text  # unreachable — caller never passes TextPart
    raise ValueError(f"unexpected part: {part}")
```

The `TextPart` branch can't run (the caller guarantees it), but the type says `MessagePart`. Readers have to figure out the contract from context.

**Correct (tighten the annotation):**

```python
ToolPart = ToolCallPart | ToolResultPart

def render_tool_result(part: ToolPart) -> str:
    if isinstance(part, ToolResultPart):
        return f"Result: {part.content}"
    return f"Call: {part.tool_name}"  # must be ToolCallPart
```

The signature documents the contract. No dead branches. A caller that tries to pass a `TextPart` gets a type error, not a runtime `ValueError`.

**When the wider type is necessary:** when the function genuinely handles the full union at some call sites and a subset at others, accept the widest used type and narrow inside. Don't invent a separate wider signature "to be safe."

**Exhaustiveness check:**

```python
from typing import assert_never

def render_tool_result(part: ToolPart) -> str:
    match part:
        case ToolResultPart(): return f"Result: {part.content}"
        case ToolCallPart(): return f"Call: {part.tool_name}"
        case _: assert_never(part)  # checker fails if union grows
```

`assert_never` ensures that if `ToolPart` gains a new variant, every `match` on it is re-examined.

### 2.5 Remove Redundant Optional Annotations

**Impact: MEDIUM (eliminates false uncertainty in the type signature)**

An annotation of `X | None` tells readers and the checker that `None` is a real possibility — every consumer now writes a `None` check. When the value is guaranteed to be set (by the constructor, by the control flow, by an earlier validation), `| None` lies about the API.

**Incorrect (optional annotation on a guaranteed-present value):**

```python
from dataclasses import dataclass

@dataclass
class Session:
    user_id: str
    token: str | None = None  # but we always generate a token in __post_init__

    def __post_init__(self) -> None:
        if self.token is None:
            self.token = generate_token()
```

Every consumer of `session.token` now writes `if session.token is not None: ...` — for a value that is always present.

**Correct (use a factory default; drop the optional):**

```python
from dataclasses import dataclass, field

@dataclass
class Session:
    user_id: str
    token: str = field(default_factory=generate_token)
```

`session.token` is now unambiguously a `str`. No defensive `None` checks downstream.

**Also incorrect (`| None` on `NotRequired` TypedDict fields):**

```python
from typing import TypedDict, NotRequired

class Config(TypedDict):
    name: str
    timeout: NotRequired[int | None]  # already optional via NotRequired
```

`NotRequired` already expresses "may be absent." Adding `| None` lets the caller pass `None` *instead of* omitting — which is rarely what you want. Either the field is absent (`NotRequired`) or it has a value (no `| None`).

**When `| None` is correct:** when `None` is a real, semantic value — "no assignee," "no parent," "not yet fetched." Absence as a meaningful state deserves `None`.

**Heuristic:** if every consumer writes `if x is not None:` before using the value, either `None` is never really set (remove `| None`) or you should have a different sentinel (a default, a distinct variant).

### 2.6 Trust the Type Checker — Remove Redundant Runtime Checks

**Impact: MEDIUM (removes noise and signals confidence in the types)**

When types already constrain a value, runtime checks for the same constraint add noise and imply the types aren't trustworthy. Every redundant `assert` or `isinstance` is a vote of no confidence in the rest of the type system.

**Incorrect (runtime checks that duplicate the type):**

```python
def process_user(user: User) -> str:
    assert user is not None        # type says User, not User | None
    assert isinstance(user, User)   # type already says User
    assert user.name                # if name: str, this only catches empty strings
    return user.name.upper()
```

The first two lines add nothing. The third conflates "empty string" with "None" — if that matters, say so with a dedicated check and a real error message.

**Correct (trust the signature):**

```python
def process_user(user: User) -> str:
    return user.name.upper()
```

If callers pass `None` against the signature, that's a bug in the caller — and the type checker will flag it at the call site.

**Also incorrect (defensive check after validation):**

```python
def process_request(raw: str) -> Response:
    validated = validate(raw)  # returns ValidatedRequest, never None
    if validated is None:
        raise ValueError("invalid")  # unreachable
    return handle(validated)
```

`validate` returns `ValidatedRequest` by its signature — no `None`. The check is dead.

**When runtime checks are the right tool:**

- At **trust boundaries**: external API responses, deserialized user input, third-party callbacks where the type is aspirational
- As **narrowing aids**: `assert isinstance(x, T)` to narrow from a wider type the checker can't otherwise see
- For **invariants the checker can't express**: "this list is sorted," "this counter is positive"

Inside your own code, let the types do the work.

### 2.7 Use Literal Types for Fixed String Sets

**Impact: HIGH (catches invalid strings at type-check time)**

When a parameter accepts one of a fixed set of string values, `str` is too wide — every typo is legal. `Literal["a", "b", "c"]` narrows the type to exactly those values and enables `match` exhaustiveness checking.

**Incorrect (plain str accepts anything):**

```python
def set_log_level(level: str) -> None:
    ...

set_log_level("DEUBG")  # typo — compiles fine, runtime surprise
```

The checker cannot tell you `"DEUBG"` is invalid. A typo at a call site silently passes through until the function hits an unexpected branch.

**Correct (Literal restricts to the valid set):**

```python
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

def set_log_level(level: LogLevel) -> None:
    ...

set_log_level("DEUBG")  # type error — caught at type-check time
```

IDEs autocomplete the valid values. Typos are flagged before running.

**Pairs well with `match`:**

```python
def level_priority(level: LogLevel) -> int:
    match level:
        case "DEBUG": return 10
        case "INFO": return 20
        case "WARNING": return 30
        case "ERROR": return 40
```

If a new level is added to the `Literal` type without updating this `match`, checkers with exhaustiveness support flag the missing case.

**When to use `Enum` instead:** when the values have methods or rich behavior (e.g., `LogLevel.DEBUG.name`, `LogLevel.DEBUG.value`). Enums also work well with exhaustiveness checking but carry more ceremony than `Literal`. For plain string tags, `Literal` is lighter.

**When to use plain `str`:** free-form user input, message bodies, URLs, any field that isn't a finite enumeration.

### 2.8 Use TYPE_CHECKING for Optional Dependencies

**Impact: MEDIUM (preserves type hints without forcing the import)**

When a module's type hints reference a class from an optional dependency, importing the module should not require that dependency to be installed. `if TYPE_CHECKING:` blocks let the checker see the import while the runtime stays lean.

**Incorrect (importing an optional dep at runtime):**

```python
import anthropic  # crashes if anthropic is not installed

class AnthropicProvider:
    def __init__(self, client: anthropic.Client) -> None:
        self._client = client
```

A user installing just the core package and never touching Anthropic still gets a `ModuleNotFoundError` at import time.

**Incorrect (falling back to `Any`):**

```python
from typing import Any

class AnthropicProvider:
    def __init__(self, client: Any) -> None:  # we gave up on the type
        self._client = client
```

This works at runtime but loses type safety on every method that uses `self._client`.

**Correct (TYPE_CHECKING block + quoted hint):**

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import anthropic

class AnthropicProvider:
    def __init__(self, client: anthropic.Client) -> None:
        self._client = client
```

With `from __future__ import annotations`, all annotations are strings at runtime — so `anthropic.Client` in the signature doesn't need the import to resolve. The checker still resolves it during type-check because it sees the `TYPE_CHECKING` branch.

**Pattern for optional-dep packages:**

```python
# At module top
try:
    import anthropic
except ImportError as e:
    raise ImportError(
        "Please install the anthropic extra: `pip install 'mylib[anthropic]'`"
    ) from e
```

Combine the runtime guard (helpful error if the user hits a code path that needs the dep) with `TYPE_CHECKING` for the hints.

### 2.9 Use TypedDict or Dataclass Instead of dict[str, Any]

**Impact: CRITICAL (restores type-checker coverage over config and payloads)**

When the shape of a dict is known (config objects, API payloads, structured event data), `dict[str, Any]` is a lie — the structure exists, it's just not declared. Every access becomes a runtime gamble. `TypedDict` or `dataclass` restores type-checker coverage.

**Incorrect (dict[str, Any] erases structure):**

```python
from typing import Any

def create_user(config: dict[str, Any]) -> User:
    name = config["name"]          # what type?
    age = config.get("age", 0)     # what type? what's the default type?
    prefs = config.get("prefs", {})  # dict or None or the passed-in value?
    return User(name=name.upper(), age=age + 1, prefs=prefs)
```

The checker can't tell you that `config["name"]` should be a `str`, that `age` should be an `int`, or that `prefs` has its own structure. Every `.upper()` call is unchecked.

**Correct (TypedDict — dict-shaped but typed):**

```python
from typing import TypedDict, NotRequired

class UserPreferences(TypedDict):
    theme: NotRequired[str]
    notifications: NotRequired[bool]

class UserConfig(TypedDict):
    name: str
    age: NotRequired[int]
    prefs: NotRequired[UserPreferences]

def create_user(config: UserConfig) -> User:
    name = config["name"]                     # str
    age = config.get("age", 0)                # int
    prefs = config.get("prefs", {})           # UserPreferences
    return User(name=name.upper(), age=age + 1, prefs=prefs)
```

**Correct (dataclass — when this is an in-memory value, not JSON):**

```python
from dataclasses import dataclass, field

@dataclass
class UserPreferences:
    theme: str = "light"
    notifications: bool = True

@dataclass
class UserConfig:
    name: str
    age: int = 0
    prefs: UserPreferences = field(default_factory=UserPreferences)

def create_user(config: UserConfig) -> User:
    return User(name=config.name.upper(), age=config.age + 1, prefs=config.prefs)
```

**When to pick which:**
- `TypedDict` — for serialization boundaries where the value genuinely is a `dict` (JSON APIs, `**kwargs`)
- `dataclass` — for in-memory values with behavior, defaults, and ergonomics
- `pydantic.BaseModel` — when you also need runtime validation

`dict[str, Any]` is only the right answer for *truly* unstructured data — log context, free-form metadata. If you know the fields, declare them.

### 2.10 Use isinstance() for Type Checking, Not hasattr/getattr

**Impact: CRITICAL (enables proper type narrowing for the checker)**

Type checkers narrow types through `isinstance()` checks, discriminator match statements, and `TypeGuard` functions — not through `hasattr()`, `getattr()`, or `type(obj).__name__ == "..."`. Agents reach for `hasattr` for "flexibility"; the actual cost is that the checker can't narrow and refactors silently break string comparisons.

**Incorrect (hasattr/getattr defeats type narrowing):**

```python
def process(part: MessagePart) -> str:
    if hasattr(part, "tool_name"):
        return f"Tool: {part.tool_name}"  # type checker: attribute is Any
    if getattr(part, "kind", None) == "text":
        return part.text  # type checker: does part.text exist? unclear
    if type(part).__name__ == "ImagePart":
        return f"Image: {part.url}"  # fragile: renaming ImagePart breaks this
    return "unknown"
```

The checker gives up on every branch. If `ToolPart` is renamed, the `type(...).__name__` string comparison silently stops matching — and no tests catch it because the function still runs.

**Correct (isinstance enables narrowing):**

```python
def process(part: MessagePart) -> str:
    if isinstance(part, ToolPart):
        return f"Tool: {part.tool_name}"  # narrowed to ToolPart
    if isinstance(part, TextPart):
        return part.text                    # narrowed to TextPart
    if isinstance(part, ImagePart):
        return f"Image: {part.url}"         # narrowed to ImagePart
    return "unknown"
```

Now the checker verifies that `part.tool_name`, `part.text`, and `part.url` each exist on the narrowed type. Renaming a class triggers type errors at every use site.

**For tagged unions, use `match` on the discriminator:**

```python
def process(part: MessagePart) -> str:
    match part.kind:
        case "tool":  return f"Tool: {part.tool_name}"
        case "text":  return part.text
        case "image": return f"Image: {part.url}"
```

When `part.kind` is a `Literal` discriminator on a `Union`, `match` narrows each branch to the matching variant.

**When to reach for `hasattr`:** genuinely optional extension protocols where classes may or may not implement a method. Even then, prefer `isinstance(obj, Protocol)` with a `runtime_checkable` Protocol over raw attribute probing.

## 3. API Design

**Impact: HIGH**

Interface decisions that compound over years. Keyword-only parameters, private underscores, immutable transforms. The difference between an API that ages well and one that accumulates compatibility shims.

### 3.1 Don't Access Private Attributes

**Impact: HIGH (prevents breakage when internals change)**

`_prefixed` names are the author's contract: "this is internal, it may change." Reaching into another module's or class's private attributes couples your code to implementation details you weren't invited into. Use the public API, or ask the owner to expose what you need.

**Incorrect (poking at private state):**

```python
from some_lib import Client

client = Client()
# peeking at a private attribute because there's no public way
retry_count = client._retry_state["count"]
client._pool.clear()  # mutating private state
```

Next version of `some_lib` renames `_retry_state` to `_retries` (it's private, they're allowed to) — your code breaks with no warning. Or worse, `_pool.clear()` no longer does what you assumed, and you corrupt state silently.

**Correct (use the public API):**

```python
from some_lib import Client

client = Client()
retry_count = client.stats.retries  # public property
client.reset_pool()                  # public method
```

If `some_lib` doesn't expose what you need, open an issue or PR. Using `_private` is a workaround, not a fix.

**Inside your own code:** same rule applies between modules. If `module_a` finds itself reaching into `module_b._helpers`, the helper probably shouldn't be private — or `module_a` shouldn't need it.

**The exception:** testing your own internals. Unit tests for a class may legitimately assert on `_private` state. Even then, prefer testing through the public interface when feasible — tests that poke at internals are brittle to refactoring.

**Double underscore (`__name`) is stronger:** Python name-mangles `__name` to `_ClassName__name`, making accidental access even harder. Use it for attributes you're committed to keeping inaccessible.

### 3.2 Instance Methods for State, Module Functions for Pure Logic

**Impact: MEDIUM (avoids unnecessary coupling while enabling polymorphism)**

Agents tend to put everything on classes because "that's how OOP works" — or conversely, make everything a module-level function because "pure is better." The right call depends on whether the function genuinely needs `self` or enables polymorphism.

**Use an instance method when:**
- The function accesses `self` attributes
- It's a natural operation on the object (the method *is* part of the object's interface)
- Subclasses will override it (polymorphism)

**Use a module-level function when:**
- Nothing about the logic depends on instance state
- The function is a pure utility that happens to take an object of that class
- Multiple classes could reasonably use the same helper

**Incorrect (module-level function awkwardly threading state):**

```python
def update_user_preferences(user: User, key: str, value: object) -> None:
    user.prefs[key] = value
    user.last_modified = now()

def get_user_display_name(user: User) -> str:
    return f"{user.first_name} {user.last_name}"
```

These both mutate/read `user` state and are core user operations — they belong on `User`.

**Correct (instance methods):**

```python
class User:
    def update_preference(self, key: str, value: object) -> None:
        self.prefs[key] = value
        self.last_modified = now()

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**Incorrect (instance method that doesn't need `self`):**

```python
class DateFormatter:
    def format_iso(self, d: date) -> str:
        return d.isoformat()  # doesn't touch self
```

**Correct (module-level function):**

```python
def format_iso(d: date) -> str:
    return d.isoformat()
```

**Extract shared logic to private top-level helpers** when multiple classes need the same computation — don't duplicate it across methods.

**`@staticmethod` / `@classmethod`:** reach for these sparingly. If a method doesn't need `self` or `cls`, it's usually a module-level function. Reserve them for alternative constructors (`@classmethod`) or namespace-grouped utilities where the class genuinely makes things more discoverable.

### 3.3 Keep Data Models Flat and Non-Redundant

**Impact: MEDIUM (reduces API surface and prevents field drift)**

Data models drift when fields duplicate each other, wrap single values in unnecessary containers, or mirror fields from the parent structure. Each duplicate is a second source of truth that can go stale. Each single-key wrapper adds access ceremony for no gain.

**Incorrect (redundant fields, single-key wrappers, unnecessary lists):**

```python
from dataclasses import dataclass

@dataclass
class ToolReturn:
    tool_name: str                           # also in parent
    call_id: str                             # also in parent
    content: dict[str, object]               # single-key wrapper around return_value
    return_value: dict[str, object]          # duplicated in content
    messages: list[Message]                  # always contains exactly one Message

@dataclass
class ToolCall:
    tool_name: str
    call_id: str
    return_part: ToolReturn
```

`tool_name` and `call_id` are carried on both the parent and the child — they'll drift. `content` wraps `return_value`. `messages` is a list that always has length one.

**Correct (flat, non-redundant):**

```python
from dataclasses import dataclass

@dataclass
class ToolReturn:
    content: object  # the actual return value, unwrapped
    message: Message

@dataclass
class ToolCall:
    tool_name: str
    call_id: str
    return_part: ToolReturn
```

`tool_name` and `call_id` live on the parent only. `content` holds the value directly. `message` is singular because there's only ever one.

**Check for:**

- Fields that exist on both parent and child (pick one, usually parent)
- `data: {"value": X}` single-key wrappers (unwrap to `data: X`)
- Lists that always contain exactly one element (use a scalar)
- Fields that are computed from other fields (derive, don't store)

**Why it matters:** redundancy means every mutation site has two (or more) places to update. Skipping one creates a drift bug that's only visible when the fields disagree.

### 3.4 Keep Old Names as Deprecated Aliases

**Impact: HIGH (enables gradual migration without breakage)**

Renaming a public function, class, or parameter is a breaking change. Users upgrade at their own pace; if the old name vanishes, they can't. Keep the old name as a deprecated alias for at least one release, pointing at the new name.

**Incorrect (rename breaks existing code immediately):**

```python
# v1.0
def get_user(user_id: str) -> User: ...

# v1.1
def fetch_user(user_id: str) -> User: ...  # renamed — v1.0 callers now crash
```

**Correct (deprecated alias):**

```python
import warnings

def fetch_user(user_id: str) -> User:
    ...

def get_user(user_id: str) -> User:
    warnings.warn(
        "get_user is deprecated; use fetch_user instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return fetch_user(user_id)
```

Old callers keep working with a warning; new callers use the new name.

**For parameter renames, use `typing.deprecated` (Python 3.13+) or keyword handling:**

```python
def fetch_user(
    user_id: str,
    *,
    timeout: float = 30,
    user_id_alt: str | None = None,  # old name
) -> User:
    if user_id_alt is not None:
        warnings.warn(
            "user_id_alt is deprecated; pass user_id instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        user_id = user_id_alt
    ...
```

**Deprecation policy:**

1. Add the new name. Old name becomes an alias.
2. Emit a `DeprecationWarning` explaining the migration.
3. Document the deprecation in the changelog and docstrings.
4. Remove the alias in a later major version (follow your project's deprecation window — typically one or two releases).

**When you can skip the alias:** the function was never part of the documented public API (starts with `_`, not in `__all__`, not in published docs). Internal renames don't need deprecation.

### 3.5 Order Required Fields Before Optional Fields

**Impact: HIGH (Python enforces this at class-definition time)**

Python's dataclass implementation requires fields without defaults to precede fields with defaults — trying to put an optional field before a required one is a `TypeError` at class-definition time. More importantly, the order communicates intent: required first, defaults last.

**Incorrect (raises `TypeError`):**

```python
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str = ""
    version: str         # TypeError: non-default argument follows default argument
```

**Correct (required fields first):**

```python
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    version: str
    description: str = ""
```

**When a required field must come after an optional one:** use keyword-only with `KW_ONLY`. This lets you reorder freely while still enforcing "required" via the type system:

```python
from dataclasses import dataclass, KW_ONLY

@dataclass
class Tool:
    name: str
    _: KW_ONLY
    description: str = ""
    version: str  # required, keyword-only — order no longer constrained
```

Everything after `_: KW_ONLY` is keyword-only, so the "required before optional" rule stops applying — the caller must pass them by name.

**Same rule applies to function parameters:**

```python
# bad: positional default before positional required
def connect(host="localhost", port): ...  # SyntaxError

# good: required first
def connect(port, host="localhost"): ...

# also good: keyword-only lets you mix freely
def connect(*, port, host="localhost", retries): ...
```

### 3.6 Return New Collections from Transforms

**Impact: HIGH (prevents surprising side effects)**

A function called `filter_active(users)` that mutates `users` in place is a trap — the name says "filter," the behavior says "modify." Default to returning new collections. Reserve mutation for functions whose names make it unmistakable (`sort_in_place`, `update_items`).

**Incorrect (transform that secretly mutates):**

```python
def filter_active(users: list[User]) -> list[User]:
    users[:] = [u for u in users if u.is_active]  # mutates input!
    return users
```

A caller doing `active = filter_active(all_users); log_total(len(all_users))` gets a confusing bug — `all_users` was modified, but the call site doesn't reveal that.

**Correct (return a new list):**

```python
def filter_active(users: list[User]) -> list[User]:
    return [u for u in users if u.is_active]
```

Input is untouched. Behavior matches the name.

**When in-place mutation is appropriate:** when it's performance-critical on a measured hot path, and the name signals it unambiguously.

```python
def sort_in_place(items: list[int]) -> None:
    items.sort()

def update_status_inplace(user: User, status: str) -> None:
    user.status = status
```

Name conventions:
- `*_in_place` / `*_inplace` — mutates, returns `None`
- `update_*` — mutates (if state-management convention) or returns new (if data-transform convention); be consistent within the codebase
- `with_*`, `filter_*`, `map_*`, `derive_*` — returns new, input untouched

**Rule of thumb:** if the function's name is a verb phrase describing a transformation, default to returning new. If it's imperative and clearly a command (`sort`, `apply`, `set`), mutation is expected.

### 3.7 Underscore Prefix for Private Names

**Impact: HIGH (signals internal API and limits backward-compat obligations)**

Names that start with `_` are internal. Names that don't are public — and public means "backward-compatible forever unless deprecated." Agents tend to leave implementation details public because there's no language-level enforcement; underscore them on the way in, not after they've leaked.

**Incorrect (implementation detail treated as public):**

```python
# mymodule.py
def format_date(d):
    return _to_iso_string(d)

def to_iso_string(d):    # helper — but no underscore, so it's public
    return d.isoformat()

__all__ = ["format_date", "to_iso_string"]  # accidentally exported
```

Now `to_iso_string` is part of the module's public API. Changing its signature, renaming it, or removing it breaks anyone who imported it.

**Correct (underscore the helper; exclude from `__all__`):**

```python
# mymodule.py
def format_date(d):
    return _to_iso_string(d)

def _to_iso_string(d):
    return d.isoformat()

__all__ = ["format_date"]
```

`_to_iso_string` is clearly internal. You can rename it, delete it, change its signature — no backward-compat obligation.

**Same rule for class attributes and methods:**

```python
class Cache:
    def get(self, key: str) -> object | None: ...     # public
    def _evict_lru(self) -> None: ...                  # internal helper
    def _entries(self) -> dict[str, object]: ...       # internal state access
```

**Don't reach into `_private` from outside.** If you find yourself writing `obj._internal`, either (a) the attribute should be public and the owner should know, or (b) the design has a gap — add a public method instead. Reaching into `_private` couples you to implementation details that may change.

**`__all__` is the contract:** `from mymodule import *` respects `__all__`. Tools like Sphinx and type checkers also use it to determine the public surface. Keep it minimal and accurate.

### 3.8 Use Keyword-Only Parameters for Optional Config

**Impact: HIGH (prevents breakage when adding or reordering params)**

Positional parameters lock in their order forever — adding a new parameter in the middle breaks every caller. Keyword-only parameters (after `*` in functions, after `_: KW_ONLY` in dataclasses) let you add, remove, or reorder without breaking callers. Agents default to positional; push back.

**Incorrect (positional config — order is now part of the API):**

```python
def fetch(url, timeout=30, retries=3, verify_ssl=True, backoff=1.5):
    ...

fetch("https://api.example.com", 60, 5, False)
```

What do `60, 5, False` mean at this call site? Only the function signature knows. And if you want to add `user_agent` between `retries` and `verify_ssl`, every positional call site breaks.

**Correct (keyword-only for config params):**

```python
def fetch(url, *, timeout=30, retries=3, verify_ssl=True, backoff=1.5):
    ...

fetch("https://api.example.com", timeout=60, retries=5, verify_ssl=False)
```

The `*` forces everything after it to be passed by name. Call sites self-document. New params can slot anywhere without breaking callers.

**For dataclasses, use `KW_ONLY`:**

```python
from dataclasses import dataclass, KW_ONLY

@dataclass
class FetchOptions:
    url: str
    _: KW_ONLY
    timeout: int = 30
    retries: int = 3
    verify_ssl: bool = True
    backoff: float = 1.5
```

Callers must pass `timeout=`, `retries=`, etc. by name.

**Heuristic:** the first one or two params can be positional (the "thing" the function operates on). Everything else — especially optional configuration — should be keyword-only.

**For public APIs this is non-negotiable:** once a library ships positional config params, every reorder or addition is a breaking change.

## 4. Error Handling

**Impact: HIGH**

Sloppy exceptions hide bugs; good exceptions localize them. Catch specific types, validate at boundaries, preserve causality with `raise ... from`.

### 4.1 Catch Specific Exception Types

**Impact: HIGH (prevents masking unrelated bugs)**

`except Exception:` catches everything — including the bugs you wanted to see. Agents default to broad handlers because "we should be resilient"; the cost is that `KeyError` from a typo in your own code gets silently swallowed alongside the network timeout you meant to handle.

**Incorrect (bare except catches unrelated errors):**

```python
def fetch_user(user_id: str) -> User | None:
    try:
        response = http.get(f"/users/{user_id}")
        return parse_user(response.json())
    except Exception:  # catches everything — including your own bugs
        return None
```

If `parse_user` has a `KeyError` bug, this returns `None` silently. Production sees "user not found" forever; the typo is invisible.

**Correct (catch what you actually handle):**

```python
def fetch_user(user_id: str) -> User | None:
    try:
        response = http.get(f"/users/{user_id}")
    except (HTTPError, TimeoutError):
        return None
    return parse_user(response.json())  # bugs here propagate as they should
```

Now only network failures return `None`. Parsing bugs crash loudly — which is what you want during development, and what surfaces real incidents in production.

**When a broad handler is appropriate:**

- At the top of a request handler or worker loop (last line of defense)
- When you will **log and re-raise** — not swallow
- Around explicitly unsafe boundaries (untrusted user code, plugins)

```python
def handle_request(req: Request) -> Response:
    try:
        return process(req)
    except Exception as e:
        logger.exception("unhandled error in request handler")
        raise  # don't swallow — let the framework return 500
```

**Create specific exception types for domain failures:**

```python
class ToolExecutionError(Exception): ...
class ToolTimeoutError(ToolExecutionError): ...
class ToolValidationError(ToolExecutionError): ...

try:
    result = run_tool(tool, args)
except ToolTimeoutError:
    retry()
except ToolValidationError as e:
    return report_invalid(e)
```

Specific exception classes make handlers self-documenting and enable different handling per failure mode.

### 4.2 Consolidate try/except Blocks with the Same Handler

**Impact: MEDIUM-HIGH (reduces duplication and simplifies control flow)**

When multiple adjacent operations raise the same exception and need the same handling, merge them into one block. Separate blocks duplicate the handler — and if the handling logic ever changes, you now need to update N places.

**Incorrect (three blocks, three copies of the same handler):**

```python
def load_config(path: Path) -> Config | None:
    try:
        raw = path.read_text()
    except FileNotFoundError:
        logger.warning("config missing: %s", path)
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("config invalid json: %s", path)
        return None

    try:
        return Config(**data)
    except ValidationError:
        logger.warning("config validation failed: %s", path)
        return None
```

Three copies of "log and return None." Changing the log level, adding a metric, or switching return value means editing three places.

**Correct (one block, one handler):**

```python
def load_config(path: Path) -> Config | None:
    try:
        raw = path.read_text()
        data = json.loads(raw)
        return Config(**data)
    except (FileNotFoundError, json.JSONDecodeError, ValidationError) as e:
        logger.warning("config load failed: %s (%s)", path, e)
        return None
```

One block, one handler, one place to change. The caller sees the same behavior; the implementation is simpler.

**When to keep blocks separate:**

- Different exceptions need **different** handling (log-and-return vs. retry vs. re-raise)
- Intermediate values matter for the handler (you want the partial result when the second step fails)
- The blocks are far apart in the function (folding them together would nest too much)

**Use `contextlib.suppress` for trivial "ignore the error" cases:**

```python
from contextlib import suppress

def try_cleanup(path: Path) -> None:
    with suppress(FileNotFoundError):
        path.unlink()
```

Cleaner than a full try/except for the "best effort, doesn't matter if it fails" pattern.

### 4.3 Inherit New Exceptions from Existing Base Exceptions

**Impact: MEDIUM-HIGH (preserves backward compatibility for callers)**

When adding a new exception type to a module that already has an exception hierarchy, inherit from the relevant base. Callers that catch the base will continue to catch the new type; skipping the base forces every caller to add a new `except` branch.

**Incorrect (new exception inherits from Exception directly):**

```python
class ToolError(Exception): ...
class ToolTimeoutError(ToolError): ...
class ToolValidationError(ToolError): ...

# New failure mode added in v2:
class ToolRateLimitError(Exception):  # doesn't inherit from ToolError
    ...

# Existing caller:
try:
    run_tool(t, args)
except ToolError:  # no longer catches ToolRateLimitError
    retry()
```

The existing `except ToolError:` no longer catches the new error. Every caller must be updated — a silent breaking change.

**Correct (inherit from the existing base):**

```python
class ToolError(Exception): ...
class ToolTimeoutError(ToolError): ...
class ToolValidationError(ToolError): ...
class ToolRateLimitError(ToolError):  # fits the hierarchy
    ...

# Existing caller still works:
try:
    run_tool(t, args)
except ToolError:  # catches ToolRateLimitError too
    retry()
```

Callers that want to handle rate limits specifically can add `except ToolRateLimitError:` — but existing broad handlers keep working.

**Design the hierarchy deliberately:**

```python
class PackageError(Exception): ...            # root for everything the package raises
class UserError(PackageError): ...            # user-correctable
class ConfigError(UserError): ...
class UsageError(UserError): ...
class SystemError(PackageError): ...          # environmental / transient
class NetworkError(SystemError): ...
class TimeoutError(SystemError): ...
```

Callers can catch at whichever level of specificity they need. Adding new subtypes is non-breaking.

**Don't invert the hierarchy:** `class TimeoutError(PackageError)` is fine; `class PackageError(TimeoutError)` is nonsense. The base is the broader category, subclasses are narrower.

**Use `__init_subclass__` or explicit checks** if you need to prevent direct instantiation of the base — keep the type system as the contract enforcement.

### 4.4 Trust Validated State — Skip Redundant Defensive Checks

**Impact: MEDIUM (removes clutter and improves resilience)**

Once a value has been validated at the boundary, internal code should trust it. Agents tend to add defensive checks "just in case" deep inside the call chain — the cost is noise, false branches, and the impression that validation elsewhere isn't reliable.

**Incorrect (re-checking already-validated state):**

```python
def fulfill_order(order: ValidatedOrder) -> None:
    if order is None:             # already enforced by type
        raise ValueError("order required")
    if not order.items:           # already enforced by Pydantic validator
        raise ValueError("order must have items")
    if order.total < 0:           # already enforced by validator
        raise ValueError("total must be non-negative")

    for item in order.items:
        process(item)
```

Every one of these checks was already done when `ValidatedOrder` was constructed. Repeating them says "I don't trust the validation."

**Correct (trust the invariants):**

```python
def fulfill_order(order: ValidatedOrder) -> None:
    for item in order.items:
        process(item)
```

Cleaner, faster, and if the validator changes, this function doesn't need updating.

**When defensive checks are appropriate:**

- At trust boundaries (first function to touch external data)
- Around code paths that can bypass the validator (direct construction in tests, deserialization shortcuts)
- When the invariant is load-bearing and a bug elsewhere could silently violate it (use `assert` to document)

```python
def fulfill_order(order: ValidatedOrder) -> None:
    assert order.items, "ValidatedOrder must have items (validator guarantees this)"
    # assertion documents the invariant; runs in dev, stripped in production
    for item in order.items:
        process(item)
```

**Use defaults instead of assertions** when the goal is resilience rather than catching bugs:

```python
# defensive, resilient — use when the system should keep running
timeout = config.timeout if config.timeout > 0 else DEFAULT_TIMEOUT

# defensive, strict — use when a zero timeout means someone messed up
assert config.timeout > 0, "timeout must be positive"
```

Pick based on whether you want the system to fail or to fall back. Don't do both.

### 4.5 Use !r Format for Identifiers in Error Messages

**Impact: MEDIUM (produces consistent, unambiguous messages)**

`{name!r}` calls `repr(name)` — producing `'foo'` instead of `foo`, `42` instead of `42`, `None` instead of nothing. Use it for identifiers (names, paths, IDs) in error messages so values are clearly delimited and edge cases (empty strings, whitespace-only names, `None`) render visibly.

**Incorrect (ambiguous formatting):**

```python
raise ValueError(f"Tool {tool_name} not found in registry")
# "Tool  not found in registry" — did tool_name have leading/trailing spaces? was it empty?
# "Tool None not found in registry" — was the literal string "None" or actual None?
```

**Correct (`!r` delimits and disambiguates):**

```python
raise ValueError(f"Tool {tool_name!r} not found in registry")
# "Tool '' not found in registry"      — clearly empty string
# "Tool 'my tool' not found in registry" — spaces visible
# "Tool None not found in registry"    — unambiguously the None sentinel
```

Quotes frame the value. `None`, numbers, and special types render with their `repr` — always unambiguous.

**Apply consistently:**

- **Names, IDs, paths:** `!r`
- **Numeric counts:** plain `{}` (e.g., `f"retrying {count} times"`)
- **Prose:** plain `{}`

```python
raise ValueError(f"tool {name!r} failed after {retries} retries")
raise FileNotFoundError(f"config not found at {path!r}")
raise KeyError(f"unknown key {key!r} in {registry_name!r}")
```

**When backticks are preferable:** some codebases use Markdown-style backticks for user-facing messages (CLI output, log lines humans read). Pick one convention per project and stick to it. `!r` is usually right for Python exception messages; backticks are usually right for log strings rendered in docs or notebooks.

### 4.6 Use assert for Invariants, Not RuntimeError

**Impact: MEDIUM-HIGH (documents assumptions and fails fast in development)**

`assert` documents "this can't happen" — and fails loudly in development if it does. `RuntimeError("internal error")` obscures the intent and fires the same in production, making programming errors look like runtime issues. Reserve exceptions for conditions the caller can reasonably respond to.

**Incorrect (RuntimeError for impossible state):**

```python
def process_step(step: Step) -> Result:
    match step:
        case InitStep():  return init()
        case RunStep():   return run()
        case DoneStep():  return done()

    raise RuntimeError("unexpected step")  # shouldn't be reachable if types are right
```

If a new `Step` variant is added and this function isn't updated, `RuntimeError("unexpected step")` fires in production. It looks like a runtime problem — but it's a coding error the type system should have caught.

**Correct (assert_never for exhaustiveness; assert for invariants):**

```python
from typing import assert_never

def process_step(step: Step) -> Result:
    match step:
        case InitStep(): return init()
        case RunStep():  return run()
        case DoneStep(): return done()
        case _: assert_never(step)  # type error at check time if new variant added
```

`assert_never(step)` is specifically designed for this — the checker will raise a type error if `Step` grows a new variant and the match isn't updated.

**Use `assert` for preconditions the checker can't express:**

```python
def binary_search(items: list[int], target: int) -> int:
    assert items == sorted(items), "binary_search requires sorted input"
    ...
```

This fails fast in development; in production with `-O`, asserts are stripped — which is appropriate because by then the invariant is trusted.

**When to raise an exception instead:**

- The caller could reasonably recover (`FileNotFoundError`, `ValidationError`)
- The input came from an untrusted boundary (user input, external API)
- The failure mode is meaningful to the caller (`PermissionError`, `TimeoutError`)

**When to `assert`:**

- "This can't happen if the rest of the code is correct"
- Internal invariants the checker can't fully enforce
- Sanity checks during development

If the condition *can* happen, make it a real exception with a meaningful type. If it genuinely shouldn't happen, `assert` it.

### 4.7 Use raise ... from to Preserve Exception Causality

**Impact: MEDIUM (keeps the original traceback visible for debugging)**

When you catch one exception and raise another, include `from original` to preserve the chain. Without it, the traceback prints "During handling of the above exception, another exception occurred" — which is usually right, but the explicit form is clearer and survives `__cause__` suppression in some runtimes.

**Incorrect (original exception lost or implicit):**

```python
def load_config(path: Path) -> Config:
    try:
        raw = path.read_text()
    except FileNotFoundError:
        raise ConfigError(f"config missing: {path}")  # loses the original FileNotFoundError context
```

The traceback will still show both — Python implicitly sets `__context__` — but the intent isn't explicit, and `__cause__` is `None`, which some tools use to distinguish "we meant this chain" vs. "an error happened while handling."

**Correct (explicit `raise ... from`):**

```python
def load_config(path: Path) -> Config:
    try:
        raw = path.read_text()
    except FileNotFoundError as e:
        raise ConfigError(f"config missing: {path}") from e
```

The traceback prints "The above exception was the direct cause of the following exception" — a deliberate chain. `__cause__` is set, so programmatic handlers and logging can walk the chain cleanly.

**Use `from None` to suppress the context:**

When the original exception is genuinely internal and the caller shouldn't see it:

```python
def parse_timestamp(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        raise ValueError(f"invalid timestamp: {s!r}") from None
```

The user-facing error is clean (`ValueError: invalid timestamp: 'abc'`) without the implementation's internal `ValueError: Invalid isoformat string:`.

**Three patterns:**

- `raise NewError() from original` — explicit chain; `__cause__` set
- `raise NewError()` inside `except` — implicit chain; `__context__` set
- `raise NewError() from None` — suppress the original context entirely

Default to `from original` when translating between exception types. Reach for `from None` when the internal cause is noise to the caller.

### 4.8 Validate Input at System Boundaries

**Impact: HIGH (fails fast and prevents bad data from spreading)**

Validate once, at the edge — not repeatedly in every internal function. Agents tend to sprinkle defensive checks throughout the call chain "in case something got through." Push validation to the boundary (API handler, CLI entrypoint, deserialization), then trust the validated value.

**Incorrect (validation scattered through every internal function):**

```python
def process_order(order_id: str) -> None:
    if not order_id:
        raise ValueError("order_id required")
    order = load_order(order_id)
    fulfill(order)

def load_order(order_id: str) -> Order:
    if not order_id:  # checked again
        raise ValueError("order_id required")
    ...

def fulfill(order: Order) -> None:
    if not order.id:  # and again
        raise ValueError("order has no id")
    ...
```

Every internal function re-validates. If the validation rule changes (e.g., order IDs must match a pattern), every copy must change.

**Correct (validate at entry; trust internally):**

```python
# boundary: the API handler
def handle_fulfill_request(req: Request) -> Response:
    try:
        body = FulfillRequest.model_validate(req.json())  # Pydantic does the work
    except ValidationError as e:
        return error_response(400, str(e))

    process_order(body.order_id)
    return success_response()

# internal: takes a validated value, trusts it
def process_order(order_id: OrderId) -> None:
    order = load_order(order_id)
    fulfill(order)
```

One validation point. Internal code takes `OrderId` (a branded `NewType`) and trusts it — the validation already happened.

**Boundaries that need validation:**

- HTTP request parsing (headers, path params, query strings, body)
- CLI argument parsing
- Reading files or database rows that originated outside the system
- Message queue consumers
- Foreign API responses

**Heuristic:** data at a boundary is untrusted. Validate it into a typed model (Pydantic, dataclass with a validator, `NewType` + explicit check). Once validated, the typed model flows through internal code unchecked.

**Fail fast:** validate before expensive operations. Don't read a 10MB file, parse it, and *then* reject it for missing a required field — check the field first.

## 5. Code Simplification

**Impact: MEDIUM-HIGH**

Python idioms that reduce LOC and mental load. Comprehensions, `any()`/`all()`, early returns, removing dead code. The rules that let Python read like Python.

### 5.1 Extract Helpers After 2+ Occurrences

**Impact: MEDIUM-HIGH (prevents divergent implementations of the same logic)**

The first copy of a piece of logic is fine. The second copy is the point of decision: extract now, or accept drift later. Agents tend to copy-paste a third time because "extracting is a bigger change"; the cost is bugs where two copies evolved in subtly different directions.

**Incorrect (same logic duplicated across handlers):**

```python
def handle_stream(stream: AsyncIterator[Chunk]) -> Response:
    collected = []
    async for chunk in stream:
        if chunk.kind == "text":
            collected.append(chunk.text)
        elif chunk.kind == "tool":
            collected.append(format_tool(chunk))
    return Response(content="".join(collected))

def handle_non_stream(response: RawResponse) -> Response:
    collected = []
    for chunk in response.chunks:
        if chunk.kind == "text":
            collected.append(chunk.text)
        elif chunk.kind == "tool":
            collected.append(format_tool(chunk))
    return Response(content="".join(collected))
```

Two copies of the chunk-formatting logic. A new chunk kind gets added — two places need updates. One gets missed, and the streaming handler silently produces different output than the non-streaming one.

**Correct (extract once, use twice):**

```python
def _format_chunk(chunk: Chunk) -> str:
    match chunk.kind:
        case "text": return chunk.text
        case "tool": return format_tool(chunk)
        case _: return ""

async def handle_stream(stream: AsyncIterator[Chunk]) -> Response:
    parts = [_format_chunk(c) async for c in stream]
    return Response(content="".join(parts))

def handle_non_stream(response: RawResponse) -> Response:
    parts = [_format_chunk(c) for c in response.chunks]
    return Response(content="".join(parts))
```

Now a new chunk kind means one change. The two handlers can't drift apart.

**When NOT to extract:**

- The two occurrences look similar but serve genuinely different purposes — premature abstraction locks them together
- The shared logic is 2-3 trivial lines and naming a helper is more noise than value
- Each caller would need the helper to accept so many optional parameters that it becomes a mode-switch

**Heuristic: "rule of three" is a safe default, but lean toward earlier extraction** when the logic encodes a domain rule (validation, formatting, permissions) that must stay consistent.

**Location of the helper:**

- Private (`_name`) in the same module if it's specific to that module
- Module-level utility if multiple modules share it
- Base class method if it's a shared class operation (`data-explicit-variants`)

### 5.2 Flatten Nested if Statements Into and Conditions

**Impact: LOW-MEDIUM (reduces indentation and improves readability)**

When nested `if` statements share the same body and have no intervening code, collapse them into a single `if` with `and`. The nested form implies the branches do something different; when they don't, the structure lies.

**Incorrect (nested if with no intervening code):**

```python
def should_notify(user: User, event: Event) -> bool:
    if user.is_active:
        if user.notifications_enabled:
            if event.priority >= user.notification_threshold:
                return True
    return False
```

Four indentation levels, three conditions, and nothing happening between them.

**Correct (combined into one condition):**

```python
def should_notify(user: User, event: Event) -> bool:
    return (
        user.is_active
        and user.notifications_enabled
        and event.priority >= user.notification_threshold
    )
```

One expression. The reader sees all conditions together.

**When nesting IS the right structure:**

- Each branch does genuinely different work
- Intermediate logging, validation, or early returns happen between checks
- The checks share a branch in only some cases

```python
# keep this nested — the branches do different things
if user.is_active:
    log_seen(user)
    if user.notifications_enabled:
        send_notification(user, event)
    else:
        queue_digest(user, event)
```

Not every chain of checks flattens. The rule is: *if every nested branch only holds another `if` until the final body, flatten*.

**Early-return flattening:**

```python
# also nested
def handle(request):
    if request.authenticated:
        if request.authorized:
            return process(request)

# flattened with guards
def handle(request):
    if not request.authenticated:
        return None
    if not request.authorized:
        return None
    return process(request)
```

Either form is fine; guard-clause style often reads cleaner when the happy path is the "bottom" of the function.

### 5.3 Inline Single-Use Intermediate Variables

**Impact: LOW-MEDIUM (reduces noise and indirection)**

When a variable is assigned once and used once immediately after, inlining it removes a name that doesn't earn its keep. Agents tend to introduce `_filtered`, `_cleaned`, `_copy` intermediates "for clarity" — but the clarity is usually from the name, and if the name isn't informative, the variable is just noise.

**Incorrect (intermediates that add nothing):**

```python
def top_admins(users: list[User], limit: int) -> list[User]:
    filtered_users = [u for u in users if u.is_admin]
    sorted_users = sorted(filtered_users, key=lambda u: u.rank)
    result = sorted_users[:limit]
    return result
```

Four lines, four names — each used exactly once. The names restate the operations, not the purpose.

**Correct (inline when the operation is its own explanation):**

```python
def top_admins(users: list[User], limit: int) -> list[User]:
    return sorted(
        (u for u in users if u.is_admin),
        key=lambda u: u.rank,
    )[:limit]
```

Four operations, zero intermediate names. Each step's intent is visible in place.

**When an intermediate variable earns its place:**

- The name adds genuine information the expression doesn't convey
- The value is used more than once
- The expression would be too long to read as one unit
- Debugging benefits from a named step (breakpoints, logging)

```python
# the name "eligible" adds information the expression doesn't
def distribute_bonuses(users: list[User], amount: Decimal) -> None:
    eligible = [u for u in users if u.tenure_months >= 12 and not u.on_leave]
    share = amount / len(eligible)
    for user in eligible:
        pay_bonus(user, share)
```

Here `eligible` is used twice and the name documents the business rule. Keep it.

**Heuristic:** if you can't give the intermediate a name more meaningful than a restatement of the operation, inline it.

### 5.4 Remove Commented-Out and Dead Code

**Impact: MEDIUM (reduces confusion about intent)**

Commented-out code, superseded implementations, unused imports, and definitions nothing calls — delete them. Version control preserves history; dead code in the file confuses readers about which implementation is actually active.

**Incorrect (commented alternatives and stale code):**

```python
def fetch_user(user_id: str) -> User:
    # Old implementation:
    # response = requests.get(f"/users/{user_id}")
    # return User(**response.json())

    response = http_client.get(f"/users/{user_id}")
    return User.model_validate(response.json())

    # TODO: switch to async version once available
    # async def fetch_user(user_id): ...

def _unused_helper(x: int) -> int:  # nothing calls this
    return x * 2
```

Readers wonder: is the commented version the fallback? Is the TODO still accurate? Is `_unused_helper` called dynamically somewhere I'm missing?

**Correct (delete; let git remember):**

```python
def fetch_user(user_id: str) -> User:
    response = http_client.get(f"/users/{user_id}")
    return User.model_validate(response.json())
```

If you need the old implementation back, `git log` has it.

**Targets to delete:**

- Commented-out blocks of code
- Functions, methods, classes that nothing calls (verify with grep across the codebase first)
- Unused imports (`ruff` or `pyflakes` finds these)
- Unused variables
- Dead branches (if a condition can never be true)
- `print()` statements left over from debugging
- Commented-out log lines

**When to keep what looks like dead code:**

- Called dynamically (by name, via `getattr`, via a registry)
- Part of a public API contract that external callers may use
- Intentionally present for future use, with a TODO that links to a tracking issue

**For "intentional TODOs," link to the tracking issue:**

```python
# TODO(ISSUE-123): switch to async http_client when the migration lands
```

A TODO with a link is a commitment. A TODO without one is a wish.

### 5.5 Return Early to Flatten Control Flow

**Impact: MEDIUM (keeps the happy path unnested and readable)**

When a function has preconditions to check, return as soon as one fails. Agents tend to write deeply nested "if valid, if authorized, if ..." pyramids — the happy path ends up buried five levels in. Guard clauses flatten the structure and make the happy path the most visible branch.

**Incorrect (pyramid of nesting):**

```python
def process_request(req: Request) -> Response:
    if req.authenticated:
        if req.authorized:
            if req.body is not None:
                if req.body.is_valid:
                    return do_process(req.body)
                else:
                    return error(400, "invalid body")
            else:
                return error(400, "missing body")
        else:
            return error(403, "forbidden")
    else:
        return error(401, "unauthenticated")
```

The actual work — `do_process(req.body)` — is the innermost line. Every error case has to be read to get there.

**Correct (guard clauses, happy path at the end):**

```python
def process_request(req: Request) -> Response:
    if not req.authenticated:
        return error(401, "unauthenticated")
    if not req.authorized:
        return error(403, "forbidden")
    if req.body is None:
        return error(400, "missing body")
    if not req.body.is_valid:
        return error(400, "invalid body")

    return do_process(req.body)
```

Each precondition is handled and dismissed. The happy path is unindented, at the bottom, easy to find.

**Works the same for loops:**

```python
# pyramid
for item in items:
    if item.active:
        if item.ready:
            process(item)

# flattened
for item in items:
    if not item.active:
        continue
    if not item.ready:
        continue
    process(item)
```

**When to keep the `else`:**

- The two branches do comparable work (not "error vs. success")
- The function is short enough that nesting doesn't obscure the structure

```python
# fine — short, parallel branches
def classify(n: int) -> str:
    if n > 0:
        return "positive"
    elif n < 0:
        return "negative"
    else:
        return "zero"
```

**Rule of thumb:** if you're checking "is this valid?" and returning an error on the no-branch, guard-clause it. If you're splitting between two equal outcomes, `if/else` is fine.

### 5.6 Use @cached_property for Expensive Derived Attributes

**Impact: MEDIUM (defers computation and avoids recomputation)**

When an attribute is computed from other fields, is expensive, and doesn't change over the object's lifetime, `@cached_property` is the right tool. It defers computation until first access and caches the result — avoiding both wasted work when the attribute is never used and repeated work when it's used many times.

**Incorrect (plain method — recomputes on every call):**

```python
from dataclasses import dataclass

@dataclass
class Report:
    rows: list[Row]

    def summary_stats(self) -> Stats:  # expensive, called many times
        return compute_stats(self.rows)
```

Every call re-walks `self.rows`. If the caller invokes `report.summary_stats()` ten times in a function, you pay ten times.

**Incorrect (eager computation in `__post_init__`):**

```python
@dataclass
class Report:
    rows: list[Row]

    def __post_init__(self) -> None:
        self.stats = compute_stats(self.rows)  # paid even if stats never used
```

You pay at construction time whether or not the caller ever reads `stats`.

**Correct (`@cached_property` — lazy and cached):**

```python
from functools import cached_property
from dataclasses import dataclass

@dataclass
class Report:
    rows: list[Row]

    @cached_property
    def summary_stats(self) -> Stats:
        return compute_stats(self.rows)
```

First access runs `compute_stats`; subsequent accesses return the cached result from `self.__dict__`. If no caller reads `summary_stats`, no work happens.

**Caveats:**

- **Mutability:** if `self.rows` changes after the property is accessed, the cached value is stale. Use `@cached_property` only when the dependencies are effectively immutable.
- **Equality / hashing:** the cache lives in `__dict__`, so it persists across `copy()` unless you clear it. Include `compare=False` on the cache field if using dataclass comparisons.
- **`@property` is still right for cheap derivations** — accessor-like computations (`full_name`, `is_valid`) don't need caching and shouldn't use it.

**Use `functools.lru_cache` for module-level pure functions:**

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def parse_version(s: str) -> Version:
    ...
```

`@cached_property` is the instance-method equivalent.

### 5.7 Use Comprehensions Over for+append Loops

**Impact: MEDIUM-HIGH (more concise, often faster, and idiomatic Python)**

Comprehensions express "build a collection from an iterable" in one line. Agents often write C-style loops with `append()` — more code, more variables, more places for off-by-one and wrong-list bugs. Reach for a comprehension by default.

**Incorrect (imperative loop + append):**

```python
def active_usernames(users: list[User]) -> list[str]:
    result = []
    for user in users:
        if user.is_active:
            result.append(user.name)
    return result

def name_to_id(users: list[User]) -> dict[str, str]:
    mapping = {}
    for user in users:
        mapping[user.name] = user.id
    return mapping
```

**Correct (comprehensions):**

```python
def active_usernames(users: list[User]) -> list[str]:
    return [user.name for user in users if user.is_active]

def name_to_id(users: list[User]) -> dict[str, str]:
    return {user.name: user.id for user in users}
```

**Also:**

```python
# set comprehension
unique_tags = {tag for post in posts for tag in post.tags}

# generator expression (lazy — doesn't build a list in memory)
total = sum(item.price for item in items)
```

**When NOT to use a comprehension:**

- Multi-step logic that doesn't fit on one line cleanly — readability beats brevity
- Side effects (use a plain loop; comprehensions are for building collections)
- Complex conditionals with intermediate variables

```python
# too dense to read — use a loop
result = [
    process(x, key=compute_key(x, config))
    for x in items
    if x.valid and (x.priority > threshold or x.override)
]
```

Break it up when the comprehension stops reading like English.

**`any()` and `all()` over comprehensions that just reduce to a bool:**

```python
# overkill
has_admin = [u.is_admin for u in users] != []  # wrong shape entirely
has_admin = any([u.is_admin for u in users])   # builds a list first

# right
has_admin = any(u.is_admin for u in users)     # generator, short-circuits
```

### 5.8 Use any() / all() Over Boolean-Flag Loops

**Impact: MEDIUM (shorter, short-circuits, no manual flag management)**

When you're checking "does any element satisfy X?" or "do all elements satisfy X?", Python has built-ins for that. Agents sometimes write manual `found = False` / `break` patterns — more code, more bugs, no short-circuit benefit.

**Incorrect (manual flag + break):**

```python
def has_admin(users: list[User]) -> bool:
    found = False
    for user in users:
        if user.is_admin:
            found = True
            break
    return found

def all_ready(services: list[Service]) -> bool:
    for s in services:
        if not s.ready:
            return False
    return True
```

**Correct (built-ins):**

```python
def has_admin(users: list[User]) -> bool:
    return any(u.is_admin for u in users)

def all_ready(services: list[Service]) -> bool:
    return all(s.ready for s in services)
```

Both short-circuit — `any()` stops at the first truthy, `all()` stops at the first falsy.

**Pass a generator, not a list:**

```python
# wasteful — builds the full list before checking
any([expensive_check(x) for x in items])

# right — lazy generator, stops at first match
any(expensive_check(x) for x in items)
```

**Other built-ins worth remembering:**

```python
# count matches
count = sum(1 for x in items if x.valid)

# min / max with a key
cheapest = min(items, key=lambda x: x.price)

# first matching element (or None)
first_error = next((x for x in items if x.failed), None)
```

`next(generator, default)` is the Pythonic "find first or default" — more direct than a loop with an early return.

**When to use a loop instead:** when you need the loop variable for something else, the logic has side effects, or the condition is too complex to fit in a generator cleanly.

### 5.9 Use x or default for Fallback Values

**Impact: LOW-MEDIUM (more concise and idiomatic than if/else)**

For the common "use `x` if it's truthy, otherwise `default`" pattern, `x or default` beats the verbose `if`/`else`. The catch: this triggers on every falsy value (`0`, `''`, `[]`, `None`) — so only use it when those aren't semantically meaningful.

**Incorrect (verbose if/else for a simple fallback):**

```python
def display_name(user: User) -> str:
    if user.nickname:
        return user.nickname
    else:
        return user.username
```

**Correct (or-fallback):**

```python
def display_name(user: User) -> str:
    return user.nickname or user.username
```

Shorter, idiomatic, and clear.

**When `or` is WRONG:** when falsy values are semantically valid.

```python
# wrong — if count is 0, we'd return DEFAULT_COUNT instead of 0
def get_count(config: Config) -> int:
    return config.count or DEFAULT_COUNT

# right — explicit about the None case
def get_count(config: Config) -> int:
    return config.count if config.count is not None else DEFAULT_COUNT
```

Zero, empty string, empty list, and empty dict are all falsy but often meaningful. `0 retries` ≠ `default retries`. `"" name` is probably a bug but it's not the same as "name was never set."

**Use `... if ... is not None else ...` when you specifically mean "None":**

```python
timeout = config.timeout if config.timeout is not None else DEFAULT_TIMEOUT
```

**Use `... if ... else ...` when the condition is more elaborate:**

```python
label = name.strip() if name and name.strip() else "anonymous"
```

**Rule of thumb:** `or` for truthy/falsy semantics; explicit `is not None` for optional-value semantics.

## 6. Performance

**Impact: MEDIUM**

Python-specific optimizations that matter on hot paths. Module-level compilation, set/dict lookups, cached properties. Not premature — applied where the hot path is measured.

### 6.1 Build a Dict Index Instead of Nested Loops

**Impact: MEDIUM (O(n) instead of O(n²))**

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

### 6.2 Combine Filter and Map Into One Pass

**Impact: LOW-MEDIUM (one iteration instead of two or three)**

When you filter a collection and then map (or map and filter, etc.), it's often one comprehension, not two or three chained operations. Each chained step allocates an intermediate list and iterates.

**Incorrect (three passes, two intermediate lists):**

```python
def prices_for_sale_items(items: list[Item]) -> list[Decimal]:
    sale_items = [i for i in items if i.on_sale]
    discounted = [i for i in sale_items if i.discount > 0]
    prices = [i.price * (1 - i.discount) for i in discounted]
    return prices
```

Three allocations, three passes.

**Correct (one pass, one list):**

```python
def prices_for_sale_items(items: list[Item]) -> list[Decimal]:
    return [
        item.price * (1 - item.discount)
        for item in items
        if item.on_sale and item.discount > 0
    ]
```

One pass, one list. Conditions combined; mapping in the expression.

**When chaining is clearer:**

If each step has enough logic that inlining makes the comprehension hard to read, keep them separate — readability wins over a small constant-factor performance gain:

```python
# fine — each step has real logic
eligible = [normalize(u) for u in users if u.tenure_months >= 12]
grouped = group_by_team(eligible)
summaries = [compute_summary(team, members) for team, members in grouped.items()]
```

**For reductions, use the built-in that takes a generator:**

```python
# don't build a list just to sum it
total = sum([i.price for i in items if i.on_sale])

# better — generator, no intermediate list
total = sum(i.price for i in items if i.on_sale)
```

Same for `min`, `max`, `any`, `all`, `''.join(...)`.

**For complex multi-step transforms, consider `itertools.chain` or the `toolz` library** — but most of the time, one comprehension is the answer.

### 6.3 Compile Static Regex Patterns at Module Level

**Impact: MEDIUM (avoids recompilation overhead on every call)**

`re.compile()` builds a pattern object once; `re.match()` / `re.search()` on a string call it every time. For regexes that don't change, compile at module scope. The cost of recompilation in a hot loop can dwarf the actual match.

**Incorrect (recompiled on every call):**

```python
import re

def extract_version(text: str) -> str | None:
    match = re.search(r"v(\d+\.\d+\.\d+)", text)  # compiled every call
    return match.group(1) if match else None
```

`re.search` caches recent patterns internally, but for any pattern complex enough to matter, you're paying compilation cost on every invocation.

**Correct (compiled once at import):**

```python
import re

_VERSION_RE = re.compile(r"v(\d+\.\d+\.\d+)")

def extract_version(text: str) -> str | None:
    match = _VERSION_RE.search(text)
    return match.group(1) if match else None
```

The pattern is built once when the module imports; every call just uses it.

**Naming:**

- `_UPPER_CASE` for module-level private regex constants (or whatever your project's constant convention is)
- Descriptive names — `_VERSION_RE`, `_EMAIL_RE`, not `_PATTERN1`

**When compilation isn't worth hoisting:**

- The pattern is built from a runtime value (different per call)
- The function is called a small number of times total
- The pattern is truly one-shot (startup-only parsing)

Even for the truly-one-shot case, a module-level constant is usually clearer than an inline string — so the performance argument isn't the only reason to hoist.

**Related:** same pattern applies to other "build once, use many" objects — `TypeAdapter`, `json.JSONDecoder` with custom hooks, precompiled templates. Build at module scope; use at call time.

### 6.4 Define TypeAdapter Instances at Module Level

**Impact: MEDIUM (avoids repeated schema construction)**

`pydantic.TypeAdapter` does real work on construction — it builds the validation schema for the target type. Inside a hot function, every call rebuilds it. Create it once at module scope and reuse.

**Incorrect (rebuilt on every call):**

```python
from pydantic import TypeAdapter

def parse_users(raw: bytes) -> list[User]:
    adapter = TypeAdapter(list[User])  # schema built every call
    return adapter.validate_json(raw)
```

Schema construction for `list[User]` involves walking the `User` class, resolving annotations, and building the validation tree. Doing it per call is pure waste.

**Correct (module-level constant):**

```python
from pydantic import TypeAdapter

_USERS_ADAPTER: TypeAdapter[list[User]] = TypeAdapter(list[User])

def parse_users(raw: bytes) -> list[User]:
    return _USERS_ADAPTER.validate_json(raw)
```

Schema built once at import; every call just runs the validator.

**Same applies to:**

- `json.JSONDecoder` with custom hooks
- `msgpack.Packer` / `Unpacker` with configuration
- Cached serializers, compiled templates, precomputed lookup structures
- Anything whose constructor does real work

**Naming:**

```python
_USERS_ADAPTER = TypeAdapter(list[User])
_CONFIG_ADAPTER = TypeAdapter(AppConfig)
_EVENT_ADAPTER: TypeAdapter[Event] = TypeAdapter(Event)
```

Module-level private (`_`-prefix), uppercase if you treat module constants as uppercase. Type annotation is optional but helpful for generic adapters.

**When the adapter type depends on runtime values:**

If you need different adapters for different inputs, cache them:

```python
from functools import cache

@cache
def _adapter_for(model_type: type) -> TypeAdapter:
    return TypeAdapter(model_type)
```

Now each distinct `model_type` gets its adapter built once.

### 6.5 Use Generators for Streaming Iteration

**Impact: MEDIUM (constant memory instead of O(n))**

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

### 6.6 Use Tuple Syntax in isinstance() Checks

**Impact: LOW (tuple syntax is measurably faster than union syntax)**

`isinstance(x, (A, B, C))` and `isinstance(x, A | B | C)` both work. The tuple form is faster at runtime because the union form constructs a `types.UnionType` every call. For hot paths, prefer the tuple.

**Incorrect (union syntax has allocation overhead):**

```python
def is_primitive(x: object) -> bool:
    return isinstance(x, int | float | str | bool)  # builds a union type each call
```

**Correct (tuple has no per-call overhead):**

```python
def is_primitive(x: object) -> bool:
    return isinstance(x, (int, float, str, bool))
```

Both forms are semantically equivalent. The tuple version is faster because Python constructs the union type on every call (in older versions) or does extra work comparing against it (in newer versions).

**When the difference matters:**

- Called many times per second in a hot path
- Inside a tight inner loop

**When it doesn't matter:**

- Called a few times per request
- Rare code paths

**Note on annotations vs. runtime checks:** the union syntax (`X | Y`) is idiomatic in type annotations and has zero cost there (annotations aren't evaluated at runtime with `from __future__ import annotations`). The tuple form is only better for the specific case of `isinstance()` calls — other places `X | Y` appears, prefer the union syntax.

**Apply consistently** — it's a simple swap, and codebases that use both forms interchangeably make profiling results less predictable. Pick the tuple form once for all `isinstance` checks and move on.

### 6.7 Use functools.lru_cache for Pure Functions

**Impact: MEDIUM (trades memory for CPU on repeatable computations)**

When a function is pure (same input → same output, no side effects) and called repeatedly with the same arguments, `@lru_cache` caches the result so subsequent calls are free. Agents often forget this exists and either hand-roll a dict cache or eat the recomputation cost.

**Incorrect (recomputing the same answer):**

```python
def parse_version(version_str: str) -> Version:
    # called from many call sites, often with the same string
    return Version.parse(version_str)
```

If 100 call sites ask `parse_version("1.2.3")`, you parse it 100 times.

**Correct (cached):**

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def parse_version(version_str: str) -> Version:
    return Version.parse(version_str)
```

First call parses and stores; subsequent calls return the cached `Version`. `maxsize` caps the cache to 256 entries (LRU eviction).

**`functools.cache` (Python 3.9+) for unbounded:**

```python
from functools import cache

@cache
def load_schema(name: str) -> Schema:
    return Schema.from_file(SCHEMA_DIR / f"{name}.json")
```

No size limit. Good when the key space is naturally small (like schema names) and entries are expensive to build.

**Requirements:**

- Arguments must be **hashable** (no mutable lists, dicts, or sets as args)
- Function must be **pure** — same inputs produce the same output
- No side effects that callers depend on happening each call

**When NOT to cache:**

- Arguments are unhashable (convert to tuple first, or use a different strategy)
- The function has meaningful side effects (logging, writes)
- The key space is unbounded and entries are large (cache grows without limit)
- The computation is cheap and the call frequency is low

**Hand-rolled caches:**

If `@lru_cache` doesn't fit (unhashable args, multi-level keys, time-based invalidation), build a module-level `dict` cache — but name it clearly and document the invalidation strategy. Uncontrolled hand-rolled caches leak memory.

**For instance methods, prefer `@cached_property`** when the "arguments" are just `self` — see `simplify-cached-property`.

### 6.8 Use set for Repeated Membership Checks

**Impact: MEDIUM (O(1) beats O(n))**

`x in some_list` scans the list every time — O(n). `x in some_set` is a hash lookup — O(1). When you're checking membership repeatedly against the same collection, the set conversion pays for itself quickly.

**Incorrect (list membership in a loop):**

```python
def filter_allowed(items: list[Item], allowed: list[str]) -> list[Item]:
    return [item for item in items if item.id in allowed]
```

For each of `len(items)` checks, `in allowed` scans the whole list. If both are 10k, that's 100M comparisons.

**Correct (convert once, check many):**

```python
def filter_allowed(items: list[Item], allowed: list[str]) -> list[Item]:
    allowed_set = set(allowed)
    return [item for item in items if item.id in allowed_set]
```

Conversion is O(n); each `in` check is O(1). Total: O(n + m) instead of O(n × m).

**When to use `frozenset`:**

Module-level constants with fixed membership — can't be modified accidentally, hashable so it can be used as a dict key:

```python
_ADMIN_ROLES: frozenset[str] = frozenset({"admin", "owner", "superuser"})

def is_admin(role: str) -> bool:
    return role in _ADMIN_ROLES
```

**When NOT to convert to set:**

- Only checking membership once (conversion costs more than the scan)
- The collection is tiny (under ~10 elements) — list scan is competitive
- Order matters and you need the list semantics

**For lookups by key (not just membership), use a dict:**

```python
# bad — scanning a list for "the one with this id"
user = next((u for u in users if u.id == target_id), None)

# good — build once, look up many
users_by_id = {u.id: u for u in users}
user = users_by_id.get(target_id)
```

Same asymptotic improvement as set membership, and you get the associated value instead of just a boolean.

## 7. Naming

**Impact: MEDIUM**

Names are the most-read interface in any codebase. Specific over generic, consistent terminology, no type suffixes that duplicate annotations.

### 7.1 Avoid Redundant Type Suffixes in Names

**Impact: LOW-MEDIUM (reduces noise when types annotate types)**

`user_list: list[User]`, `config_dict: dict[str, str]`, `name_str: str` — the suffix repeats what the type annotation already says. Python has type annotations; let them do the work. Agents default to Hungarian-style naming because "it makes the type clear" — the type is right there.

**Incorrect (suffix restates the type):**

```python
def filter_users(user_list: list[User], active_dict: dict[str, bool]) -> list[User]:
    name_str = user_list[0].name_str
    result_list: list[User] = []
    ...
```

Every name repeats its type. The code is harder to read because the meaningful word is buried.

**Correct (let types speak):**

```python
def filter_users(users: list[User], active_by_id: dict[str, bool]) -> list[User]:
    name = users[0].name
    result: list[User] = []
    ...
```

`users` and `active_by_id` describe what the value is for; the types describe the shape.

**Suffixes to drop:**

- `_list`, `_dict`, `_set`, `_tuple` — shape is in the type
- `_str`, `_int`, `_float`, `_bool` — primitive type is in the type
- `Value`, `Type`, `Class` — usually redundant (`UserType` vs. just `User`)

**When a type-ish suffix genuinely helps:**

- `_by_key` names signal the dict's key (`users_by_id`, `posts_by_author`)
- `_count`, `_index`, `_id` signal the semantic role, not the type
- `_bytes` / `_str` on a variable that could be either (`body_bytes` vs. `body_text`) — disambiguating two valid forms is useful

**Class names:** don't suffix with `Class`. `UserClass` is just `User`. The definition is `class User:`.

**Enum values:** keep them short and meaningful. `Color.RED` reads better than `Color.COLOR_RED`.

**Private helpers:** same rule applies. `_parse_user_dict` where the return is `dict[str, User]` — just `_parse_users`.

**Exception classes:** convention is to end with `Error` (`ValidationError`, `TimeoutError`). This is the established Python pattern and worth keeping.

### 7.2 Drop Redundant Prefixes When Context Is Clear

**Impact: MEDIUM (reduces noise and improves readability)**

When a field is accessed as `tool_config.tool_description`, the `tool_` prefix adds nothing — the class name already provides that context. Agents tend to repeat the class name in every field ("just to be clear") — the result is noise that makes real information harder to find.

**Incorrect (prefix repeats the class context):**

```python
from dataclasses import dataclass

@dataclass
class ToolConfig:
    tool_name: str
    tool_description: str
    tool_version: str
    tool_timeout: float
```

Every access reads `config.tool_name`, `config.tool_description`. The `tool_` adds zero information.

**Correct (name without the redundant prefix):**

```python
@dataclass
class ToolConfig:
    name: str
    description: str
    version: str
    timeout: float
```

Now `config.name`, `config.description` — shorter and just as clear.

**The rule:** drop the prefix when the class, module, or variable name already establishes the context.

**Examples from real codebases:**

```python
# before → after
server.server_label       → server.label
mcp_server.mcp_version    → mcp_server.version   (or just version on the class)
user_profile.user_id      → user_profile.user_id (probably keep — "id" alone is too generic)
```

The last example is a judgment call. `user_profile.id` would be unambiguous in context, but `user_id` reads well when passing it around as a variable. Lean toward dropping when it's a *field on* a class, keep the prefix when the value *travels as* a parameter.

**When to keep a prefix:**

- The field is a **foreign key** to another entity (`user_id` on a `Post`, `author_id` on a `Comment`) — the prefix signals what it points to
- Two related fields share a type and need disambiguation (`created_at` vs. `updated_at`)
- Dropping the prefix makes the name ambiguous (`format` could mean many things; `date_format` is specific)

**Be consistent:** whatever you pick, apply it uniformly across sibling fields. `tool_name` with `description` (mixed) reads worse than either all-prefixed or all-bare.

### 7.3 Rename When Behavior Changes

**Impact: MEDIUM (prevents misleading names from hiding behavior changes)**

A function's name is a promise about what it does. When the behavior changes — wider scope, different return type, side effects added — the old name lies. Agents tend to keep names stable because "it's a smaller diff"; the cost is that every reader now has to figure out that the name is wrong.

**Incorrect (name no longer matches behavior):**

```python
# v1: called only for function tools
def _call_function_tool(tool: FunctionTool, args: dict) -> Result:
    return tool.invoke(args)

# v2: extended to handle output tools too, but name unchanged
def _call_function_tool(tool: FunctionTool | OutputTool, args: dict) -> Result:
    if isinstance(tool, FunctionTool):
        return tool.invoke(args)
    return tool.build_output(args)  # wait, this isn't a "function tool"
```

Every reader now has to re-learn what `_call_function_tool` means. The name says "function tool"; the body says "any tool."

**Correct (rename to reflect the wider scope):**

```python
def _call_tool(tool: FunctionTool | OutputTool, args: dict) -> Result:
    if isinstance(tool, FunctionTool):
        return tool.invoke(args)
    return tool.build_output(args)
```

Name matches behavior again.

**Signals that a rename is due:**

- The function's scope expanded (handles more types, more cases)
- The return type changed substantively
- Side effects were added or removed
- The function's "level" changed (was a leaf, now orchestrates; was a command, now a query)

**When in-place rename is fine:**

- Private (`_`-prefixed) functions — callers are all internal, update them
- Internal helpers with a small number of call sites

**When rename needs a migration:**

- Public API — add the new name, keep the old as a deprecated alias (see `api-deprecated-aliases`)
- Widely-used internal helpers — IDE-assisted rename is safer than hand-edit

**For method renames across a class hierarchy** — use the `@override` decorator when the intent is to override, and let the checker catch stragglers:

```python
from typing import override

class MemoryToolset(Toolset):
    @override
    def list_tools(self) -> list[Tool]: ...
```

If `Toolset` renames `list_tools`, `@override` makes the subclass fail type-checking until updated.

### 7.4 Use Consistent Terminology Across Code and Docs

**Impact: MEDIUM (prevents fragmented searches and user confusion)**

When the same concept appears as `message` in one module, `last_message` in another, and `latest` in a third, readers can't grep. Pick one term per concept and use it everywhere — in code, docstrings, error messages, and external docs.

**Incorrect (same concept, three names):**

```python
# module_a.py
def get_last_message(session): ...

# module_b.py
def fetch_latest(session): ...

# module_c.py
def current_message(session): ...

# error message
raise ValueError("no recent message found")
```

A user searching for "latest message" in code finds one match; in docs, another; in error messages, a third. The concept is fragmented.

**Correct (one term, everywhere):**

```python
# everywhere
def get_latest_message(session): ...
raise ValueError("no latest message found")
# docs: "The latest message is..."
```

One word per concept. Search works.

**Choose deliberately — and write it down:**

- `latest` vs. `last` vs. `most_recent` — pick one
- `message` vs. `msg` — pick one
- `tool` vs. `function` vs. `capability` — pick one
- `user` vs. `account` vs. `member` — pick one

If the codebase has a `GLOSSARY.md` or `CONTRIBUTING.md`, list the canonical terms and their boundaries. If not, pick through current usage by grepping — whichever is most common wins.

**When different terms are genuinely different things:**

Sometimes "message" and "msg" mean different things (a full message object vs. a short string body). That's fine — but then the distinction should be explicit and documented. If you need two terms, you need two concepts.

**Refactoring legacy inconsistency:**

- Add the canonical alias first, deprecate the old
- Update docstrings and error messages in the same PR
- Don't let PRs introduce new variants (`message`, `msg`, `messageObj` in one diff) — pick one, stick to it

**Why it matters:** users grep. Docs search. Error messages end up in Stack Overflow questions. When terminology fragments, every question becomes "how do I look this up?" — and the answer gets split across three terms that mean the same thing.

### 7.5 Use Specific Parameter and Variable Names

**Impact: MEDIUM (prevents confusion when multiple instances are in scope)**

Generic names like `id`, `name`, `data`, `info` communicate nothing about what the value is. When you have multiple IDs or data objects in scope, they collide. Prefer names that convey the semantic role.

**Incorrect (generic names):**

```python
def transfer(id: str, id2: str, data: dict, info: dict) -> None:
    ...

def process_tools(id: str) -> None:
    config = load_config(id)
    memory = load_memory(id)  # is this the same id, or a different one?
    ...
```

Reading the call site: `transfer("u123", "t456", {...}, {...})` — which is the sender, which is the recipient, which dict is which?

**Correct (specific):**

```python
def transfer(sender_id: str, recipient_id: str, transfer_data: TransferRequest, audit_info: AuditContext) -> None:
    ...

def process_tools(toolset_id: str) -> None:
    config = load_config(toolset_id)
    memory = load_memory(toolset_id)
    ...
```

Every name describes what the value is. Call sites self-document.

**When generic is acceptable:**

- Truly generic helpers — `def first(items: list[T]) -> T`, `items` is fine
- Very short functions where the role is obvious from the body
- Following a convention (`self`, `cls`, `_` for ignored values, `i` / `j` for loop indices in math contexts)

**Generic with type annotations can be OK for one-off helpers:**

```python
def render(user: User) -> str:  # "user" is generic but context is clear
    return f"{user.first_name} {user.last_name}"
```

There's only one `User` here — no ambiguity.

**The red flag:** any time you end up with `id`, `id2`, `id3` — or `data`, `info`, `details`, `meta` all in the same scope — stop and rename. The number suffixes tell you the names aren't doing their job.

**Naming for loops:**

```python
# bad
for x in users:
    for y in x.posts:
        for z in y.comments:
            ...

# good
for user in users:
    for post in user.posts:
        for comment in post.comments:
            ...
```

Short variable names are fine when the type is obvious and the body is short. Three-letter variables in a three-level-deep loop is a readability problem.

### 7.6 Use UPPER_CASE for Module Constants

**Impact: LOW-MEDIUM (signals immutability and public/private scope)**

Module-level values that don't change during execution are constants. The `UPPER_CASE` convention signals "don't reassign this" and is widely recognized across Python codebases. Agents often leave constants as regular `lower_case` — the convention is cheap and the signal is strong.

**Incorrect (looks like a reassignable variable):**

```python
# mymodule.py
default_timeout = 30
max_retries = 3
allowed_hosts = frozenset({"localhost", "127.0.0.1"})

def fetch(url: str) -> Response:
    for attempt in range(max_retries):
        try:
            return http.get(url, timeout=default_timeout)
        except TimeoutError:
            continue
```

A reader sees `default_timeout` and can't tell at a glance whether it's a constant or a mutable module-level config someone might reassign.

**Correct (UPPER_CASE signals constant):**

```python
# mymodule.py
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1"})

def fetch(url: str) -> Response:
    for attempt in range(MAX_RETRIES):
        try:
            return http.get(url, timeout=DEFAULT_TIMEOUT)
        except TimeoutError:
            continue
```

**Private / internal constants start with `_`:**

```python
_DEFAULT_CACHE_SIZE = 512
_INTERNAL_HEADER = "x-mymodule-trace"
```

The underscore keeps them out of `from module import *` and signals they're not part of the public API.

**When a value isn't really a constant:**

- It's computed from other values at import time (a derived dict built from `os.environ`, etc.)
- It's mutable and intentionally reassignable (feature flags, test hooks)

For those, keep them `lower_case`. The convention is for *intentional constants* — values you commit to never reassigning.

**Enum members:** also UPPER_CASE by convention:

```python
from enum import Enum

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
```

**Class constants:** UPPER_CASE on the class body, same rule:

```python
class Cache:
    DEFAULT_SIZE = 1024
    _EVICTION_RATIO = 0.1
```

**`typing.Final` to enforce it:**

```python
from typing import Final

DEFAULT_TIMEOUT: Final[int] = 30  # checker flags any reassignment
```

Pair the convention with `Final` when you want the checker to enforce it.

## 8. Imports & Structure

**Impact: LOW-MEDIUM**

Module hygiene. Imports at the top, optional dependencies handled explicitly, no duplicates or unused names.

### 8.1 Handle Optional Dependencies Explicitly

**Impact: MEDIUM (clear error messages instead of cryptic ImportError)**

When a package has optional integrations (e.g., Anthropic support in a multi-provider library), importing the module should not require every optional dep. Handle `ImportError` at module scope with a helpful message pointing to the install extra.

**Incorrect (bare import crashes if the dep isn't installed):**

```python
import anthropic

class AnthropicProvider:
    ...
```

A user who installed just `pip install mylib` and never wanted Anthropic support still gets a crash if any code path accidentally imports this module.

**Incorrect (silently swallowing the ImportError):**

```python
try:
    import anthropic
except ImportError:
    anthropic = None  # downstream code randomly breaks

class AnthropicProvider:
    def __init__(self):
        client = anthropic.Client()  # AttributeError: 'NoneType' has no 'Client'
```

The failure surfaces as a bizarre `AttributeError` far from the root cause.

**Correct (raise with an actionable install hint):**

```python
try:
    import anthropic
except ImportError as e:
    raise ImportError(
        "anthropic is required for AnthropicProvider. "
        "Install with: pip install 'mylib[anthropic]'"
    ) from e

class AnthropicProvider:
    ...
```

The error message tells the user exactly how to fix it. The original `ImportError` is preserved via `from e` for debugging.

**Pairing with `TYPE_CHECKING` for type hints** (see `types-type-checking-imports`):

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import anthropic

try:
    import anthropic as _anthropic_runtime
except ImportError as e:
    raise ImportError(
        "anthropic is required. Install with: pip install 'mylib[anthropic]'"
    ) from e

class AnthropicProvider:
    def __init__(self, client: anthropic.Client) -> None:  # type-hint works
        self._client = client
```

**When to import inside functions instead:**

If the dependency is truly optional at the *feature* level (not the *module* level), defer the import into the function that needs it. Users who never call that function never pay the import cost, and missing the dep only fails if the feature is actually used.

```python
def export_to_parquet(data: list[dict], path: Path) -> None:
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise ImportError(
            "pyarrow is required for Parquet export. "
            "Install with: pip install 'mylib[parquet]'"
        ) from e
    ...
```

Use module-scope for deps the module's public classes require. Use function-scope for features gated behind specific function calls.

### 8.2 No Duplicate Imports

**Impact: LOW (prevents confusion and redundant work)**

Two imports of the same name are either redundant (if they're identical) or a sign that a refactor left both in place. Either way, delete one. Tools flag this, but agents sometimes add a new import on top of an existing one without checking.

**Incorrect (same name imported twice):**

```python
import json
from typing import Any
from pathlib import Path

# ... later in the file, after a later edit ...
from pathlib import Path       # duplicate
from pathlib import Path as P  # different alias, same underlying import
```

The first duplicate is pure redundancy. The second is worse — now `Path` and `P` both exist in the namespace, pointing to the same class.

**Correct (one import per name):**

```python
import json
from typing import Any
from pathlib import Path
```

If two aliases are genuinely needed (very rare — usually a code-smell), pick one:

```python
from pathlib import Path  # use this name everywhere
```

**When "duplicates" are actually distinct:**

```python
from foo import bar
from foo.baz import bar as baz_bar  # different bar, aliased to avoid collision
```

These are different objects with the same name in different namespaces. Aliasing one disambiguates. This is fine — but it's *not* a duplicate; the names differ.

**Detection:**

- `ruff check --select F811` flags redefinitions
- `pyflakes` also catches these

Add to pre-commit or CI.

**Root cause:** duplicate imports usually appear after:

- Merging branches that both added the same import
- An IDE auto-import on top of an existing import
- Refactoring that copied a block without cleaning up the imports

Reviewing the imports block after any merge or mass edit catches these before they land.

### 8.3 Place Imports at the Top of the File

**Impact: LOW-MEDIUM (makes dependencies visible at a glance)**

Imports belong at the top of the module, in conventional ordering (stdlib, third-party, local). Inline imports inside functions hide dependencies from readers, complicate static analysis, and surprise anyone debugging a `ModuleNotFoundError` raised in the middle of a call.

**Incorrect (imports scattered through the function bodies):**

```python
def fetch_user(user_id: str) -> User:
    import requests  # hidden dependency
    response = requests.get(f"/users/{user_id}")
    return User(**response.json())

def process():
    from .helpers import validate  # easily missed
    ...
    import json  # another one
    data = json.dumps(result)
```

Readers can't see the module's dependency graph without scanning every function. Tools that analyze imports (linters, bundle checkers) get confused. If a deferred import fails, the error surfaces far from the file's top.

**Correct (all imports at the top, grouped and ordered):**

```python
import json
from typing import Any

import requests

from .helpers import validate


def fetch_user(user_id: str) -> User:
    response = requests.get(f"/users/{user_id}")
    return User(**response.json())

def process():
    ...
```

The conventional order (PEP 8):

1. Standard library imports
2. Related third-party imports
3. Local application/library-specific imports

Blank lines separate the groups. `ruff` / `isort` automate this — run them.

**When inline imports are legitimate:**

**1. Breaking circular imports.** When two modules legitimately need each other and can't be merged, inline one import inside the function that uses it:

```python
def handle_event(event: Event) -> None:
    from .other_module import process  # breaks an import cycle
    process(event)
```

Add a comment explaining why — future readers might otherwise "fix" it.

**2. Optional dependencies with runtime gating.** When a feature requires a heavy or optional package that shouldn't be loaded unless the feature is used:

```python
def render_plot(data: list[float]) -> bytes:
    import matplotlib.pyplot as plt  # only imported when plotting is requested
    ...
```

This is the narrow exception — think twice before using it. See `imports-optional-dependencies` for a cleaner pattern with typed stubs.

**3. Avoiding module-level side effects.** Rare — if an import triggers side effects you specifically want to defer.

Outside these cases, top-of-file is the rule.

### 8.4 Remove Unused Imports

**Impact: LOW-MEDIUM (prevents accidental dependencies and reduces noise)**

Every import is a declaration of "this module depends on X." Unused imports lie about dependencies, add reading noise, risk circular imports, and can mask refactoring errors (the import survives long after the only call site was deleted).

**Incorrect (imports for names that aren't used):**

```python
import json
import re
from typing import Any, Optional, Union

from .helpers import validate, format_date  # format_date never used

def compact(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"))
```

`re`, `Optional`, `Union`, `format_date` aren't used. Readers wonder if they're intentional. Linters flag them (eventually). `validate` is also unused here.

**Correct (just what's needed):**

```python
import json
from typing import Any


def compact(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"))
```

**Automate detection:**

`ruff check --select F401` flags unused imports. Add it to pre-commit or CI — manual review misses too many.

**The re-export exception:**

When a module intentionally re-exports names from elsewhere (common in `__init__.py`), declare the re-exports explicitly:

```python
# __init__.py
from .client import Client as Client        # explicit re-export — "as" form is F401-safe
from .errors import ClientError as ClientError
```

Or list them in `__all__`:

```python
# __init__.py
from .client import Client
from .errors import ClientError

__all__ = ["Client", "ClientError"]
```

Either form signals "this import is intentional, not forgotten."

**Type-only imports:**

If an import is used only in annotations, move it under `if TYPE_CHECKING:` (see `types-type-checking-imports`). That removes the runtime cost and keeps the checker happy.

**When you might keep an unused import:**

- Forces registration as a side effect (`import my_plugin_module` that self-registers). Document this clearly — `# noqa: F401 — registers handlers at import time`
- Part of a stable public API in `__init__.py` re-exports

Outside those cases: delete.

### 8.5 Scope Helpers and Constants to Their Usage Site

**Impact: LOW-MEDIUM (reduces namespace pollution and clarifies intent)**

When a helper function or constant is only used in one function or class, define it there — not at module level "just in case" someone else needs it later. Module-level scope is a commitment to every future reader: "this is part of the module's surface."

**Incorrect (module-level helper used only inside one function):**

```python
# somewhere in a 500-line module
def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())

def _DEFAULT_MAX_LENGTH() -> int:
    return 280

def summarize(text: str) -> str:
    text = _normalize_whitespace(text)
    return text[: _DEFAULT_MAX_LENGTH()]

# ... 400 more lines, no other use of _normalize_whitespace or _DEFAULT_MAX_LENGTH
```

`_normalize_whitespace` lives in the module namespace forever, visible to everything else in the file. A future reader sees it and wonders if it's meant to be used elsewhere. If not, why is it out here?

**Correct (scope to the function that uses it):**

```python
def summarize(text: str) -> str:
    DEFAULT_MAX_LENGTH = 280
    normalized = " ".join(text.split())
    return normalized[:DEFAULT_MAX_LENGTH]
```

Or, if the helper has enough logic to want a name:

```python
def summarize(text: str) -> str:
    def _normalize(s: str) -> str:
        return " ".join(s.split())

    return _normalize(text)[:280]
```

**When module-level is the right scope:**

- Used by multiple functions within the module
- Genuinely part of the module's API surface
- A constant that needs to be patched in tests (module-level constants are easy to monkeypatch)
- A pattern that would be expensive to rebuild per call (compiled regex, module constant, `TypeAdapter`)

**When class-level is right:**

- Used by multiple methods on the same class
- Part of the class's contract (constants referenced by name, e.g., `MyClass.DEFAULT_TIMEOUT`)

**The rule, reversed:** ask "does this helper need to be at this scope?" If a narrower scope works, use it.

**Imports follow the same principle** (see `imports-top-of-file`): default to top-of-module because imports-at-function-scope is the narrower version of the same instinct. Imports are the exception; helpers and constants are not.


## References

- https://docs.python.org/3/library/typing.html
- https://docs.pydantic.dev/
- https://mypy.readthedocs.io/
- https://peps.python.org/pep-0544/
- https://peps.python.org/pep-0695/
- https://github.com/pydantic/pydantic-ai
