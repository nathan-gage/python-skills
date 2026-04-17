# Python Best Practices

A structured skill for writing and reviewing Python code. Rules are derived from real PR review patterns, organized by impact, and formatted for AI-agent consumption.

**Python version baseline:** 3.11+ (some rules note higher-version features explicitly — e.g., `warnings.deprecated()` is 3.13+).

## Structure

```
python-best-practices/
├── SKILL.md                # Entrypoint loaded into agent context (quick reference)
├── README.md               # This file — human-facing overview and contribution notes
├── metadata.json           # Version, abstract, references, Python version floor
├── AGENTS.md               # (generated) Compiled document with every rule expanded
├── test-cases.json         # (generated) LLM evaluation data extracted from rule examples
├── rules/                  # Individual rule files (one rule per file)
│   ├── _sections.md        # Section metadata (titles, impacts, descriptions, prefixes)
│   ├── _template.md        # Template for new rules (with required `references` line)
│   └── {prefix}-{name}.md  # Rule files; `prefix` matches a section in `_sections.md`
└── src/                    # Build, validate, and extract-tests scripts
    ├── build.py            # Compile rules into AGENTS.md
    ├── validate.py         # Lint rule files (frontmatter, examples, references)
    └── extract_tests.py    # Generate test-cases.json from rule examples
```

## Sections

### 1. Data Modeling (CRITICAL) — `data-`

Derive over store, discriminated unions, explicit variants, mutation contracts, mutable defaults, sentinels, timezone-aware datetimes. The architectural foundation — mistakes here compound hardest.

### 2. Type Safety (CRITICAL) — `types-`

No `Any` drift, precise annotations, proper narrowing. The type checker is load-bearing; keep it that way.

### 3. API Design (HIGH) — `api-`

Keyword-only params, private underscores, immutable transforms, no boolean flag soup. Interface decisions that compound over years.

### 4. Error Handling (HIGH) — `error-`

Specific exceptions, fail-fast validation, consolidated try/except, context managers for resources, exhaustiveness via `assert_never`. Sloppy exceptions hide bugs; good ones localize them.

### 5. Code Simplification (MEDIUM-HIGH) — `simplify-`

Comprehensions, `any()`/`all()`, early returns, dead-code removal. Python idioms that reduce LOC and mental load.

### 6. Performance (MEDIUM) — `perf-`

Module-level compilation, set/dict lookups, cached properties. Python-specific optimizations applied where the hot path is measured.

### 7. Naming (MEDIUM) — `naming-`

Specific names, consistent terminology, no type suffixes. Names are the most-read interface in any codebase.

### 8. Imports & Structure (LOW-MEDIUM) — `imports-`

Top-of-file imports (with documented exceptions), optional dependency handling, no import-time side effects. Module hygiene.

## Authoring Workflow

1. Copy `rules/_template.md` to `rules/{prefix}-{name}.md`
2. Choose the appropriate prefix from `_sections.md`
3. Fill in the frontmatter (including a primary-source `references` line for any rule that depends on language version or library behavior)
4. Write a short explanation, an Incorrect/Correct pair, and a closing note about edge cases
5. Run the build / validate / extract-tests scripts (below)

## Scripts

The `src/` directory contains the maintenance pipeline:

```bash
# Compile rules into AGENTS.md
python src/build.py

# Lint rule files (frontmatter, references, example structure, broken links)
python src/validate.py

# Extract Incorrect/Correct example pairs into test-cases.json (for LLM evals)
python src/extract_tests.py
```

A typical authoring loop is `validate.py` → fix → `build.py` → `extract_tests.py` before committing. `AGENTS.md` and `test-cases.json` are generated outputs — do not edit them by hand.

## Rule File Format

Each rule file follows this structure:

```markdown
---
title: Rule Title Here
impact: MEDIUM
impactDescription: brief phrase describing the payoff
tags: tag1, tag2, applicability:pydantic   # `applicability:` for ecosystem-specific rules
references: https://docs.python.org/3/library/...
---

## Rule Title Here

Brief explanation of the rule and why it matters. Name the impulse the agent is tempted to take.

**Incorrect (what's wrong with this):**

```python
# Bad example
```

**Correct (what's right about this):**

```python
# Good example
```

Optional closing paragraph with nuance, edge cases, or version notes.
```

### When `references` is required

`references` is **required** when the rule depends on:

- A specific Python version (3.10 union types in `isinstance`, 3.11 `assert_never`, 3.13 `warnings.deprecated`)
- Standard-library behavior (`assert` under `-O`, `cached_property` thread safety)
- Third-party library behavior (Pydantic, mypy, ruff)
- A PEP

Pure judgment-call rules (naming preferences, taste) may omit `references` but adding one is encouraged.

### Tagging applicability

Rules that only apply within a specific ecosystem (e.g., Pydantic) carry an `applicability:{name}` tag and call it out in the body. This lets future filtering/eval pipelines skip rules that don't apply to a given codebase.

## Impact Levels

- `CRITICAL` — Highest priority; prevents classes of bugs or unmaintainable code
- `HIGH` — Significant maintainability or correctness improvements
- `MEDIUM-HIGH` — Noticeable improvements worth enforcing
- `MEDIUM` — Good practices for cleaner, clearer code
- `LOW-MEDIUM` — Marginal improvements
- `LOW` — Incremental; apply opportunistically (e.g., micro-optimizations on profiled hot paths only)

## Acknowledgments

Rule material draws from PR-review patterns in the Pydantic AI codebase (`agent_docs/`), Vercel's `react-best-practices` and `composition-patterns` skills (structural inspiration), and cross-cutting principles from the `clanker-discipline` skill.
