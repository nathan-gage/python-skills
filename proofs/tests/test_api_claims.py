"""Proofs for python-best-practices api-* rule claims."""

import dataclasses

import pytest


def test_dataclass_required_after_optional_is_definition_error():
    """api-required-before-optional: "trying to put an optional field before a required one is a
    TypeError at class-definition time."
    """
    with pytest.raises(TypeError, match="non-default argument"):

        @dataclasses.dataclass
        class Tool:
            name: str
            description: str = ""
            version: str  # the claim under test


def test_kw_only_lifts_the_ordering_constraint():
    """api-required-before-optional: "Everything after `_: KW_ONLY` is keyword-only, so the
    'required before optional' rule stops applying."
    """

    @dataclasses.dataclass
    class Tool:
        name: str
        _: dataclasses.KW_ONLY
        description: str = ""
        version: str  # required, keyword-only — legal after a default

    tool = Tool("grep", version="1.0")
    assert (tool.name, tool.version, tool.description) == ("grep", "1.0", "")
    with pytest.raises(TypeError):
        Tool("grep")  # version is still required
