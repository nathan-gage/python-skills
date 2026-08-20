---
name: python-pytest
description: Pytest discipline for writing, reviewing, and fixing Python tests — what deserves to be a committed test, deterministic concurrency testing, fixture isolation, mocking boundaries, and suite structure. Triggers on writing or reviewing pytest tests, designing fixtures, parametrizing cases, mocking or patching, debugging flaky or order-dependent tests, xfail/skip decisions, and pytest configuration.
license: MIT
metadata:
  author: python-pytest
  version: "1.0.0"
  pythonVersion: ">=3.11"
---

# Python Pytest

Guidelines for writing and reviewing pytest suites. 15 rules across 5 categories, prioritized by impact.

A rule match is a signal, not a verdict. Most rules are design preferences for new tests — check the rule's impact level before flagging in review or churning a stable suite.

Quick-reference lines are triggers, not licenses: before applying a rule as a review finding or a transformation, open the rule file and check its counter-signal — the marker-opened paragraph (`**When ...**` / `**Scope:**` / `**Exception ...**`) saying when NOT to apply it.

## When to Apply

- Writing new tests or fixtures
- Reviewing test files for value, isolation, or determinism
- Debugging flaky, order-dependent, or falsely-green tests
- Configuring pytest and its plugin surface

The unit of judgment is the *contract a test defends* — every rule here traces back to whether a failure would mean something.

## Impact Levels

- `HIGH` — the test defends nothing or lies (probes, self-oracles, timing bets, masked flakes). Fix when found.
- `MEDIUM-HIGH` — isolation and mocking failures that surface as order-dependence or tautology.
- `MEDIUM` — structure and granularity; apply to new tests.
- `LOW-MEDIUM` — suite-level hygiene; apply when configuring or composing suites.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Test Value | HIGH | `value-` |
| 2 | Determinism | HIGH | `determinism-` |
| 3 | Fixtures & Isolation | MEDIUM-HIGH | `fixtures-` |
| 4 | Mocking | MEDIUM-HIGH | `mock-` |
| 5 | Structure & Execution | MEDIUM | `structure-` |

## Quick Reference

### Test Value (`value-`)

- `value-observable-contracts` — A committed test protects a named behavior; delete execution probes
- `value-independent-oracles` — Expected values derived independently, never by re-running the implementation's formula
- `value-one-behavior-per-test` — Split independently-failing phases; merge duplicate coverage

### Determinism (`determinism-`)

- `determinism-sync-not-sleep` — Events/barriers with failure-bound timeouts; never sleeps or elapsed-time thresholds
- `determinism-no-flake-masking` — No rerun plugins, widened timeouts, or intermittent xfail; fix the race
- `determinism-strict-xfail` — `xfail(strict=True)` so an unexpected pass fails the run

### Fixtures & Isolation (`fixtures-`)

- `fixtures-narrowest-scope` — Function scope by default; widen only expensive immutable setup
- `fixtures-restore-global-state` — `monkeypatch` env/cwd/attrs; restore absent vars too; cleanup runs on failure
- `fixtures-canonical-objects` — Production constructors for fixtures, not hand-guessed dicts; raw inputs when the constructor is under test

### Mocking (`mock-`)

- `mock-stable-boundaries` — Fake the transport you don't own; run the code you do; no mock tautologies
- `mock-patch-where-used` — Patch the namespace where the name is looked up, not where it's defined
- `mock-assert-wire-format` — Assert serialized bytes/strings at compatibility boundaries, not Python intent

### Structure & Execution (`structure-`)

- `structure-parametrize-partitions` — Cases are contract-distinct partitions with independent expecteds; guard generated case sets
- `structure-unique-module-names` — Collision-free test module import identities across composed suites
- `structure-plugin-hygiene` — Autoload is a fine default; on observed plugin drift, make the surface explicit

## How to Use

Read individual rule files for detail:

```
rules/value-observable-contracts.md
rules/mock-patch-where-used.md
```

Each rule has:

- Impact level in frontmatter
- Brief explanation
- Incorrect example
- Correct example
- Optional note on edge cases

For the full compiled guide with all rules expanded: `AGENTS.md`.
