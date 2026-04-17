# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, Cursor, Copilot, etc.) when working with code in this repository.

## Repository Overview

An agent skill for Python software engineering, packaged for use with Claude Code and other agent harnesses. Skills are bundles of instructions and rules that extend an agent's capabilities with domain-specific guidance.

This skill exists to counteract the failure modes agents fall into when writing Python: reaching for `Any`, stacking optional fields, bypassing the type checker, catching broad exceptions, and repeating logic across call sites. The rules are opinionated, codified from real PR reviews and production experience. This codebase will outlive the agents that write to it — the skill here is the sieve that keeps quality in.

## Creating a New Skill

### Directory Structure

```
skills/
  {skill-name}/           # kebab-case directory name
    SKILL.md              # Required: skill definition (frontmatter + quick reference)
    README.md             # Required: human-facing overview and contribution notes
    metadata.json         # Required: version, abstract, references
    AGENTS.md             # Required: compiled full document with all rules expanded
    rules/
      _sections.md        # Section definitions (title, prefix, impact)
      _template.md        # Template for new rule files
      {prefix}-{name}.md  # Individual rule files
```

### Naming Conventions

- **Skill directory**: `kebab-case` (e.g., `python-best-practices`)
- **SKILL.md**: Always uppercase, always this exact filename
- **Rule files**: `{prefix}-{short-name}.md` where prefix matches a section in `_sections.md`
- **Special files**: Prefixed with `_` (excluded from compilation)

### SKILL.md Format

```markdown
---
name: {skill-name}
description: {One sentence describing when the skill should trigger. Include the exact tasks it covers.}
license: MIT
metadata:
  author: {author}
  version: "1.0.0"
---

# {Skill Title}

{Brief description of what the skill does and when to apply it.}

## When to Apply

- {Trigger 1}
- {Trigger 2}

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | {Section} | {IMPACT} | `{prefix}-` |

## Quick Reference

### 1. {Section Name} ({IMPACT})

- `{rule-id}` - {One-line summary}
```

### Rule File Format

```markdown
---
title: {Rule Title}
impact: {CRITICAL | HIGH | MEDIUM-HIGH | MEDIUM | LOW-MEDIUM | LOW}
impactDescription: {brief phrase describing the payoff}
tags: {comma-separated tags}
---

## {Rule Title}

Brief explanation — why it matters in one paragraph.

**Incorrect ({what's wrong with this}):**

```python
# Bad code example
```

**Correct ({what's right about this}):**

```python
# Good code example
```

Optional closing paragraph with nuance, edge cases, or references.
```

### Best Practices for Context Efficiency

Skills load on-demand — only the skill name and description are loaded at startup. The full `SKILL.md` loads only when the agent decides the skill is relevant. Keep each file small so the agent pulls in only what it needs:

- **Keep SKILL.md under 200 lines** — it should be a map, not a textbook
- **One rule per file** — agents can grep for the specific rule they care about
- **Write specific descriptions** — every word in the description shapes when the skill triggers
- **Use progressive disclosure** — `SKILL.md` points at rule files; rule files point at external references if needed

### Impact Levels

- `CRITICAL` — Prevents classes of bugs or unmaintainable code; never skip
- `HIGH` — Significant maintainability or correctness improvements
- `MEDIUM-HIGH` — Noticeable improvements worth enforcing
- `MEDIUM` — Good practices for cleaner, clearer code
- `LOW-MEDIUM` — Marginal improvements
- `LOW` — Incremental; apply opportunistically

### Section Ordering

Sections in `_sections.md` are numbered. The numeric prefix communicates priority, but the **filename prefix** (e.g., `types-`, `api-`) is what groups rules. Rules within a section sort alphabetically by title.

## Philosophy

These skills are written for agents first, humans second. That means:

- **Impulses matter.** Every rule names the shortcut the agent is tempted to take, then names the better path.
- **Examples over prose.** Incorrect/correct pairs beat paragraphs of explanation.
- **Short over exhaustive.** One focused rule beats a catch-all essay.
- **Concrete over abstract.** "Use `isinstance()` over `hasattr()`" beats "prefer explicit type checks."

When adding rules, ask: *would an agent reading this recognize the mistake they just made?* If not, the rule is either too vague or the example is too generic.
