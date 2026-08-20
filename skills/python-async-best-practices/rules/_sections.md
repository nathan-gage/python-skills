# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

Section impact is a typical-case label. Individual rules range one level above or below the section — check each rule's frontmatter.

---

## 1. Concurrency & Async (async)

**Impact:** MEDIUM-HIGH  
**Description:** Event-loop discipline. Blocking calls, task ownership, bounded fan-out, deterministic stream cleanup. These failures pass single-request smoke tests and surface under load.
