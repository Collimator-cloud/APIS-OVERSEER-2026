# Phase 0 → Phase 1 Consensus Digest Template

**Digest Title:** [Primary Memo Title] — Phase 1 Consensus Digest
**Digest ID:** [AUTO-ASSIGNED]
**Compiler:** [Name / Role]
**Compilation Date:** [YYYY-MM-DD]
**Related Memo:** [link to primary memo]

---

## Summary
- **Primary proposal (1–2 lines):**
- **Response window:** [start — end]
- **Total addenda received:** [N]
- **Primary conflicts identified:** [brief list]

---

## Addenda (canonical list)
Each submitted addendum is recorded as an entry below in the exact submitted format.

Addendum format (recorded):
- **AD-ID:** AD-XXX
- **Author:** @name (Role)
- **Category:** [MANDATORY | RECOMMENDED | OPTIONAL]
- **Domain:** [Architecture | Performance | Tooling / Environment | Simulation Logic | Rendering / Perception | Process / Governance]
- **Statement:** [1–3 sentences, verbatim recorded]
- **Failure Mode if Ignored:** [1 sentence]
- **Link:** [link to issue/entry]


---

## Conflicts & Overlaps
- **Conflict C1:** [Brief description of conflict between AD-001 and AD-007]
  - Affected addenda: [AD-001, AD-007]
  - Stakes: [e.g., both marked MANDATORY and mutually exclusive]
  - Proposed arbitration owner: [e.g., DeepSeek / Architect]
  - Recommended evidence to resolve: [tests/benchmarks/logs]

Repeat for each conflict.

---

## Decisions & Verdicts (final records)
For every addendum, record the final action and rationale.

Entry format:
- **AD-ID:** AD-XXX
- **Decision:** [ACCEPTED | MODIFIED | REJECTED | DEFERRED]
- **Rationale:** [1–2 sentences summarizing why]
- **Implementation PR:** [link or N/A]
- **Tests added:** [link to unit/visual/benchmark tests]
- **Sign-offs:** [@DeepSeek, @Perplexity, @Grok, @Architect (if required)]

Example:
- **AD-002** — **Decision:** ACCEPTED
  - **Rationale:** Satisfies performance constraint with minimal change; unit tests verify behavior with float32 inputs.
  - **Implementation PR:** #12
  - **Tests added:** tests/test_masks_dtype.py
  - **Sign-offs:** @DeepSeek (ok), @Claude (ack)

---

## Merged Changes (Actionable items for Claude Code)
- **Change A:** File / module — `path/to/file.py`
  - **Summary:** [what was changed]
  - **Related addenda:** [AD-xxx]
  - **PR:** [link]
  - **Est. effort:** [low/med/high]

List all concrete changes accepted for implementation.

---

## Rejected / Deferred Items
- **AD-00X:** [Summary]
  - **Reason:** [why rejected or deferred]
  - **Suggested alternative (if any):** [Optional]

---

## Tests, Benchmarks & Visuals
- Unit tests: [links]
- Benchmarks: [links and summary of results & acceptable thresholds]
- Visual validation: [screenshots / links to rendered outputs]

---

## Sign-offs (final approvals)
- Compiler: @Name (date)
- Specialists: @DeepSeek (date), @Perplexity (date), @Grok (date), @ChatGPT (date)
- Architect (if required): @Gemini (date)

---

## Rollout & Backout Plan
- **Version:** [e.g., v0.1.0]
- **Implementation deadline:** [YYYY-MM-DD]
- **Rollout steps:**
  1. Merge implementation PRs
  2. CI / smoke tests (include x, y, z)
  3. Deploy to staging for visual verification
  4. Release
- **Backout steps:** [how to revert if issues found]

---

## Appendices & Links
- Primary memo link
- All addenda issue links (list)
- Arbitration memos and decision PRs
- Test artifacts and benchmark logs

---

**Compiler notes:** [Optional: notes about unresolved edge cases, caveats, or next review date]

**Compiler signature:** [Name — YYYY-MM-DD]
