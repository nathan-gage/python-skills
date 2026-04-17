---
title: Phase Related Optional Fields Into Nested Structs
impact: HIGH
impactDescription: one optional check instead of eight
tags: data, modeling, optional, dataclasses
---

## Phase Related Optional Fields Into Nested Structs

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
