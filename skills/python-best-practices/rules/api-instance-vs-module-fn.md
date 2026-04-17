---
title: Instance Methods for State, Module Functions for Pure Logic
impact: MEDIUM
impactDescription: avoids unnecessary coupling while enabling polymorphism
tags: api, methods, functions, design
---

## Instance Methods for State, Module Functions for Pure Logic

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
