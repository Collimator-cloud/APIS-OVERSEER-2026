# 🔄 AGENT HANDOFF TEMPLATE

**Purpose:** Ensure seamless context transfer between AI agents in the APIS-OVERSEER project.

**Compliance:** This template enforces invariant [ARCH-COMM-02] (15s Reconstruction Goal) and [ARCH-COMM-03] (Chronicle Schema).

---

## 📋 HANDOFF CHECKLIST

Use this checklist when ending your session:

- [ ] Updated [PROJECT_STATE.md](../PROJECT_STATE.md) "Last Updated" field
- [ ] Added entry to Chronicle (📜 Recent Evolutions section)
- [ ] Verified Chronicle entry ≤140 characters in WHY field
- [ ] Completed LOCK CHECK verification
- [ ] Committed/saved all code changes
- [ ] Updated performance metrics if changed
- [ ] Documented any new red lines or invariants

---

## 📝 HANDOFF FORMAT

```markdown
## HANDOFF: [Your Role] → [Next Role/Agent]

**Date:** YYYY-MM-DD
**Outgoing Agent:** [e.g., Claude Sonnet 4.5 (Builder)]
**Incoming Agent:** [e.g., Gemini 2.5 Pro (Architect)] or "TBD"
**Session Duration:** [e.g., 45 minutes]

---

### What I Did (Summary)
[2-3 sentences describing completed work]

---

### Chronicle Entry Added
**ID:** [e.g., 002]
**Tag:** [PERF/PERC/BIOL/GOVERNANCE]
**WHY:** [Max 140 chars - what changed and why it matters]

---

### Files Modified/Created
- [ ] [file1.py](../file1.py) - Brief description
- [ ] [file2.py](../file2.py) - Brief description
- [ ] [docs/report.md](report.md) - Brief description

---

### Performance Impact
**Before:** [e.g., 5.67ms avg frame time]
**After:** [e.g., 5.82ms avg frame time]
**Change:** [e.g., +0.15ms due to new feature X]
**Budget Status:** ✅ PASS / ⚠️ WARNING / 🚨 CRITICAL

---

### Open Questions / Blockers
[List any unresolved decisions or blockers for next agent]
- Question 1
- Question 2

If none: "None - all work complete and validated."

---

### LOCK CHECK
**Status:** ✅ YES / ❌ NO

**Required Context for Next Agent:**
- [ ] [PROJECT_STATE.md](../PROJECT_STATE.md) updated
- [ ] [Memo/report name if applicable]
- [ ] [Link to relevant spec or design doc]

**Verification:**
[Confirm next agent can reconstruct context in ≤15 seconds using above documents]

---

### Recommendations for Next Session
[Optional - suggest next steps or priorities]
1. Step 1
2. Step 2

---

**Signature:**
[Your Agent Name/Role]
[Date]
```

---

## 🎯 QUICK HANDOFF (For Routine Updates)

If you only made minor changes (bug fix, small optimization), use this abbreviated format:

```markdown
## QUICK HANDOFF

**Agent:** [Your name]
**Date:** YYYY-MM-DD
**Change:** [One-sentence description]
**Chronicle ID:** [e.g., 003]
**Files:** [file1.py, file2.py]
**Performance:** No change / +X ms
**LOCK CHECK:** ✅ YES
```

---

## 📏 CHRONICLE SCHEMA REFERENCE

Every Chronicle entry must follow this format:

```
ID | DATE | ROLE | TAG [PERF/PERC/BIOL/GOVERNANCE] | WHY (max 140 chars) | LOCK CHECK [YES/NO]
```

**Example:**
```
002 | 2026-01-07 | BUILDER | [PERF] | Optimized pheromone blur kernel, reduced frame time by 0.3ms. | ✅ YES
```

**Tags:**
- `[PERF]` - Performance optimization or profiling change
- `[PERC]` - Perceptual/visual change (rendering, UX)
- `[BIOL]` - Biological behavior or realism change
- `[GOVERNANCE]` - Protocol, invariant, or process change

---

## ⚠️ LOCK CHECK REQUIREMENTS

**LOCK CHECK: YES** means ALL of the following are true:
1. PROJECT_STATE.md reflects current project state
2. All relevant memos/reports are linked in Chronicle entry
3. Performance metrics are up-to-date
4. Next agent can reconstruct context in ≤15 seconds
5. No critical decisions are left undocumented

**LOCK CHECK: NO** means handoff is incomplete. This triggers a 10-minute grace period before performance budgets re-enforce (per [ARCH-COMM-04]).

---

## 🚨 EMERGENCY HANDOFF

If you must leave mid-task due to error, timeout, or blocker:

```markdown
## EMERGENCY HANDOFF

**Agent:** [Your name]
**Date:** YYYY-MM-DD
**Status:** 🚨 INCOMPLETE
**Reason:** [e.g., Timeout, critical error, awaiting human decision]

**Incomplete Work:**
- [ ] Task 1 (50% done)
- [ ] Task 2 (not started)

**Critical Context:**
[What the next agent MUST know to continue]

**Files in Unstable State:**
- [file1.py](../file1.py) - Description of issue

**LOCK CHECK:** ❌ NO (emergency context only)

**Next Agent Action:**
[Specific first step to resume or rollback]
```

---

## 📖 EXAMPLE HANDOFF

```markdown
## HANDOFF: Builder → Architect

**Date:** 2026-01-07
**Outgoing Agent:** Claude Sonnet 4.5 (Builder)
**Incoming Agent:** Gemini 2.5 Pro (Lead Architect)
**Session Duration:** 30 minutes

---

### What I Did (Summary)
Implemented the "Hive Mind" communication infrastructure per architect specification. Created PROJECT_STATE.md as the authoritative status page, established Chronicle schema, and built handoff automation templates.

---

### Chronicle Entry Added
**ID:** 001
**Tag:** [GOVERNANCE]
**WHY:** Locked Phase 4 communication rituals & failover budgets.

---

### Files Modified/Created
- [x] [PROJECT_STATE.md](../PROJECT_STATE.md) - Authoritative project status page
- [x] [docs/HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) - Agent transition template
- [ ] [simulation.py](../simulation.py) - Pending: Diagnostic check for PROJECT_STATE.md

---

### Performance Impact
**Before:** 5.67ms avg frame time
**After:** 5.67ms avg frame time (no simulation changes)
**Change:** 0ms (documentation only)
**Budget Status:** ✅ PASS

---

### Open Questions / Blockers
- Should diagnostic check halt simulation or just warn if PROJECT_STATE.md is missing?
- Waiting for architect decision on Phase 5 specification.

---

### LOCK CHECK
**Status:** ✅ YES

**Required Context for Next Agent:**
- [x] [PROJECT_STATE.md](../PROJECT_STATE.md) updated with Chronicle 001
- [x] [docs/HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) created
- [x] [PHASE4_IMPLEMENTATION_REPORT.md](../PHASE4_IMPLEMENTATION_REPORT.md) (baseline context)

**Verification:**
Incoming architect can read PROJECT_STATE.md (10s) + Chronicle entry (3s) = 13s total reconstruction time. ✅ Meets 15s goal.

---

### Recommendations for Next Session
1. Review communication infrastructure for approval
2. Specify diagnostic behavior (halt vs warn)
3. Begin Phase 5 design when ready

---

**Signature:**
Claude Sonnet 4.5 (Builder)
2026-01-07
```

---

**End of Template**
*Use this template for every agent transition to maintain the "Hive Mind" protocol.*
*When in doubt, prefer over-documentation to under-documentation.*
