# Python Skills

A collection of skills for AI coding agents writing Python. Skills are packaged instructions that extend agent capabilities with domain-specific rules.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Available Skills

### python-best-practices

Python software engineering guidelines derived from real PR review patterns. Contains 50+ rules across 8 categories, prioritized by impact.

**Use when:**
- Writing new Python modules, functions, classes, or data models
- Reviewing Python code for type safety, API clarity, or maintainability
- Refactoring dataclasses, Pydantic models, or state-management patterns
- Designing service interfaces, Protocol boundaries, or exception hierarchies

**Categories covered:**
- Data Modeling (Critical) — derive over store, discriminated unions, explicit variants, mutation contracts
- Type Safety (Critical) — precise types, no `Any` drift, `isinstance` over `hasattr`
- API Design (High) — keyword-only params, private underscores, immutable transforms
- Error Handling (High) — specific exceptions, fail-fast validation, consolidated try/except
- Code Simplification (Medium-High) — comprehensions, early returns, Pythonic idioms
- Performance (Medium) — module-level compilation, set/dict lookups, cached properties
- Naming (Medium) — specific names, consistent terminology, no type suffixes
- Imports & Structure (Low-Medium) — top-of-file imports, optional dependency handling

## Installation

```bash
npx skills add nathan-gage/python-best-practices
```

Or copy directly into Claude Code:

```bash
cp -r skills/python-best-practices ~/.claude/skills/
```

For other agent harnesses, point the harness at `skills/python-best-practices/`. The skill is self-contained.

## Usage

Skills are automatically available once installed. The agent will use them when relevant tasks are detected.

**Examples:**
```
Review this Python module for type safety
```
```
Refactor this class — it's accumulated a lot of optional fields and mode flags
```
```
Design the interface for this service layer
```

## Skill Structure

Each skill contains:
- `SKILL.md` - Entrypoint loaded into agent context
- `README.md` - Human-facing overview
- `metadata.json` - Version, abstract, references
- `AGENTS.md` - Compiled document with all rules expanded
- `rules/` - Individual rule files (one per rule)

See `AGENTS.md` at the repo root for guidance on authoring new rules or sections.

## License

MIT
