# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Data Modeling (data)

**Impact:** CRITICAL
**Description:** The architectural foundation. Deriving values instead of storing them, using discriminated unions instead of optional bags, making mutation contracts explicit. Mistakes here compound into state nobody intended.

## 2. Type Safety (types)

**Impact:** CRITICAL
**Description:** Precise types catch bugs at type-check time and keep IDE autocomplete useful. The type checker is load-bearing — keep it that way. No `Any` drift, no `# type: ignore` without justification.

## 3. API Design (api)

**Impact:** HIGH
**Description:** Interface decisions that compound over years. Keyword-only parameters, private underscores, immutable transforms. The difference between an API that ages well and one that accumulates compatibility shims.

## 4. Error Handling (error)

**Impact:** HIGH
**Description:** Sloppy exceptions hide bugs; good exceptions localize them. Catch specific types, validate at boundaries, preserve causality with `raise ... from`.

## 5. Code Simplification (simplify)

**Impact:** MEDIUM-HIGH
**Description:** Python idioms that reduce LOC and mental load. Comprehensions, `any()`/`all()`, early returns, removing dead code. The rules that let Python read like Python.

## 6. Performance (perf)

**Impact:** MEDIUM
**Description:** Python-specific optimizations that matter on hot paths. Module-level compilation, set/dict lookups, cached properties. Not premature — applied where the hot path is measured.

## 7. Naming (naming)

**Impact:** MEDIUM
**Description:** Names are the most-read interface in any codebase. Specific over generic, consistent terminology, no type suffixes that duplicate annotations.

## 8. Imports & Structure (imports)

**Impact:** LOW-MEDIUM
**Description:** Module hygiene. Imports at the top, optional dependencies handled explicitly, no duplicates or unused names.
