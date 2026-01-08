# VERSIONED CONTRACT PROTOCOL

**Phase:** Phase 7 - AI Team Optimization Experiments
**Date:** 2026-01-08
**Status:** ACTIVE

---

## PURPOSE

Versioned contracts provide structured handoff documentation between AI agents, ensuring constraint preservation, decision traceability, and rapid context reconstruction across multi-agent sessions.

**Key Innovation:** Treating agent handoffs like API contracts with versioning, preventing "constraint drift" over multiple iterations.

---

## TEMPLATE

```markdown
## VERSIONED CONTRACT v[X.Y]

**Version:** X.Y (major.minor - increment on significant changes)
**Date:** YYYY-MM-DD HH:MM
**Track:** [Bee / Orchestration / Both] + Time Allocation: [Bee: X% / Orchestration: Y% / Overhead: Z%]
**Priority:** [Primary track focus for this session]
**From Agent:** [Agent Name/Role]
**To Agent:** [Agent Name/Role] or "Next Session"
**Session Duration:** [Time spent on task]

### CONSTRAINTS
Hard constraints that MUST be preserved:
- [Constraint 1] — Evidence: [file:line or commit hash]
- [Constraint 2] — Evidence: [file:line or commit hash]
- [Constraint 3] — Evidence: [file:line or commit hash]

### DECISIONS
Key decisions made in this session with traceable evidence:
- [Decision 1] — Commit: [hash] — Rationale: [why]
- [Decision 2] — Evidence: [file:line] — Rationale: [why]

### STATE
Current performance metrics and system status:
- Frame Time: [X.XX]ms (target: ≤8ms)
- Bee Count: [N] (target: [M])
- Memory Usage: [X]MB (baseline: [Y]MB, limit: +5MB)
- Test Status: [PASS/FAIL] — [test_name]

### NEXT
Specific, measurable next actions (prioritized):
1. [Action 1] — Expected outcome: [measurable result]
2. [Action 2] — Expected outcome: [measurable result]
3. [Action 3] — Expected outcome: [measurable result]

### METRICS (Phase 7)

#### Bee Track Metrics:
- Frame Time @ Scale: [X.XX]ms @ [N] bees (target: ≤8ms)
- Memory Scaling Factor: [X.XX]MB per 1000 bees
- Bee Joy Index (BJI): [1-5] (Coordinator: [N], Agent: [N])
- Feature Progress: [Features completed this session]

#### Orchestration Track Metrics:
- Constraint Preservation (CSR): [N/M constraints intact from previous session]
- Velocity Efficiency (CVE): [functional LOC per 1000 tokens]
- Reconstruction Time (RTI): [seconds to full context]
- Human Decisions Required (HDL): [count this session]
- Time Allocation Balance: Bee [X]% / Orchestration [Y]% / Overhead [Z]%

### RISKS
Known risks or technical debt:
- [Risk 1] — Mitigation: [approach]
- [Risk 2] — Mitigation: [approach]

---

**Lock Check:** [YES/NO] — Next agent has sufficient context
**Contract Hash:** [First 8 chars of SHA-256 of CONSTRAINTS section]
```

---

## USAGE RULES

### When to Create a Versioned Contract
- **Required:** At end of every session (formal handoff)
- **Required:** Before major architectural changes
- **Optional:** Mid-session checkpoints for complex work

### Version Numbering
- **Major (X):** Increment when constraints change or major decisions made
- **Minor (Y):** Increment for status updates without constraint/decision changes

### Constraint Documentation
- List ALL active red lines from PROJECT_STATE.md
- Add session-specific constraints (e.g., "Do not modify pheromone grid size")
- Include file:line references or commit hashes for verification

### Evidence Requirements
- Every constraint must have verifiable evidence
- Decisions must reference commits or file locations
- Use git commit hashes (first 8 chars) for traceability

---

## MEASUREMENT FRAMEWORK

### Constraint Preservation Rate
**Formula:** `(Constraints intact after N handoffs) / (Total constraints at start) × 100`

**Collection Method:**
1. Hash constraints section at contract creation
2. Next agent verifies constraints against current codebase
3. Report violations in new contract's METRICS section

**Target:** ≥95% preservation across 3+ handoffs

### Velocity Efficiency
**Formula:** `(Functional lines of code added/modified) / (Total tokens in session) × 1000`

**Collection Method:**
1. Track token usage via API/SDK metrics
2. Use `git diff --stat` for LOC changes
3. Exclude comments, docs, whitespace (functional code only)

**Target:** TBD (establish baseline over 3 sessions)

### Reconstruction Index
**Formula:** Time (seconds) for incoming agent to understand current state

