"""Shared detection of counter-signal prose in rule bodies.

A counter-signal is the passage that tells the reader when NOT to apply the
rule — the "preserve this" half of a judgment call. `validate.py` requires
one on every MEDIUM-or-higher rule; `extract_tests.py` exports the matched
paragraphs so eval pipelines can score restraint, not just rewriting.

The patterns are generous by design: the goal is to flag rules with *no*
judgment prose at all, not to grade phrasing. Tune only when a rule with a
genuine counter-signal fails validation.
"""

from __future__ import annotations

import re

MEDIUM_PLUS_IMPACTS: frozenset[str] = frozenset(
    {"CRITICAL", "HIGH", "MEDIUM-HIGH", "MEDIUM"}
)

COUNTER_SIGNAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Bold lead-ins that introduce scope limits or preservation guidance
    re.compile(r"(?im)^\*\*when\b"),
    re.compile(
        r"(?im)^\*\*(?:exception|scope|caveats?|watch|keep|don'?t|preserve|state the test level)\b"
    ),
    # Inline judgment phrasing
    re.compile(r"(?i)\bwhen not to\b"),
    re.compile(r"(?i)\bwhen to (?:keep|use|reach|promote|stay)\b"),
    re.compile(r"(?i)\bis (?:fine|acceptable|appropriate|legitimate|expected|the right tool)\b"),
    re.compile(r"(?i)\b(?:are|stays?|still) fine\b"),
    re.compile(r"(?i)\bfine (?:at|for|when|to)\b"),
    re.compile(r"(?i)\bacceptable\b"),
    re.compile(r"(?i)\blegitimate(?:ly)?\b"),
    re.compile(r"(?i)\bgenuinely\b"),
    re.compile(r"(?i)\bkeep (?:the|them|it|a|an|blocks|`)"),
    re.compile(r"(?i)\bdeliberate exception\b"),
    re.compile(r"(?i)\bonly when\b"),
    re.compile(r"(?i)\bsafe to\b"),
    re.compile(r"(?i)\bnot (?:a law|universal)\b"),
    re.compile(r"(?i)\brule of thumb\b"),
    re.compile(r"(?i)\bheuristic\b"),
    re.compile(r"(?i)\bjudgment call\b"),
)


def _prose_paragraphs(body: str) -> list[str]:
    """Split body into paragraphs, treating fenced code blocks as opaque."""
    paragraphs: list[str] = []
    buffer: list[str] = []
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            buffer.append(line)
            continue
        if not in_fence and not line.strip():
            if buffer:
                paragraphs.append("\n".join(buffer))
                buffer = []
            continue
        buffer.append(line)
    if buffer:
        paragraphs.append("\n".join(buffer))
    return paragraphs


def has_counter_signal(body: str) -> bool:
    return any(pat.search(body) for pat in COUNTER_SIGNAL_PATTERNS)


def counter_signal_paragraphs(body: str) -> list[str]:
    """Return prose paragraphs (not code blocks) carrying counter-signal phrasing."""
    matched: list[str] = []
    for paragraph in _prose_paragraphs(body):
        if paragraph.lstrip().startswith("```"):
            continue
        if any(pat.search(paragraph) for pat in COUNTER_SIGNAL_PATTERNS):
            matched.append(paragraph.strip())
    return matched
