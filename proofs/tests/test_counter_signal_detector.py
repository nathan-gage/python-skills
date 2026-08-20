"""Unit tests for the skills' counter-signal detector (src/counter_signals.py).

The detector is positional, not natural-language classification: only prose
paragraphs that OPEN with a marker count. These tests pin the false-positive
modes the marker design exists to prevent.
"""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[2] / "skills" / "python-best-practices" / "src")
)

from counter_signals import counter_signal_paragraphs, has_counter_signal  # noqa: E402


def test_marked_paragraph_is_extracted():
    body = (
        "## Rule\n\nDo the thing.\n\n"
        "**Preserve the existing design when:** the callers are external.\n"
    )
    matches = counter_signal_paragraphs(body)
    assert len(matches) == 1
    assert matches[0].startswith("**Preserve")


def test_affirmative_thesis_with_keep_is_not_extracted():
    body = (
        "## Rule\n\n"
        "Renaming a public function is a breaking change. Keep the old name as a "
        "deprecated alias for at least one release.\n"
    )
    assert counter_signal_paragraphs(body) == []
    assert not has_counter_signal(body)


def test_mid_paragraph_marker_is_not_extracted():
    body = "## Rule\n\nDo the thing. **When not to:** never, actually.\n"
    assert counter_signal_paragraphs(body) == []


def test_code_blocks_never_match():
    body = (
        "## Rule\n\nDo the thing.\n\n"
        "```python\n# **When** in doubt, keep the check\nkeep = True\n```\n"
    )
    assert counter_signal_paragraphs(body) == []


def test_multiple_markers_all_extracted_in_order():
    body = (
        "## Rule\n\nThesis.\n\n"
        "**Scope:** only fan-out that scales with input.\n\n"
        "middle prose.\n\n"
        "**When NOT to bound:** a fixed handful of coroutines.\n"
    )
    matches = counter_signal_paragraphs(body)
    assert [m.split(":")[0] for m in matches] == ["**Scope", "**When NOT to bound"]
