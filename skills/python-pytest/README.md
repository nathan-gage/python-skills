# Python Pytest

A structured skill for writing and reviewing pytest suites. Rules codify testing discipline — what deserves to be committed, how tests stay deterministic and isolated, where mocks belong — formatted for agent consumption.

**Python version baseline:** 3.11+.

## Structure

```
python-pytest/
├── SKILL.md                # Entrypoint loaded into agent context (quick reference)
├── README.md               # This file
├── metadata.json           # Version, abstract, references
├── AGENTS.md               # (generated) Compiled document with every rule expanded
├── test-cases.json         # (generated) LLM eval data extracted from rule examples
├── rules/                  # Individual rule files (one rule per file)
│   ├── _sections.md        # Section metadata
│   ├── _template.md        # Template for new rules
│   └── {prefix}-{name}.md  # Rule files; `prefix` matches a section in `_sections.md`
└── src/                    # Build, validate, extract-tests scripts
```

## Sections

| # | Section | Typical Impact | Prefix |
|---|---|---|---|
| 1 | Test Value | HIGH | `value-` |
| 2 | Determinism | HIGH | `determinism-` |
| 3 | Fixtures & Isolation | MEDIUM-HIGH | `fixtures-` |
| 4 | Mocking | MEDIUM-HIGH | `mock-` |
| 5 | Structure & Execution | MEDIUM | `structure-` |

Section impact is the typical case; individual rules range one level above or below — always check the rule frontmatter.

## Authoring Workflow

1. Copy `rules/_template.md` to `rules/{prefix}-{name}.md`
2. Choose the prefix from `_sections.md`
3. Fill in frontmatter (`title`, `impact`, `impactDescription`, `tags`, `references`)
4. Write a short explanation + Incorrect/Correct pair + optional note
5. Run `src/validate.py` → fix → `src/build.py` → `src/extract_tests.py`

Keep rule bodies short — target 20–40 lines. One Incorrect block, one Correct block, optional one-paragraph note. Rules are observational, not prescriptive: describe the pattern and the cost; show the fix; leave judgment to the reader.

## Scripts

```bash
uv run src/build.py            # compile rules into AGENTS.md
uv run src/validate.py         # lint frontmatter, references, example structure
uv run src/extract_tests.py    # generate test-cases.json for LLM evals
```

`AGENTS.md` and `test-cases.json` are generated outputs — don't hand-edit.

## Relationship to python-best-practices

`python-best-practices` covers production Python (data modeling, errors, async, types); this skill covers the test suite that guards it. The shared philosophy: a rule match is a signal, not a verdict, and the reader's context wins. Cross-references between the two skills are by rule id.
