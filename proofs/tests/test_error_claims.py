"""Proofs for python-best-practices error-* rule claims."""

import subprocess
import sys


def test_assert_stripped_under_optimize():
    """error-assert-debug-only: "Python emits no code for assert under -O." """
    proc = subprocess.run(
        [sys.executable, "-O", "-c", "assert False, 'never raises under -O'"],
        capture_output=True,
    )
    assert proc.returncode == 0

    proc = subprocess.run([sys.executable, "-c", "assert False"], capture_output=True)
    assert proc.returncode != 0  # without -O the assert fires
