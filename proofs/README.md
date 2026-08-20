# Claim Proofs

Executable verification for claims made by the rules in `skills/`. Every check cites the rule id and the claim it verifies, so a failing check pinpoints a rule that needs correcting — and a claim that can't be checked here shouldn't ship as a rule.

This directory is repo tooling: it is **not** part of any vendored skill.

## Lanes

- `tests/` — **runtime claims**, executed across every supported CPython (language semantics that changed between versions, counterintuitive runtime behavior: `bool`/`int` subtyping, `gather` orphans, generator finalization, absorbed cancellation, `lru_cache` retention).
- `typing_tests/` — **type-checker claims**, executed through mypy, pyright, and ty against small fixtures with per-checker expected verdicts (variance, exhaustiveness, `cast` being unchecked). A verdict change after a checker upgrade is signal: the backing rule needs a qualifier.

Performance claims and design heuristics have no executable lane; rules state them as heuristics, not facts.

## Running

Requires [uv](https://docs.astral.sh/uv/) and `make`.

```bash
make -C proofs           # runtime matrix (3.11, 3.12, 3.13, 3.14) + typing checkers
make -C proofs 3.14      # one runtime version
make -C proofs typing    # checker fixtures only
make -C proofs -k        # keep going past a failing version
```

Under the hood: `uv run --python <version> pytest` for the runtime lane; `uv run pytest typing_tests` for the checker lane. uv provisions interpreters and checkers on demand.

## Adding a check

1. A rule asserting version- or behavior-sensitive **runtime** semantics → add a test in `tests/`, docstring citing `<skill>/<rule-id>` and quoting the claim.
2. A rule asserting **type-checker** behavior → add a fixture in `typing_tests/fixtures/` (marking the claim line with `EXPECT-ERROR` / `EXPECT-CLEAN`) and its expected verdicts in `typing_tests/test_typing_claims.py`. Observe real checker output first; never encode a guess.
3. Keep checks deterministic: events and subprocess exit codes, no sleeps as synchronization (see `python-pytest/determinism-sync-not-sleep` — the proofs eat their own cooking).
4. A check that fails on a supported version or checker means the rule text is wrong or needs a qualifier — fix the rule, not the check.
