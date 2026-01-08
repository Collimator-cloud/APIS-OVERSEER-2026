# MEMO TEMPLATE

---

## METADATA

**ID:** `[YYYY-MM-DD-SHORT_NAME]`
**AUTHOR:** `[ROLE]`
**LOOP_MODE:** `EL | PML | SDL`
**TAG:** `[PERF/BIOL/ARCH/GOV/IMPL/PERC]`
**WHY:** `[Summary — HARD CAP: 140 characters maximum]`
**Tags (max 3):** `[Optional: performance | UX | governance | biology | tooling | sim]`


---

## TAG DEFINITIONS

- **PERF** — Performance optimization, benchmarks, metrics
- **BIOL** — Biological metaphors, agent lifecycle, emergence patterns
- **ARCH** — Architecture decisions, system design, structural changes
- **GOV** — Governance, process, protocol, compliance rules
- **IMPL** — Implementation details, feature development, bug fixes
- **PERC** — Perception layer, UI/UX, visual design, user feedback

---

## CONTENT SECTIONS

### 1. CONTEXT
Brief background explaining what led to this memo.

### 2. DECISION / FINDING
What was decided, discovered, or resolved.

### 3. IMPLEMENTATION
Technical details, code changes, or steps taken.

### 4. VALIDATION
How the change was verified (tests, benchmarks, visual inspection).

### 5. NEXT STEPS
Any follow-up actions or dependencies.

---

## ENFORCEMENT RULES

1. **WHY Field Constraint:**
   - Maximum length: **140 characters** (hard cap)
   - Claude Code must validate character count before saving
   - Exceeding this limit triggers truncation or rejection

2. **Filename Convention:**
   - Format: `YYYY-MM-DD_[TAG]_[SHORT_NAME].md`
   - Example: `2026-01-07_GOV_Phase5_Archive.md`

3. **Location:**
   - Triage memos: `docs/memos/triage/`
   - Spec memos: `docs/memos/specs/`
   - Governance memos: `docs/memos/governance/`

---

## EXAMPLE MEMO

**ID:** `2026-01-07-Phase5-Archive`
**AUTHOR:** `ARCHITECT`
**TAG:** `GOV`
**WHY:** `Establish archive governance to ensure memo consistency, enforce WHY cap, and maintain reconstruction speed compliance.`

### CONTEXT
Phase 5 requires formalized documentation standards to prevent context drift and ensure rapid agent reconstruction.

### DECISION
Implemented hard 140-character cap on WHY field, standardized memo naming conventions, and created mandatory directory structure.

### IMPLEMENTATION
Created `docs/templates/MEMO_TEMPLATE.md`, enforced validation in Claude Code workflow, and established governance audit protocol.

### VALIDATION
Tested character count validation, verified directory structure creation, confirmed template compliance.

### NEXT STEPS
- Integrate validation into Claude Code's memo creation workflow
- Perform quarterly governance audits
- Update PROJECT_STATE.md after each task completion

---

**LOCK CHECK:** `YES` — Template validated and ready for use.
