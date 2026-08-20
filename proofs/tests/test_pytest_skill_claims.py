"""Proofs for python-pytest rule claims."""

import os
from urllib.parse import urlencode

import pytest


def test_urlencode_bool_wire_casing():
    """mock-assert-wire-format: "urlencode({"include_disabled": False}) produces
    include_disabled=False (capital F)."
    """
    assert urlencode({"include_disabled": False}) == "include_disabled=False"


def test_monkeypatch_restores_originally_absent_env_var():
    """fixtures-restore-global-state: "monkeypatch records prior state — including 'was not set' —
    and restores it in teardown."
    """
    name = "PYTHON_SKILLS_PROOF_ABSENT_VAR"
    assert name not in os.environ
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv(name, "1")
        assert os.environ[name] == "1"
    assert name not in os.environ  # absent again, not left set


def test_strict_xfail_fails_run_on_unexpected_pass(pytester: pytest.Pytester):
    """determinism-strict-xfail: "an unexpected pass fails the run with [XPASS(strict)]." """
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.xfail(strict=True, reason="expected to fail")
        def test_unexpectedly_passes():
            assert True
        """
    )
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*XPASS(strict)*"])


def test_nonstrict_xfail_keeps_run_green_on_unexpected_pass(pytester: pytest.Pytester):
    """determinism-strict-xfail: "an xfail that unexpectedly passes reports XPASS and the run
    stays green."
    """
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.xfail(reason="expected to fail")
        def test_unexpectedly_passes():
            assert True
        """
    )
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider")
    result.assert_outcomes(xpassed=1)
    assert result.ret == 0  # green despite the marker being stale


def test_same_named_test_modules_collide_under_prepend(pytester: pytest.Pytester):
    """structure-unique-module-names: "two test_utils.py ... collect both in one invocation and
    pytest raises ImportPathMismatchError (or one module shadows the other)" — and
    "--import-mode=importlib ... removes the uniqueness requirement."
    """
    (pytester.path / "service_tests").mkdir()
    (pytester.path / "script_tests").mkdir()
    (pytester.path / "service_tests" / "test_utils.py").write_text("def test_service(): pass\n")
    (pytester.path / "script_tests" / "test_utils.py").write_text("def test_script(): pass\n")

    collided = pytester.runpytest_inprocess("-p", "no:cacheprovider")
    assert collided.ret != 0
    collided.stdout.fnmatch_lines(["*import file mismatch*"])

    importlib_mode = pytester.runpytest_inprocess(
        "-p", "no:cacheprovider", "--import-mode=importlib"
    )
    importlib_mode.assert_outcomes(passed=2)


def test_tests_package_init_alone_does_not_disambiguate(pytester: pytest.Pytester):
    """structure-unique-module-names: "a `tests/` package whose parent is not a package imports as
    tests.<module> ... adding only service/tests/__init__.py and scripts/tests/__init__.py renames
    both to tests.test_utils — still one identity, still colliding."
    """
    for parent in ("service", "scripts"):
        tree = pytester.path / parent / "tests"
        tree.mkdir(parents=True)
        (tree / "__init__.py").write_text("")
        (tree / "test_utils.py").write_text(f"def test_{parent}(): pass\n")

    collided = pytester.runpytest_inprocess("-p", "no:cacheprovider")
    assert collided.ret != 0
    collided.stdout.fnmatch_lines(["*import file mismatch*"])

    importlib_mode = pytester.runpytest_inprocess(
        "-p", "no:cacheprovider", "--import-mode=importlib"
    )
    importlib_mode.assert_outcomes(passed=2)
