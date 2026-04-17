---
name: python-best-practices
description: Python software engineering guidelines from real PR review patterns. This skill should be used when writing, reviewing, or refactoring Python code — especially dataclasses, service interfaces, error handling, and type annotations. Triggers on tasks involving Python modules, API design, data modeling, type safety, exception handling, or refactoring for maintainability.
license: MIT
metadata:
  author: python-best-practices
  version: "1.1.0"
  pythonVersion: ">=3.11"
---

# Python Best Practices

Comprehensive guidelines for Python codebases that must resist drift over time. 60+ rules across 8 categories, prioritized by impact to guide automated refactoring and code generation.

The rules codify the failure modes agents fall into: reaching for `Any`, stacking optional fields into grab-bag models, catching bare `except:`, using mutable defaults, and bypassing type checkers with `# type: ignore`. Each rule names the impulse, shows the failure, and points at the better path.

## When to Apply

Reference these guidelines when:

- Writing new Python modules, functions, classes, or data models
- Designing public APIs, Protocol interfaces, or service boundaries
- Reviewing code for type safety, clarity, or maintainability
- Refactoring dataclasses, Pydantic models, or state-management patterns
- Adding exception handling, validation, or error paths
- Optimizing hot paths for performance

## Python Version Baseline

Rules assume **Python 3.11+** as the floor (for `assert_never`, `Self`, exception groups, `tomllib`). Rules that depend on a higher version call it out inline:

- `warnings.deprecated()` — 3.13+
- `zoneinfo` — 3.9+
- Union types in `isinstance()` — 3.10+
- `assert_never` — 3.11+ (use `typing_extensions` to backport)

Rules tagged `applicability:pydantic` are Pydantic-specific.

## Rule Categories by Priority

| Priority | Category               | Impact       | Prefix      |
|----------|------------------------|--------------|-------------|
| 1        | Data Modeling          | CRITICAL     | `data-`     |
| 2        | Type Safety            | CRITICAL     | `types-`    |
| 3        | API Design             | HIGH         | `api-`      |
| 4        | Error Handling         | HIGH         | `error-`    |
| 5        | Code Simplification    | MEDIUM-HIGH  | `simplify-` |
| 6        | Performance            | MEDIUM       | `perf-`     |
| 7        | Naming                 | MEDIUM       | `naming-`   |
| 8        | Imports & Structure    | LOW-MEDIUM   | `imports-`  |

## Quick Reference

### 1. Data Modeling (CRITICAL)

