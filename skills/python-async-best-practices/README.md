# Python Async Best Practices

A structured skill for writing and reviewing asyncio code. Rules cover event-loop discipline — blocking calls, task lifecycle, bounded fan-out, stream cleanup — formatted for agent consumption. Split out of `python-best-practices` so async guidance stays delineated and independently vendorable.

**Python version baseline:** 3.11+ (`TaskGroup`, `asyncio.timeout`; the 3.13 executor-sizing change is called out inline).

## Structure

```
python-async-best-practices/
├── SKILL.md                # Entrypoint loaded into agent context (quick reference)
├── README.md               # This file
├── metadata.json           # Version, abstract, references
├── AGENTS.md               # (generated) Compiled document with every rule expanded
├── test-cases.json         # (generated) LLM eval data extracted from rule examples
├── rules/                  # Individual rule files (one rule per file)
│   ├── _sections.md        # Section metadata
│   ├── _template.md        # Template for new rules
│   └── async-{name}.md     # Rule files
└── src/                    # Build, validate, extract-tests scripts
```

## Sections

| # | Section | Typical Impact | Prefix |
|---|---|---|---|
| 1 | Concurrency & Async | MEDIUM-HIGH | `async-` |

Individual rules range one level above or below — always check the rule frontmatter.

## Authoring Workflow

1. Copy `rules/_template.md` to `rules/async-{name}.md`
2. Fill in frontmatter (`title`, `impact`, `impactDescription`, `tags`, `references`)
3. Write a short explanation + Incorrect/Correct pair + optional note
4. Run `src/validate.py` → fix → `src/build.py` → `src/extract_tests.py`

Version-sensitive or counterintuitive runtime claims MUST get an executable proof in the repository's `proofs/` harness (see the root `AGENTS.md`).

## Scripts

```bash
uv run src/build.py            # compile rules into AGENTS.md
uv run src/validate.py         # lint frontmatter, references, example structure
uv run src/extract_tests.py    # generate test-cases.json for LLM evals
```

`AGENTS.md` and `test-cases.json` are generated outputs — don't hand-edit.

## Relationship to python-best-practices

`python-best-practices` covers production Python generally; this skill owns the event-loop discipline, including asyncio cancellation semantics (`async-preserve-cancellation`). Its `error-specific-exceptions` rule covers broad-catch hygiene and points here for the asyncio depth. Cross-references between skills are by rule id.
