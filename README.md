# Python Skills

A collection of skills for AI coding agents writing Python. Skills are packaged instructions that extend agent capabilities with domain-specific rules.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Available Skills

### python-best-practices

Python software engineering guidelines derived from real PR review patterns. 75 rules across 8 categories, prioritized by impact. A rule match is a signal, not a verdict — most rules are design preferences for new code, not bugs to fix across the repo.

**Use when:**
- Writing new Python modules, functions, classes, or data models
- Reviewing Python code for type safety, API clarity, or maintainability
- Refactoring dataclasses, Pydantic models, or state-management patterns
- Designing service interfaces, Protocol boundaries, or exception hierarchies

**Categories covered (typical impact; individual rules may differ):**
- Data Modeling (High) — mutable defaults, derive-don't-store, discriminated unions, explicit variants, timezone-aware datetimes
- Error Handling (Medium-High) — specific exceptions, context managers, exception hierarchies, traceback-preserving logs
- Type Safety (Medium-High) — precise types over `Any`, fix type errors rather than ignore, `isinstance` over `hasattr`
- API Design (Medium) — keyword-only params, required-before-optional, no boolean-flag soup, private underscores
- Code Simplification (Low-Medium) — comprehensions, early returns, Pythonic idioms
- Performance (Low-Medium) — module-level compilation, set/dict lookups, cached properties (on measured hot paths)
- Naming (Low-Medium) — specific names, consistent terminology, no type suffixes
- Imports & Structure (Low) — top-of-file imports, no import-time side effects, optional dependency handling

### python-async-best-practices

Async and concurrency best practices, split out so event-loop guidance stays delineated and independently installable. 5 rules: blocking calls, task ownership (TaskGroup, cancel-then-drain), bounded fan-out, preserved cancellation, async generator cleanup.

**Use when:**
- Writing or reviewing `async def` code, task spawning, or streaming consumers
- Auditing services for blocking calls or unbounded concurrency
- Debugging hangs, orphaned tasks, or unraisable warnings at teardown

### python-pytest

Pytest discipline for test suites. 15 rules across 5 categories — test value (observable contracts, independent oracles), determinism (event-based synchronization, strict xfail), fixture isolation, mocking boundaries, and suite structure.

**Use when:**
- Writing or reviewing pytest tests and fixtures
- Debugging flaky, order-dependent, or falsely-green tests
- Deciding what deserves to be a committed test
- Configuring pytest's plugin surface

## Installation

```bash
npx skills add nathan-gage/python-best-practices
npx skills add nathan-gage/python-async-best-practices
npx skills add nathan-gage/python-pytest
```

Or copy directly into Claude Code:

```bash
cp -r skills/python-best-practices skills/python-async-best-practices skills/python-pytest ~/.claude/skills/
```

For other agent harnesses, point the harness at the skill directory under `skills/`. Each skill is self-contained.

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
- `SKILL.md` - Entrypoint loaded into agent context (quick reference)
- `README.md` - Human-facing overview and authoring workflow
- `metadata.json` - Version, abstract, references, Python version floor
- `AGENTS.md` - (generated) Compiled document with all rules expanded
- `test-cases.json` - (generated) LLM evaluation data extracted from rule examples
- `rules/` - Individual rule files (one per rule), plus `_sections.md` and `_template.md`
- `src/` - Build, validate, and extract-tests scripts (`build.py`, `validate.py`, `extract_tests.py`)

`AGENTS.md` and `test-cases.json` are generated outputs — do not edit them by hand. See the per-skill README and `AGENTS.md` at the repo root for guidance on authoring new rules or sections.

## License

MIT