**Collection Method:**
1. New agent reports time from reading CONTRACT to "ready to work"
2. Includes reading referenced files/commits
3. Excludes time waiting for human input

**Target:** <30s (2× the Phase 5 target for added complexity)

### Human Decision Load
**Formula:** Count of questions or decisions requiring human input per hour

**Collection Method:**
1. Track AskUserQuestion tool calls
2. Track explicit "awaiting human decision" states
3. Normalize to per-hour rate

**Target:** ≤3 decisions/hour (goal: autonomous work within constraints)

---

## EXAMPLE CONTRACT

```markdown
## VERSIONED CONTRACT v1.0

**Version:** 1.0
**Date:** 2026-01-08 14:35
**From Agent:** Claude Sonnet 4.5 (Builder)
**To Agent:** Next Session (Supervisor-Worker Pattern)
**Session Duration:** 45 minutes

### CONSTRAINTS
- Velocity Magnitude Lock — Evidence: [simulation.py:437-440](simulation.py#L437-L440)
- Frame Time ≤8ms baseline — Evidence: [PROJECT_STATE.md:52](PROJECT_STATE.md#L52)
- Debug Budget ≤1.0ms — Evidence: [PROJECT_STATE.md:56](PROJECT_STATE.md#L56)
- Pheromone grid 128×128 (fixed) — Evidence: [config.py:85](config.py#L85)

### DECISIONS
- Created Phase 7 docs structure — Commit: 9f4a97b — Rationale: Prepare for orchestration experiments
- Established versioned contract protocol — Evidence: [docs/phase7/versioned_contracts.md](docs/phase7/versioned_contracts.md) — Rationale: Reduce constraint drift

### STATE
- Frame Time: 5.67ms (target: ≤8ms) ✅
- Bee Count: 2000 (target: 5000 in Phase 7)
- Memory Usage: TBD (baseline to be established)
- Test Status: PASS — test_phase4.py (600 frames)

### NEXT
1. Scale to 3000 bees — Expected: ≤7ms frame time maintained
2. Profile memory usage baseline — Expected: Establish +5MB limit reference
3. Implement first advanced behavior (waggle dance or guard behavior) — Expected: Observable emergent pattern

### METRICS (Phase 7)
- Constraint Preservation: 4/4 (100% - first session, no prior handoff)
- Velocity Efficiency: TBD (baseline session)
- Reconstruction Time: TBD (awaiting next agent measurement)
- Human Decisions Required: 0 (preparation work, no ambiguity)

### RISKS
- Memory usage unknown at scale — Mitigation: Profile before scaling to 5000
- Advanced behaviors may conflict with performance budget — Mitigation: Prototype with small subset first

---

**Lock Check:** YES — All Phase 7 infrastructure documented
**Contract Hash:** a3f7b2e1
```

---

## INTEGRATION WITH EXISTING PROTOCOLS

### Relationship to Chronicle Entries
- **Chronicle:** High-level evolution tracking (140-char WHY)
- **Versioned Contract:** Detailed handoff with evidence and metrics
- **Use both:** Chronicle for historical record, Contract for active work

### Relationship to HANDOFF_TEMPLATE.md
- Versioned contracts REPLACE informal handoffs
- Handoff template remains for non-experimental phases
- Phase 7+ uses versioned contracts exclusively

### Relationship to PROJECT_STATE.md
- PROJECT_STATE.md remains single source of truth
- Versioned contracts reference it (don't duplicate)
- Contracts add session-specific context and evidence

---

## FAILURE MODES & MITIGATIONS

### Contract Bloat
**Symptom:** Contracts exceed 500 lines, take >5min to write
**Mitigation:** Use references instead of duplication, prune stale constraints

### Evidence Rot
**Symptom:** File:line references break due to refactoring
**Mitigation:** Prefer commit hashes for decisions, update references when noticed

### Metric Gaming
**Symptom:** Agents optimize for metrics instead of actual progress
**Mitigation:** Human review of contracts, qualitative assessment alongside metrics

### Version Chaos
**Symptom:** Unclear when to increment major vs minor version
**Mitigation:** Strict rule: constraints/decisions = major, status only = minor

---

## VALIDATION CHECKLIST

Before finalizing a versioned contract:
- [ ] All constraints have evidence (file:line or commit hash)
- [ ] All decisions have rationale
- [ ] STATE metrics are current and accurate
- [ ] NEXT actions are specific and measurable
- [ ] Phase 7 metrics are calculated and included
- [ ] Lock Check is YES or NO with justification
- [ ] Contract hash is computed and included

---

**END OF PROTOCOL**

*This document is the authoritative specification for versioned contracts in Phase 7.*
*When in doubt, consult this template and adapt to context.*
