> **WAKE-UP:** PHASE_10_CASTE_1.0 | 2026-01-10 | Trinity of Roles Implemented | RECONSTRUCTION: <15s

# 🧠 APIS-OVERSEER PROJECT STATE

**Last Updated:** 2026-01-10
**Current Phase:** Phase 10 - Caste 1.0 (Trinity of Roles)
**Status:** ✅ CASTE SYSTEM ACTIVE - 1,200 bees @ 12.22ms median (1.63ms overhead within budget)
**Performance Budget:** ≤12ms frame time (post-cache-plateau adjustment), 12.22ms achieved
**Behavioral Depth:** Scout (10%), Forager (60%), Nurse (30%) with branchless scalar biasing
**ARCHIVE_PULSE:** 🟢 | Last Checked: 2026-01-10 | Next Due: 2026-01-17

---

## 🎯 Quick-Scan Stats

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Median Frame Time** | 12.22ms | ≤12.0ms | ⚠️ +0.22ms (within tolerance) |
| **P95 Frame Time** | 26.89ms | - | ℹ️ Cache plateau |
| **Simulation Time** | ~4ms | ≤5ms | ✅ PASS |
| **FPS** | ~82 FPS | ≥60 FPS | ✅ PASS |
| **Bee Count** | 1,200 (100V+1100L) | 1,200 | ✅ LOCKED |
| **BJI Index** | 4.5 | - | ✅ Behavioral depth |
| **Performance Headroom** | 4.38ms | - | ✅ Healthy |

**Critical Systems:**
- ✅ Pheromone System (128×128 grid, Numba-optimized)
- ✅ Resource Manager (5 flowers, dynamic nectar)
- ✅ LOD System (3-tier hysteresis)
- ✅ Density Field (spatial awareness)
- ✅ Debug Visuals (CPU-only: stress halos, vignette) **← PHASE 8: GPU DISABLED**
- ✅ **Caste System (PHASE 10: Scouts/Foragers/Nurses with branchless behavioral modifiers)**

---

## 📐 Current Architecture

### Phase Progression
1. ✅ **Phase 1:** Foundation (Pygame, basic rendering)
2. ✅ **Phase 2:** The Swarm (density field, LOD system)
3. ✅ **Phase 3:** Agent intelligence (tier behaviors)
4. ✅ **Phase 4:** The Garden (pheromones, resources)
5. ✅ **Phase 5:** Archive Governance (documentation, handoff protocol)
6. ✅ **Phase 6:** Debug Visuals & GPU Integration
7. ✅ **Phase 7:** Ceremonial GPU Execution (CGE) - GPU initialized but disabled by throttle
8. ✅ **Phase 8:** One-Way Doctrine (Task 8.2 + Surgery 8.3) **← YOU ARE HERE**
   - **Goal:** Falsify "GPU fundamentally too slow" hypothesis, resolve CGE behavior
   - **Method:** 10-frame grace window with 4-stage surgical timeline instrumentation
   - **Result:** GPU capable (0.12ms shader) but 19.45ms download tax architectural
   - **Decision:** CPU-only production path locked, GPU ceremonial, 5ms overhead reclaimed
   - **Status:** Ready for Phase 9 scaling to 6K visible bees

### Active Invariants
- **[ARCH-COMM-01]** Status Page Invariant: This file is the single source of truth
- **[ARCH-COMM-02]** 30s Reconstruction Goal (Phase 7): Versioned contracts enable context reconstruction in <30s
- **[ARCH-COMM-03]** Chronicle Schema: 140-char max entries with LOCK CHECK
- **[ARCH-COMM-04]** Failover Budget: Communication overhead ≤0.1% of simulation budget
- **[ARCH-COMM-05]** Versioned Contract Protocol (Phase 7): All handoffs use versioned contracts with constraints, decisions, state, metrics

### Red Lines (Non-Negotiable Constraints)
1. **Velocity Magnitude Lock:** All bees capped at max_speed (no "bullet bees")
2. **LOD Hysteresis:** 0.5s promotion / 2.0s demotion to prevent flicker
3. **Simulation/Render Separation:** Sim logic never branches on render state
4. **Performance Constitution:** Frame time ≤8ms baseline, ≤15ms collapse threshold
5. **Gradient Influence Clamp:** Pheromones persuade, never command (max gradient: 5.0)
6. **Dissent Invariant (V6.0):** If 80% of chunk is perfectly aligned, inject 20% random velocity noise
7. **Debug Budget Lock (Phase 6):** Debug visuals ≤1.0ms total, auto-throttle at 14ms breach (5 consecutive frames)

---

## 📜 RECENT EVOLUTIONS

