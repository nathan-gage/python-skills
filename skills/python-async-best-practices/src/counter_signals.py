"""Structural detection of counter-signal passages in rule bodies.

A counter-signal is the passage that tells the reader when NOT to apply the
rule — the "preserve this" half of a judgment call. It must be a standalone
prose paragraph that OPENS with one of a small closed set of bold markers,
so detection is positional, not natural-language classification:

    **When ...** / **Preserve ...** / **Scope ...** / **Exception ...**
    **Caveat(s) ...** / **Keep ...** / **Don't ...** / **Watch ...**
    **State the test level ...**

`validate.py` requires one on every rule regardless of impact; `extract_tests.py`
exports exactly these paragraphs as `counter_signals`, so eval pipelines score
restraint against passages that are unambiguously conditions — never against a
rule's affirmative thesis, and never against code blocks.
"""

from __future__ import annotations

import re

COUNTER_SIGNAL_MARKER_RE: re.Pattern[str] = re.compile(
    r"^\*\*(?:when|preserve|scope|exception|caveats?|keep|don'?t|watch|state the test level)\b",
    re.IGNORECASE,
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


def counter_signal_paragraphs(body: str) -> list[str]:
    """Return prose paragraphs that open with a counter-signal marker.

    Paragraphs inside or beginning with code fences never match; a marker
    phrase appearing mid-paragraph (e.g. inside a rule's affirmative thesis)
    never matches.
    """
    matched: list[str] = []
    for paragraph in _prose_paragraphs(body):
        stripped = paragraph.strip()
        if stripped.startswith("```"):
            continue
        if COUNTER_SIGNAL_MARKER_RE.match(stripped):
            matched.append(stripped)
    return matched


def has_counter_signal(body: str) -> bool:
    return bool(counter_signal_paragraphs(body))
