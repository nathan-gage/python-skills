---
title: Rule Title Here
impact: MEDIUM
impactDescription: brief phrase describing the payoff (e.g., "prevents drift between call sites")
tags: tag1, tag2
references: https://primary-source-1.example.com, https://primary-source-2.example.com
---

## Rule Title Here

Brief explanation — one or two sentences. Observational, not prescriptive: describe the pattern and what it costs.

**Incorrect ({what's wrong with this}):**

```python
# Bad code example
```

**Correct ({what's right about this}):**

```python
# Good code example
```

Optional one-paragraph note with nuance, edge cases, or version notes.

**When NOT to apply:** every rule MUST end with at least one counter-signal — a standalone paragraph opening with an approved marker (`**When ...**`, `**Scope ...**`, `**Preserve ...**`, `**Exception ...**`, `**Keep ...**`, `**Caveat ...**`, `**Don't ...**`, `**Watch ...**`) that says when the existing code should be preserved. `validate.py` enforces its presence; `extract_tests.py` exports it as `counter_signals` for restraint-scoring evals. Let the examples carry the main point; the counter-signal carries the judgment.