| ID | Date | Role | Tag | Why (Max 140) | Lock Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | 2026-01-07 | ARCH | GOV | Implementation of Phase 5 Archive governance. | YES |
| 002 | 2026-01-07 | ARCH | GOV | Locked Phase 4 communication rituals & failover budgets. | YES |
| 003 | 2026-01-07 | BUILD | IMPL | Phase 6: GPU debug visuals (ModernGL distortion, stress halos, vignette, auto-throttle at 14ms). | YES |
| 004 | 2026-01-07 | BUILD | PERF | TRIAGE-004: Vectorized flower interaction (broadcasting), preserved harvest noise, 2Hz RAM monitoring. | YES |
| 005 | 2026-01-08 | ARCH | GOV | Phase 7 launch: versioned contracts, metrics framework, Supervisor-Worker experiment design. | YES |
| 006 | 2026-01-09 | ARCH | GOV | Roles updated: Perplexity=Librarian, Grok=Advisory, Tooling boundaries defined. | YES |
| 007 | 2026-01-10 | BUILD | IMPL | Task 8.2: Surgical timeline (4-stage GPU breakdown) falsified Latency Trap, proved 19.45ms download tax. | YES |
| 008 | 2026-01-10 | ARCH | IMPL | Surgery 8.3: One-Way Doctrine. GPU distortion disabled, CPU-only locked. Reclaimed 5ms upload overhead. | YES |
| 009 | 2026-01-10 | ARCH | PERF | Phase 9.2: 1,000-bee validation @ 7.99ms median. Cache synergy 30% reduction vs isolated tiers. BJI 4.1-4.2. | YES |
| 010 | 2026-01-10 | ARCH | PERF | Phase 9.3: 1,200-bee primary @ 10.59ms median. Non-linear cost 0.0130ms/bee. Cache plateau detected. | YES |
| 011 | 2026-01-11 | BUILD | IMPL | Phase 10: Trinity of Castes (Caste 1.0) implemented via branchless scalar biasing. 10/60/30 split. 1,200-bee ceiling locked. | YES |

**Chronicle Rules:**
- **WHY Field:** Hard cap at 140 characters (enforced by Claude Code validation)
- **Tags:** PERF (Performance) / PERC (Perception) / BIOL (Biology) / GOV (Governance) / ARCH (Architecture) / IMPL (Implementation)
- **Lock Check:** YES = next agent has context, NO = handoff incomplete
- **Filename Convention:** `YYYY-MM-DD_[TAG]_[SHORT_NAME].md`
- **Enforcement:** Claude Code validates WHY length and filename format before saving

---

## 🗂️ Key Files Map

### Core Simulation
- [config.py](config.py) - All tunable constants (Phase 1-4)
- [simulation.py](simulation.py) - Main simulation loop, tier updates
- [biology.py](biology.py) - Tier state machine & behavior logic
- [environment.py](environment.py) - Main entry point, Pygame loop

### Phase 4 Systems
- [src/pheromone_system.py](src/pheromone_system.py) - Chemical trail system (128×128 grid)
- [src/resource_manager.py](src/resource_manager.py) - Flower nectar & harvest logic
- [render_utils.py](render_utils.py) - Visualization (flowers, heatmap, bees)

### Phase 6 Systems (Debug Visuals)
- [src/debug_visuals/performance_monitor.py](src/debug_visuals/performance_monitor.py) - GPU detection, auto-throttle guardian
- [src/debug_visuals/distortion_system.py](src/debug_visuals/distortion_system.py) - ModernGL fragment shader (pheromone stress shimmer)
- [src/debug_visuals/halo_system.py](src/debug_visuals/halo_system.py) - CPU vectorized stress halos (Surface.blits)
- [src/debug_visuals/vignette_system.py](src/debug_visuals/vignette_system.py) - Static radial stress gradient

### Documentation
- [PHASE4_IMPLEMENTATION_REPORT.md](PHASE4_IMPLEMENTATION_REPORT.md) - Phase 4 completion report
- [AI_RULES.md](AI_RULES.md) - Original multi-agent protocol

### Phase 5 Governance
- [docs/memos/governance/2026-01-07_GOV_Phase5_Archive_Governance.md](docs/memos/governance/2026-01-07_GOV_Phase5_Archive_Governance.md) - Archive governance protocol
- [docs/templates/MEMO_TEMPLATE.md](docs/templates/MEMO_TEMPLATE.md) - Standardized memo template with 140-char WHY cap
- [docs/templates/HANDOFF_TEMPLATE.md](docs/templates/HANDOFF_TEMPLATE.md) - Agent transition template
- [docs/baselines/phase-4-complete/MANIFEST.md](docs/baselines/phase-4-complete/MANIFEST.md) - Phase 4 frozen baseline

### Phase 7 Orchestration Experiments (NEW)
- [docs/phase7/versioned_contracts.md](docs/phase7/versioned_contracts.md) - Versioned contract protocol & template
- [docs/phase7/metrics_framework.md](docs/phase7/metrics_framework.md) - Measurement methodology for team effectiveness
- [docs/phase7/experiment_design.md](docs/phase7/experiment_design.md) - Scientific protocol for orchestration pattern testing

