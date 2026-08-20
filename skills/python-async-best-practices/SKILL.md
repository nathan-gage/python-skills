---
name: python-async-best-practices
description: Async and concurrency best practices for Python — event-loop discipline, task lifecycle, bounded fan-out, and async generator cleanup. Triggers on writing or reviewing asyncio code, async def functions, create_task/gather/TaskGroup usage, semaphores and queues, async generators and streams, blocking-call audits, or debugging hangs, orphaned tasks, swallowed cancellations, and unraisable async warnings.
license: MIT
metadata:
  author: python-async-best-practices
  version: "1.0.0"
  pythonVersion: ">=3.11"
---

# Python Async Best Practices

Guidelines for writing and reviewing asyncio code. 5 rules in 1 category, prioritized by impact.

A rule match is a signal, not a verdict. These failures typically pass single-request smoke tests and surface under load — weigh the rule against the code's real concurrency profile.

Quick-reference lines are triggers, not licenses: before applying a rule as a review finding or a transformation, open the rule file and check its counter-signal — the marker-opened paragraph (`**When ...**` / `**Scope:**` / `**Keep ...**`) saying when NOT to apply it.

## When to Apply

- Writing or reviewing `async def` code, task spawning, or streaming consumers
- Auditing an async service for blocking calls or unbounded fan-out
- Debugging hangs, orphaned tasks, or unraisable warnings at teardown

## Impact Levels

- `HIGH` — stalls or silent failures affecting every task on the loop. Fix when found.
- `MEDIUM` — resource and cleanup discipline; apply to new code and code under review.

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Concurrency & Async | MEDIUM-HIGH | `async-` |

## Quick Reference

### Concurrency & Async (`async-`)

- `async-no-blocking-event-loop` — No sync I/O, sleeps, or heavy CPU in `async def`; `asyncio.to_thread` for blocking calls
- `async-own-your-tasks` — `TaskGroup` by default; hold references and cancel-then-drain longer-lived tasks
- `async-bound-concurrency` — Semaphore/queue bounds when fan-out scales with input size
- `async-generator-cleanup` — `aclosing()` / explicit `aclose()` when leaving an async generator early
- `async-preserve-cancellation` — Cancellation is control flow: cleanup, then re-raise; never a logged failure

## Related Skills

- `python-best-practices` — production Python generally; its `error-specific-exceptions` rule covers broad-catch hygiene and points here for asyncio cancellation depth.
- `python-pytest` — `determinism-sync-not-sleep` applies these ideas to concurrency *tests*.

## How to Use

Read individual rule files for detail:

```
rules/async-no-blocking-event-loop.md
rules/async-own-your-tasks.md
```

Each rule has:

- Impact level in frontmatter
- Brief explanation
- Incorrect example
- Correct example
- Optional note on edge cases

For the full compiled guide with all rules expanded: `AGENTS.md`.
