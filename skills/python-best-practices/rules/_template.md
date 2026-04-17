---
title: Rule Title Here
impact: MEDIUM
impactDescription: brief phrase describing the payoff (e.g., "prevents drift between call sites")
tags: tag1, tag2
references: https://primary-source-1.example.com, https://primary-source-2.example.com
---

## Rule Title Here

Brief explanation of the rule and why it matters. One or two sentences. Name the impulse the agent is tempted to take.

**Incorrect (what's wrong with this):**

```python
# Bad code example
```

**Correct (what's right about this):**

```python
# Good code example
```

Optional closing paragraph with nuance, edge cases, or references.

---

## Authoring notes

**The `references` field is required when the rule depends on language-version or library behavior.** Link to primary sources — the language reference, library docs, or a PEP. If the rule is a pure judgment call (e.g., a naming preference), `references` may be omitted, but adding one is still encouraged.

Examples of when references are required:

- Rule mentions a specific Python version (e.g., 3.10, 3.11, 3.13)
- Rule cites stdlib behavior (e.g., `assert` semantics under `-O`, `cached_property` thread safety)
- Rule cites third-party library behavior (Pydantic, mypy, ruff)
- Rule cites a PEP

Examples of when references may be omitted:

- "Use `_prefix` for private helpers" (project convention, no version dependency)
- "Specific names beat generic names" (taste / readability)

Keep references to **primary sources**. Blog posts and tutorials drift; PEPs and stdlib docs do not.