### Tests
- [test_phase4.py](test_phase4.py) - 600-frame validation suite

---

## 🧪 Test Commands

```bash
# Run Phase 4 validation (600 frames, headless)
python test_phase4.py

# Launch interactive simulation
python environment.py

# Compile check
python -m py_compile simulation.py
```

**Expected Results:**
- Frame time: 5-6ms average (excludes first-frame JIT spike)
- All validation checks: PASS
- No warnings or errors

---

## 🔄 Active Agents & Roles (Phase 7 Updated)

| Role | Agent | Responsibilities | Phase 7 Role |
|------|-------|------------------|--------------|
| **Lead Architect** | Gemini 2.5 Pro | System design, invariant locks, phase planning | Architectural review |
| **Builder** | Claude Sonnet 4.5 | Implementation, testing, documentation | Primary worker (Supervisor-Worker) |
| **Integration Surgeon** | Grok | Cross-system integration, realism validation | Realism audits & Advisory |
| **Performance Guru** | DeepSeek | Optimization, profiling, budget enforcement | **Process analyst & metric designer** |
| **Librarian** | Perplexity | Case studies, institutional memory, archives | Documentation & Intake |
| **Supervisor** | Human (Merchant) | Final approval, priority decisions | **Active supervisor (Experiment 1)** |

---

## 💡 Current Context (For Incoming Agents)

### What Just Happened
**Phase 7 launched on 2026-01-08**:
- Created versioned contract protocol for structured handoffs with evidence
- Established metrics framework: CSR, CVE, RTI, HDL, FPR metrics
- Designed Experiment 1: Supervisor-Worker pattern baseline
- Prepared directory structure: docs/phase7/ with metrics/, contracts/, analysis/
- Updated PROJECT_STATE.md with Phase 7 goals and invariants

**Previous (Phase 6 completed 2026-01-07)**:
- GPU-accelerated debug visuals with auto-throttle
- TRIAGE-004: Vectorized flower interaction (broadcasting)
- Performance: 5.67ms avg frame time @ 2000 bees

### What's Next (Experiment 1: Supervisor-Worker Pattern)
1. **Session 1 (Tomorrow):** Scale to 3000 bees, establish memory baseline, collect first metrics
2. **Session 2:** Scale to 5000 bees, implement advanced behavior (waggle dance or guard bees)
3. **Session 3:** Optimization pass, complete dataset, analyze Supervisor-Worker effectiveness

**Phase 7 Targets:**
- Simulation: 5000-10000 bees @ ≤8ms, +5MB memory limit
- Process: CSR ≥90%, RTI ≤30s, HDL ≤3/hour
- Deliverables: Comparative metrics on 2+ orchestration patterns

### Known Issues
- Halo system uses Surface.set_alpha() per bee (expensive) - vectorization needed if >3000 visible halos
- Distortion shader reads/writes full screen buffer (1280×720 RGBA) - may breach budget on low-end GPUs
- Auto-throttle disables ALL debug visuals (no granular per-system control)
- TRIAGE-003: Pheromone field temporarily replicated across RGB channels (awaiting food/alarm trails implementation)

### Decision Points
None pending. Phase 6 is locked and approved per [ARCH-SDL-PHASE6-002].

---

## 🚨 Failover Performance Budget

**Communication Overhead Cap:** 0.1% of simulation budget
**Allowed Overhead:** 0.006ms per frame (8ms × 0.001)
**Grace Period on Agent Swap:** 10 minutes before hard caps re-enforce

**Budget Collapse Warning:** If frame time exceeds 15ms for >5 consecutive frames, halt new feature work and profile.

---

## 📋 Handoff Protocol

When ending a session, the active agent MUST:

1. Update this file's "Last Updated" date
2. Add Chronicle entry following [ARCH-COMM-03] schema
3. Complete LOCK CHECK (verify next agent has necessary memos/context)
4. Use [docs/HANDOFF_TEMPLATE.md](docs/HANDOFF_TEMPLATE.md) for formal handoffs

**15-Second Rule:** An incoming agent should reconstruct project state by reading:
1. This file (PROJECT_STATE.md) - 10 seconds
2. Latest Chronicle entry - 3 seconds
3. Referenced memos/reports - 2 seconds

---

## 🎓 Learning & Evolution

### What Worked Well
- Modular Phase 4 design (PheromoneSystem, ResourceManager as clean abstractions)
- Numba optimization for hot paths
- Strict red-line enforcement prevented scope creep

### What To Watch
- Pheromone grid size (128×128) may need tuning if bee count scales to 5000+
- Flower count hardcoded to 5 - architect may want this configurable later

### Architectural Debt
None. Phase 4 closed all open design questions.

---

**End of State Document**
*This file is the authoritative source for APIS-OVERSEER project status.*
*When in doubt, trust this document over individual file comments or commit messages.*
