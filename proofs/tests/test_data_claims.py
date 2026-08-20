"""Proofs for python-best-practices data-* rule claims."""

import dataclasses
import sys
import warnings
from datetime import UTC, datetime, timezone

import pytest


def test_mutable_default_shared_across_calls():
    """data-mutable-defaults: "A mutable default is shared across every call that doesn't override it." """

    def append_item(item: int, items: list[int] = []) -> list[int]:  # noqa: B006 — the claim under test
        items.append(item)
        return items

    assert append_item(1) == [1]
    assert append_item(2) == [1, 2]  # same list object as the first call


def test_dataclass_rejects_bare_mutable_default():
    """data-mutable-defaults: "@dataclass rejects bare mutable defaults with ValueError." """
    with pytest.raises(ValueError, match="mutable default"):

        @dataclasses.dataclass
        class User:
            tags: list[str] = []  # the claim under test


def test_bool_is_int_subtype():
    """data-reject-bool-as-int: "isinstance(True, int) is True, True == 1, and hash(True) == hash(1)." """
    assert isinstance(True, int)
    assert True == 1  # noqa: E712 — the claim under test
    assert hash(True) == hash(1)


def test_bool_collides_with_int_dict_key():
    """data-reject-bool-as-int: "{1: ..., True: ...} — one entry: True collides with key 1." """
    d = {1: "a", True: "b"}
    assert d == {1: "b"}
    assert len(d) == 1


def test_bool_ordering_of_checks_matters():
    """data-reject-bool-as-int: "the check must come first, because the int check accepts booleans." """
    value: object = True
    assert isinstance(value, int)  # an int-only gate lets True through
    assert isinstance(value, bool) or not isinstance(value, int)  # bool-first gate rejects it


def test_sum_counts_true_flags():
    """data-reject-bool-as-int: "the same subtype relationship is why sum(flags) counts Trues." """
    assert sum([True, False, True]) == 2


def test_utc_alias_is_timezone_utc():
    """data-aware-datetimes: "UTC (3.11+) is an alias for timezone.utc." """
    assert UTC is timezone.utc
    assert datetime.now(UTC).tzinfo is timezone.utc


def test_utcnow_is_naive_and_deprecated_in_312():
    """data-aware-datetimes: "datetime.utcnow() returns naive; deprecated in 3.12+." """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        value = datetime.utcnow()
    assert value.tzinfo is None
    emitted_deprecation = any(issubclass(w.category, DeprecationWarning) for w in caught)
    assert emitted_deprecation == (sys.version_info >= (3, 12))
