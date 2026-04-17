# Python Best Practices

A structured skill for writing and reviewing Python code. Rules are derived from real PR review patterns, organized by impact, and formatted for AI-agent consumption.

## Structure

- `rules/` — Individual rule files (one per rule)
  - `_sections.md` — Section metadata (titles, impacts, descriptions, prefixes)
  - `_template.md` — Template for creating new rules
  - `{prefix}-{name}.md` — Individual rule files
- `SKILL.md` — Entrypoint loaded into agent context
- `AGENTS.md` — Compiled document with all rules expanded
- `metadata.json` — Version and abstract

## Sections

### 1. Data Modeling (CRITICAL) — `data-`

Derive over store, discriminated unions, explicit variants, mutation contracts. The architectural foundation — mistakes here compound hardest.

### 2. Type Safety (CRITICAL) — `types-`

No `Any` drift, precise annotations, proper narrowing. The type checker is load-bearing; keep it that way.

### 3. API Design (HIGH) — `api-`

Keyword-only params, private underscores, immutable transforms. Interface decisions that compound over years.

### 4. Error Handling (HIGH) — `error-`

Specific exceptions, fail-fast validation, consolidated try/except. Sloppy exceptions hide bugs; good ones localize them.

### 5. Code Simplification (MEDIUM-HIGH) — `simplify-`

Comprehensions, `any()`/`all()`, early returns, dead-code removal. Python idioms that reduce LOC and mental load.

### 6. Performance (MEDIUM) — `perf-`

Module-level compilation, set/dict lookups, cached properties. Python-specific optimizations that matter on hot paths.

### 7. Naming (MEDIUM) — `naming-`

Specific names, consistent terminology, no type suffixes. Names are the most-read interface in any codebase.

### 8. Imports & Structure (LOW-MEDIUM) — `imports-`

Top-of-file imports, optional dependency handling. Module hygiene.

## Creating a New Rule

1. Copy `rules/_template.md` to `rules/{prefix}-{name}.md`
2. Choose the appropriate prefix from `_sections.md`
3. Fill in the frontmatter and content
4. Ensure you have clear incorrect/correct examples with explanations

## Rule File Format

Each rule file should follow this structure:

```markdown
---
title: Rule Title Here
impact: MEDIUM
impactDescription: brief phrase describing the payoff
tags: tag1, tag2
---

## Rule Title Here

Brief explanation of the rule and why it matters. One or two sentences.

**Incorrect (why this is wrong):**

\`\`\`python
# Bad example
\`\`\`

**Correct (why this is right):**

\`\`\`python
# Good example
\`\`\`

Optional closing paragraph with nuance or references.
```

## Impact Levels

- `CRITICAL` — Highest priority; prevents classes of bugs or unmaintainable code
- `HIGH` — Significant maintainability or correctness improvements
- `MEDIUM-HIGH` — Noticeable improvements worth enforcing
- `MEDIUM` — Good practices for cleaner, clearer code
- `LOW-MEDIUM` — Marginal improvements
- `LOW` — Incremental; apply opportunistically

## Acknowledgments

Rule material draws from PR-review patterns in the Pydantic AI codebase (`agent_docs/`), Vercel's `react-best-practices` and `composition-patterns` skills (structural inspiration), and cross-cutting principles from the `clanker-discipline` skill.
