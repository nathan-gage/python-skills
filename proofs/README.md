# Claim Proofs

Executable verification for claims made by the rules in `skills/`. Every test cites the rule id and the exact claim it proves, so a failing proof pinpoints a rule that needs correcting — and a claim that can't be proven here shouldn't ship as a rule.

This directory is repo tooling: it is **not** part of any vendored skill.

## Scope

Runtime-provable claims only, prioritized by risk of version drift:

- language semantics that changed between versions (`cached_property` locking, `datetime.UTC`)
- counterintuitive runtime behavior rules assert (`bool`/`int` subtyping, `gather` orphans, generator finalization, `lru_cache` retention)
- pytest behaviors the `python-pytest` skill depends on (strict xfail, monkeypatch restoration, import-identity collisions)

Type-checker-level claims (variance, narrowing, `TYPE_CHECKING`) are out of scope for this harness — they are verified against checker documentation, not runtime.

## Running

Requires [uv](https://docs.astral.sh/uv/). Run the suite across every supported Python:

```bash
make -C proofs           # all versions: 3.11, 3.12, 3.13, 3.14
make -C proofs 3.14      # one version
make -C proofs -k        # keep going past a failing version
```

Under the hood: `uv run --python <version> pytest`. uv provisions interpreters on demand.

## Adding a proof

1. New rule makes a version- or behavior-sensitive claim → add a test in `tests/`, docstring citing `<skill>/<rule-id>` and quoting the claim.
2. Keep proofs deterministic: events and subprocess checks, no sleeps as synchronization (see `python-pytest/determinism-sync-not-sleep` — the proofs eat their own cooking).
3. A proof that fails on some supported version means the rule text is wrong or needs a version qualifier — fix the rule, not the proof.
