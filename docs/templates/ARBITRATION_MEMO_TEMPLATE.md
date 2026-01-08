# Arbitration Memo Template

**Title:** [Short, descriptive title]
**Memo ID:** [AUTO-ASSIGNED]
**Author (Compiler):** [Name / Role]
**Date:** [YYYY-MM-DD]
**Scope:** [e.g., "Phase 1 → Phase 2 consensus arbitration on <topic>"]

---

## Purpose

One-sentence summary of what this arbitration memo resolves and why arbitration is required.

## Context

Short background: reference the primary memo and the set of addenda (IDs/list) that triggered arbitration.

## Decisions to be Made

- Decision D1: [Short description of the decision question]
- Decision D2: [Short description]

Each decision should include: required outcome options, constraints, and any dependency on other decisions.

## Arbitration Rules (Process)

1. **Primary owners and reviewers:** List specialists responsible for each domain (e.g., DeepSeek for performance).  
2. **Timeline:** Specify decision window (e.g., 72 hours for minor, 1 week for moderate, 2 weeks for architectural).  
3. **Evidence required:** Tests, benchmarks, reproducer, or spec that must accompany arguments.  
4. **Conflict resolution:** If conflicting mandatory addenda exist, a decision is reached by:  
   - Specialist majority (if applicable) OR  
   - Architect tie-break (if change impacts system contract).  
5. **Sign-off:** Decisions require at least one specialist and the Compiler sign-off; architectural escalations require Architect approval.

## Evaluation Criteria

- **Mandatory compliance:** Does the candidate solution satisfy all MANDATORY addenda? (yes/no)
- **Behavioral/Perceptual acceptance:** Tests or visual checks owned by The Brain.  
- **Performance:** Benchmarks and acceptable deltas defined by DeepSeek.  
- **Tooling/Environment:** Perplexity validates installability and CI integrations.

## Proposed Options / Recommendation

List 2–3 candidate solutions per decision, each with: short description, trade-offs, tests, and estimated implementation cost (low/med/high).

### Example format

**Option A — Quick fix:** [summary]
- Pros: [list]
- Cons: [list]
- Tests required: [unit/benchmark/visual]
- Est. effort: [low/med/high]

**Option B — Robust fix:** [summary]
- Pros:
- Cons:
- Tests required:
- Est. effort:

## Verdict Format (final record)

For each decision, record:
- Decision ID: [D1]
- Chosen option: [A/B/C]
- Rationale: [1–2 sentences]
- Tests added: [links to tests/PRs]
- Sign-offs: [@DeepSeek, @Perplexity, @Architect]
- Implementation owner: [@Claude]

## Timeline & Rollout

- Implementation deadline: [YYYY-MM-DD]
- Rollout plan & version tagging
- Backout plan (if needed)

## Follow-ups & Dependencies

List follow-up tasks and who owns them.

## Appendices

- Links to primary memo, all addenda (with IDs), relevant PRs, test artifacts, logs, and benchmarks.

---

**Compiler signature:** [Name — YYYY-MM-DD]

**Notes:** Use this memo to produce a single PR that implements accepted changes and attaches the `Consensus Digest` as an artifact.