- `data-derive-dont-store` — Compute from evidence; don't cache flags that mirror each other
- `data-discriminated-unions` — Replace optional bags with tagged variants; make impossible states impossible
- `data-explicit-variants` — Concrete classes per mode beat one class with `is_thread`/`is_edit`/`is_forward` flags
- `data-phased-composition` — Group co-present optional fields into one nested optional, not eight siblings
- `data-mutation-contract` — Mutate OR return; never both (callers can't tell which to use)
- `data-encapsulate-mutable-state` — Trap mutable state in the **narrowest clear scope** — closure, focused class, or instance attribute as the case demands
- `data-mutable-defaults` — Never `def f(items=[])`; use `None` + body construction or `default_factory`
- `data-sentinel-when-none-is-valid` — Use a private sentinel when `None` is itself a meaningful domain value
- `data-aware-datetimes` — Timezone-aware `datetime.now(timezone.utc)` at every boundary; `datetime.utcnow()` is deprecated
- `data-delete-dead-variants` — Remove union/enum branches that are never constructed
- `data-newtype-for-ids` — Brand primitive IDs (`NewType('UserId', str)`) so they aren't interchangeable

### 2. Type Safety (CRITICAL)

- `types-avoid-any` — Precise types (Protocol, TypeVar, Union) over `Any`
- `types-typeddict-over-dict-any` — `TypedDict`/dataclass instead of `dict[str, Any]` when structure is known
- `types-isinstance-for-narrowing` — `isinstance()` for type checks; not `hasattr`/`getattr`/`type(x).__name__`
- `types-literal-for-fixed-sets` — `Literal["a", "b"]` for fixed string sets; not plain `str`
- `types-fix-errors-not-ignore` — Fix type errors; `# type: ignore` should be a last resort with justification
- `types-fix-types-not-cast` — Fix the type definition; `cast()` only when runtime logic genuinely narrows
- `types-remove-redundant-optional` — Drop `| None` when values are guaranteed present
- `types-type-checking-imports` — `if TYPE_CHECKING:` for optional deps; keep hints without runtime import
- `types-narrow-to-runtime-reality` — Annotations should match what control flow actually lets through
- `types-trust-the-checker` — Remove redundant runtime checks when types already constrain the value

### 3. API Design (HIGH)

- `api-required-before-optional` — Required fields before optional in dataclasses (Python enforces this)
- `api-keyword-only-params` — `*` or `KW_ONLY` marker for optional/config params to prevent breakage
- `api-no-boolean-flag-params` — `Literal`/`Enum` over positional `True, False` soup; split functions when bodies barely overlap
- `api-underscore-for-private` — `_prefix` for internals; exclude from `__all__`
- `api-immutable-transforms` — Return new collections; don't mutate inputs (unless named `update_*` / `*_inplace`)
- `api-deprecated-aliases` — `warnings.deprecated()` (3.13+) for renamed funcs/classes; compatibility kwargs + `warnings.warn` for renamed parameters
- `api-no-private-access` — Don't reach into `_prefixed` names from outside the module
- `api-model-cohesion` — Keep models flat; avoid duplicate/single-key-wrapped/redundant fields
- `api-instance-vs-module-fn` — Pick the simplest namespace that matches ownership and polymorphism

### 4. Error Handling (HIGH)

- `error-no-bare-except` — `except:` catches `KeyboardInterrupt`/`SystemExit`/`CancelledError`; never use it
- `error-specific-exceptions` — Catch specific types; `except Exception:` only at outer-loop log-and-reraise sites
- `error-context-managers` — `with` / `async with` for files, locks, sessions, temp dirs; not manual `close()`
- `error-consolidate-try-except` — Merge blocks that catch the same exception with similar handling
- `error-assert-debug-only` — `assert` is stripped under `-O`; only use it for debug-only invariants
- `error-assert-never-exhaustiveness` — `typing.assert_never` for exhaustiveness checks (3.11+)
- `error-validate-at-boundaries` — Validate input before expensive work; fail fast at system edges
- `error-inherit-base-exceptions` — New exceptions inherit from existing bases for backward compatibility
- `error-repr-in-messages` — `f"tool {name!r}"` for identifiers in error text; consistent quoting
- `error-raise-from-for-chains` — `raise NewErr(...) from original` to preserve causality
- `error-trust-validated-state` — Trust validated, immutable, locally-constructed state in the same trust domain; keep checks for mutable/external/rehydrated objects
- `error-preserve-cancellation` — `CancelledError` is `BaseException` on 3.8+; don't false-flag `except Exception:` for "swallowing cancellation"

### 5. Code Simplification (MEDIUM-HIGH)

- `simplify-comprehensions` — Comprehensions over `for` + `.append()` / `dict()` + update
- `simplify-any-all-builtins` — `any()`/`all()` over manual flag + `break`
- `simplify-fallback-or` — `x or default` over verbose `if`/`else` (when falsy values aren't semantic)
- `simplify-inline-single-use-vars` — Drop `_filtered`, `_copy` intermediates that are used once
- `simplify-flatten-nested-if` — Combine into `if cond1 and cond2:` when there's no intervening code
- `simplify-cached-property` — `@cached_property` for derived attrs on **immutable** instances with `__dict__`; not thread-safe
- `simplify-extract-after-duplication` — Extract helpers once a pattern repeats; don't copy-paste a third time
- `simplify-remove-dead-code` — Delete commented-out code and unused definitions; git preserves history
- `simplify-early-return` — Return early; don't nest the happy path three levels deep

### 6. Performance (MEDIUM)

- `perf-compile-regex-module-level` — Compile static regex at module scope; not inside hot functions
- `perf-type-adapter-constant` — Define Pydantic `TypeAdapter` instances at module scope *(applicability: pydantic)*
- `perf-set-for-membership` — `set` for repeated `in` checks; O(1) beats `list.__contains__`
- `perf-dict-index-over-nested-loops` — Build a `dict` for lookups; not nested `for` + `if`
- `perf-generator-over-list` — Stream with generators when memory or first-result latency matters; lists are fine when you re-iterate or need `len()`
- `perf-lru-cache-pure-fns` — `functools.lru_cache` / `functools.cache` for pure functions
- `perf-isinstance-tuple-syntax` — Tuple form is marginally faster; **only rewrite on profiled hot paths**, not as a stylistic crusade
- `perf-combine-iterations` — Fuse `filter` + `map` into one pass when possible

### 7. Naming (MEDIUM)

- `naming-drop-redundant-prefixes` — `ToolConfig.description` over `ToolConfig.tool_description`
- `naming-specific-over-generic` — `toolset_id`, `memory_id`; not bare `id`, `name`, `data`
- `naming-rename-on-behavior-change` — Rename when behavior changes; stale names mislead
- `naming-no-type-suffixes` — No `_dict`, `_list`, `_str` suffixes; types annotate types
- `naming-upper-case-constants` — `MAX_RETRIES`; prefix with `_` for internal (`_DEFAULT_TIMEOUT`)
- `naming-consistent-terminology` — Same concept, same word across code/docs/errors

### 8. Imports & Structure (LOW-MEDIUM)

- `imports-top-of-file` — Imports at the top by default; documented exceptions for circular imports, optional heavy deps, and side-effect deferral
- `imports-no-side-effects` — Modules must be cheap to import — no network calls, model loads, env reads, or registrations at import time
- `imports-optional-dependencies` — `try`/`except ImportError` with helpful install hints
- `imports-remove-unused` — Delete unused imports; keep module namespace tight
- `imports-no-duplicates` — One import per name
- `imports-scope-helpers-to-usage` — Define helpers near where they're used; not at module level "just in case"

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/data-derive-dont-store.md
rules/types-avoid-any.md
```

Each rule file contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Primary-source `references` (PEPs, stdlib docs, library docs) when version- or library-dependent
- Closing notes on edge cases or applicability

## Authoring & Maintenance

The skill ships with a build/validate/extract-tests pipeline (see `README.md`):

- `python src/build.py` — compile rules into `AGENTS.md`
- `python src/validate.py` — lint frontmatter, references, and example structure
- `python src/extract_tests.py` — generate `test-cases.json` for LLM evals

Rule files live under `rules/`; `AGENTS.md` and `test-cases.json` are generated outputs.

## Full Compiled Document

For the complete guide with every rule expanded: `AGENTS.md`. Note that `AGENTS.md` is large by design (every rule body) — agents can grep individual rule files in `rules/` instead when only one or two rules are relevant.
