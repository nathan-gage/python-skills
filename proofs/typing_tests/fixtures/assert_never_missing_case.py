"""error-assert-never-exhaustiveness: a missed variant is reported at the assert_never call."""

from typing import Literal, assert_never


def priority(level: Literal["low", "high"]) -> int:
    if level == "low":
        return 1
    assert_never(level)  # EXPECT-ERROR: level is still "high" here
