"""Checker-fixture evidence for typing-behavior claims.

Runs mypy, pyright, and ty over small fixtures and asserts each checker's
verdict, so typing claims in the skills rest on executed checker behavior
rather than memory. Each fixture's module docstring cites the rule it backs;
`EXPECT-ERROR` / `EXPECT-CLEAN` comments mark the claim line.

A verdict change after a checker upgrade is signal, not noise: it means a
rule's typing claim needs a version qualifier or a rewrite.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

# fixture filename -> should the checker report at least one error?
# Observed uniform across mypy 1.13+, pyright 1.1.390+, and ty 0.0.1a.
CASES: list[tuple[str, bool]] = [
    ("invariance_list_param.py", True),
    ("covariant_sequence_param.py", False),
    ("assert_never_missing_case.py", True),
    ("cast_is_unchecked.py", False),
]


def _mypy_has_errors(fixture: Path, cache_dir: Path) -> bool:
    proc = subprocess.run(
        [
            sys.executable, "-m", "mypy",
            "--no-error-summary",
            "--cache-dir", str(cache_dir),
            str(fixture),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), f"mypy usage error: {proc.stdout}{proc.stderr}"
    return proc.returncode == 1


def _pyright_has_errors(fixture: Path, cache_dir: Path) -> bool:
    del cache_dir
    proc = subprocess.run(
        ["pyright", "--outputjson", str(fixture)],
        capture_output=True,
        text=True,
    )
    report = json.loads(proc.stdout)
    return report["summary"]["errorCount"] > 0


def _ty_has_errors(fixture: Path, cache_dir: Path) -> bool:
    del cache_dir
    proc = subprocess.run(
        ["ty", "check", str(fixture)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), f"ty usage error: {proc.stdout}{proc.stderr}"
    return proc.returncode == 1


CHECKERS = {
    "mypy": _mypy_has_errors,
    "pyright": _pyright_has_errors,
    "ty": _ty_has_errors,
}


@pytest.mark.parametrize("fixture_name, expect_errors", CASES)
@pytest.mark.parametrize("checker", sorted(CHECKERS))
def test_checker_verdict(checker: str, fixture_name: str, expect_errors: bool, tmp_path: Path):
    fixture = FIXTURES / fixture_name
    has_errors = CHECKERS[checker](fixture, tmp_path)
    assert has_errors == expect_errors, (
        f"{checker} verdict changed on {fixture_name}: "
        f"expected {'errors' if expect_errors else 'clean'} — "
        f"the rule claim this fixture backs needs a qualifier"
    )
