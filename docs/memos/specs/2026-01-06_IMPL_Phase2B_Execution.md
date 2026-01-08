# Phase 2B — Implementation Execution (Instruction & Checklist)

**Title:** Phase 2B — Implementation Execution Order & Guardrails
**Compiler / Steward:** Interim Consensus Steward (Project Coordinator)
**Date:** 2026-01-06

---

## Purpose
This document records the authoritative execution order, boundaries, and absolute guardrails for Phase 2B implementation. Claude Code is authorized to proceed strictly within this frame.

---

## Authority Summary
Claude Code may modify files only to implement the **Final Locked Phase 1 Consensus Digest**. Any ambiguity, conflict, or requirement beyond the locked digest must be escalated to the Consensus Steward and Architect immediately.

---

## Execution Order (MUST follow exactly)

1. **Step 1 — Environment Stabilization**
   - Pin runtime to **Python 3.12**.
   - Replace `pygame` with **`pygame-ce`** and verify prebuilt wheels on Windows.
   - Produce validated `requirements.txt` and update CI matrix to include Python 3.12+.
   - Acceptance: Clean install + smoke test run on Windows.

2. **Step 2 — Data Model Corrections**
   - Implement **view-based `int32` flags** on `float32` matrices.
   - Remove any bitwise operations on float arrays (replace `&`/`|` with `np.logical_and` / explicit casts as appropriate).
   - Add unit tests that assert dtype safety and no TypeErrors.
   - Acceptance: All tests pass and no runtime TypeErrors remain.

3. **Step 3 — Temporal Decoupling**
   - Enforce **30 Hz fixed-step simulation** and **60 Hz rendering** (decoupled).
   - Ensure monotonic timers and drift-safe step accumulation.
   - Implement LOD hysteresis (0.5s / 2.0s thresholds as locked).

4. **Step 4 — Performance Hardening**
   - Apply Numba `@njit` to hot paths (spatial grid updates, pheromone fields).
   - Eliminate Python loops in hot paths and validate via microbenchmarks.
   - Acceptance: Benchmarks meet locked performance targets.

5. **Step 5 — Rendering Compliance**
   - Use batched `Surface.blits()` and texture atlases.
   - Ensure Tier 3 Nebula entities are stateless and spawned ephemerally.
   - No per-entity Nebula rendering logic.

6. **Step 6 — Diagnostics & Validation**
   - Integrate `diagnostics.py` checks and enforce the 16.6 ms frame budget.
   - Emit warnings (not silent fixes) when budgets are violated.
   - Acceptance: Diagnostics confirm stable FPS under load.

---

## Absolute Guardrails (Halt & Escalate immediately)
- Any change that alters the three-tier architecture, illusion contract, or locked performance model.
- Any fix that requires new persistent state for entities that were specified as stateless.
- Any deviation from the locked addenda.
- If decision is ambiguous, stop and escalate—do not proceed by interpretation.

**Communication protocol:** Blocking issues -> Consensus Steward; no side-channel decisions; commits must map to execution steps.

---

## Implementation Checklist (to be ticked per Step)
- [ ] Step 1 — Environment Stabilization: branch created, requirements updated, CI updated, smoke tests pass on Windows.
- [ ] Step 2 — Data Model Corrections: dtype-safe views implemented, unit tests added.
- [ ] Step 3 — Temporal Decoupling: fixed-step sim, decoupled rendering, timers tested.
- [ ] Step 4 — Performance Hardening: Numba applied, benchmarks added.
- [ ] Step 5 — Rendering Compliance: batched blits, atlas usage, Tier 3 statelessness validated.
- [ ] Step 6 — Diagnostics & Validation: diagnostics integrated, frame budget validated.
- [ ] PR opened with links to Consensus Digest & Arbitration memos; specialists assigned as reviewers.

---

## Rollout & Validation
- Implementation must be merged only after specialist sign-offs (DeepSeek, Perplexity, Grok) and a successful CI run on Windows + Linux with Python 3.12.
- Post-merge: run a staging validation pass with diagnostics and visual smoke test.

---

## Escalation Contacts
- Consensus Steward (Interim): @ProjectCoordinator
- Architect: @Gemini
- Performance Guru: @DeepSeek
- Tooling: @Perplexity

---

**Compiler signature:** Interim Consensus Steward — 2026-01-06

*This document is authoritative for Phase 2B execution and must be committed to `docs/` and referenced in PRs.*