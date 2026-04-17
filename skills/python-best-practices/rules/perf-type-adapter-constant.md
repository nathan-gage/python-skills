---
title: Define TypeAdapter Instances at Module Level
impact: MEDIUM
impactDescription: avoids repeated schema construction
tags: perf, pydantic, type-adapter, module-level, applicability:pydantic
references: https://docs.pydantic.dev/latest/api/type_adapter/
---

## Define `TypeAdapter` Instances at Module Level

> **Applicability:** this rule is specific to Pydantic v2's `TypeAdapter`. The same principle applies to any object whose constructor does real work (`json.JSONDecoder` with custom hooks, `msgpack.Packer`, compiled templates) — the Pydantic example is the canonical case.

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
