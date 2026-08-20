# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

Section impact is a typical-case label. Individual rules range one level above or below the section — check each rule's frontmatter.

---

## 1. Test Value (value)

**Impact:** HIGH  
**Description:** What deserves to be a committed test. Observable contracts over execution probes, independent oracles over implementation echoes. A test that can't fail for a real reason is weight, not coverage.

## 2. Determinism (determinism)

**Impact:** HIGH  
**Description:** Tests that pass for reasons. Event-based synchronization over sleeps, strict xfail, no flake-masking retries. Nondeterminism hidden today is a debugging session later.

## 3. Fixtures & Isolation (fixtures)

**Impact:** MEDIUM-HIGH  
**Description:** State that comes back clean. Narrowest fixture scope, restored globals, canonical object construction. Leaked state makes test order a hidden input.

## 4. Mocking (mock)

**Impact:** MEDIUM-HIGH  
**Description:** Fakes that prove something. Mock at owned IO boundaries, patch where names are looked up, assert wire representations. A test fully determined by its mocks tests the mocks.

## 5. Structure & Execution (structure)

**Impact:** MEDIUM  
**Description:** The suite as a system. Contract-distinct parametrization, collision-free module identities, deliberate plugin surface, preserved exit codes. Collection-time and CI-time failure modes live here.
