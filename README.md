# Python Best Practices

An agent skill for Python software engineering. Codifies review-derived rules that keep Python codebases type-safe, well-composed, and maintainable — especially when much of the code is written by AI agents.

Follows the [Agent Skills](https://agentskills.io/) format and works with Claude Code, Claude.ai, Cursor, and any harness that loads `SKILL.md` frontmatter.

## The Skill

### python-best-practices

Comprehensive Python guidelines derived from PR review patterns. Contains 50+ rules across 8 categories, prioritized by impact.

**Use when:**
- Writing new Python modules, functions, classes, or data models
- Reviewing Python code for type safety, API clarity, or maintainability
- Refactoring dataclasses, Pydantic models, or state-management patterns
- Designing service interfaces, Protocol boundaries, or exception hierarchies

**Categories covered (in priority order):**

1. **Data Modeling (Critical)** — derive over store, discriminated unions, explicit variants, mutation contracts
2. **Type Safety (Critical)** — precise types, no `Any` drift, `isinstance` over `hasattr`
3. **API Design (High)** — keyword-only params, private underscores, immutable transforms
4. **Error Handling (High)** — specific exceptions, fail-fast validation, consolidated try/except
5. **Code Simplification (Medium-High)** — comprehensions, early returns, Pythonic idioms
6. **Performance (Medium)** — module-level compilation, set/dict lookups, cached properties
7. **Naming (Medium)** — specific names, consistent terminology, no type suffixes
8. **Imports & Structure (Low-Medium)** — top-of-file imports, optional dependency handling

## Installation

**Claude Code:**

```bash
cp -r skills/python-best-practices ~/.claude/skills/
```

**Claude.ai:**

Add the skill to project knowledge or paste `SKILL.md` contents into the conversation.

**Any agent harness:**

Point your harness at `skills/python-best-practices/`. The skill is self-contained.

## Usage

Once installed, the agent loads the skill when relevant tasks appear.

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

```
skills/python-best-practices/
├── SKILL.md          # Entrypoint loaded into agent context
├── README.md         # Human-facing overview
├── metadata.json     # Version, abstract, references
├── AGENTS.md         # Compiled document with all rules expanded
└── rules/
    ├── _sections.md  # Section definitions
    ├── _template.md  # Template for new rules
    └── {prefix}-{name}.md  # Individual rule files
```

Each rule file is self-contained. The agent can load the skill map from `SKILL.md`, then reach for the specific rule file it needs.

See `AGENTS.md` at the repo root for guidance on authoring new rules or sections.

## Philosophy

Agents have systematic impulses that erode codebases over time: reaching for `Any`, stacking optional fields into grab-bag models, catching bare `Exception`, bypassing type checkers with `# type: ignore`, and repeating logic because refactoring feels expensive. Each shortcut compounds — the codebase drifts toward a state nobody intended, and the cost lands on whoever touches it next.

This skill is the pushback. It names the impulse, shows the failure, and points at the better path — in vocabulary the agent recognizes, with examples the agent will actually match against.

This codebase will outlive the agents that write to it. Every shortcut becomes someone else's burden; every hack compounds into technical debt that slows everyone down. The skill is not a checklist — it's a discipline, pointed at the future.

## License

MIT
