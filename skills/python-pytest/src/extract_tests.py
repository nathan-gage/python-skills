#!/usr/bin/env python3
"""Extract rule examples and counter-signals into test-cases.json.

The output is consumed by LLM eval pipelines. The `correct` block is ONE
valid instance under the rule's conditions — not a canonical target. Score
whether the agent (a) recognizes the failure mode in `incorrect`, (b) applies
the rule only when its conditions hold, and (c) PRESERVES code matching the
`counter_signals` passages. Do not score similarity to the `correct` block.

Schema (per entry):
    {
      "rule": "{filename without extension}",
      "title": "{rule title}",
      "impact": "{CRITICAL|HIGH|...}",
      "tags": ["tag1", "tag2"],
      "incorrect": "{first incorrect code block, language=python}",
      "correct": "{first correct code block, language=python}",
      "explanation": "{first paragraph of the rule body}",
      "counter_signals": ["{prose paragraphs saying when NOT to apply the rule}"]
    }

Rules without a clean Incorrect/Correct pair are skipped with a warning.

Usage:
    uv run src/extract_tests.py

Run from the skill root.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from counter_signals import counter_signal_paragraphs

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
INCORRECT_BLOCK_RE = re.compile(
    r"\*\*Incorrect[^*]*?\*\*[^\n]*\n+```python\n(.*?)```",
    re.DOTALL,
)
CORRECT_BLOCK_RE = re.compile(
    r"\*\*Correct[^*]*?\*\*[^\n]*\n+```python\n(.*?)```",
    re.DOTALL,
)


@dataclass
class TestCase:
    rule: str
    title: str
    impact: str
    tags: list[str]
    incorrect: str
    correct: str
    explanation: str
    counter_signals: list[str]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        return None
    fm_raw, body = match.group(1), match.group(2)
    frontmatter: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()
    return frontmatter, body


def first_paragraph(body: str) -> str:
    body = body.lstrip()
    lines = body.split("\n", 1)
    if lines and lines[0].startswith("## "):
        body = lines[1] if len(lines) > 1 else ""
    body = body.lstrip()
    paragraph: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith(("**", "```", "#", ">", "-")):
            break
        paragraph.append(stripped)
    return " ".join(paragraph)


def extract(path: Path) -> TestCase | None:
    text = path.read_text()
    parsed = parse_frontmatter(text)
    if parsed is None:
        return None
    frontmatter, body = parsed

    incorrect_match = INCORRECT_BLOCK_RE.search(body)
    correct_match = CORRECT_BLOCK_RE.search(body)
    if not incorrect_match or not correct_match:
        return None

    title = frontmatter.get("title", path.stem)
    impact = frontmatter.get("impact", "")
    tags_raw = frontmatter.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    explanation = first_paragraph(body)
    counter_signals = counter_signal_paragraphs(body)

    return TestCase(
        rule=path.stem,
        title=title,
        impact=impact,
        tags=tags,
        incorrect=incorrect_match.group(1).rstrip(),
        correct=correct_match.group(1).rstrip(),
        explanation=explanation,
        counter_signals=counter_signals,
    )


def main() -> int:
    root = Path.cwd()
    rules_dir = root / "rules"
    output_path = root / "test-cases.json"

    if not rules_dir.exists():
        print(f"rules/ not found at {rules_dir}", file=sys.stderr)
        return 1

    cases: list[dict[str, object]] = []
    skipped: list[str] = []

    for path in sorted(rules_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        case = extract(path)
        if case is None:
            skipped.append(path.name)
            continue
        cases.append(
            {
                "rule": case.rule,
                "title": case.title,
                "impact": case.impact,
                "tags": case.tags,
                "incorrect": case.incorrect,
                "correct": case.correct,
                "explanation": case.explanation,
                "counter_signals": case.counter_signals,
            }
        )

    payload = {
        "generated_by": "src/extract_tests.py",
        "scoring": (
            "The correct block is one valid instance under the rule's conditions, "
            "not a canonical target. Score condition-aware application and "
            "preservation of code matching counter_signals, not similarity to correct."
        ),
        "count": len(cases),
        "cases": cases,
    }
    output_path.write_text(json.dumps(payload, indent=2) + "\n")

    print(
        f"wrote {output_path.name}: {len(cases)} cases extracted, "
        f"{len(skipped)} skipped",
        file=sys.stderr,
    )
    for name in skipped:
        print(f"  skipped (no clean Incorrect/Correct pair): {name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
