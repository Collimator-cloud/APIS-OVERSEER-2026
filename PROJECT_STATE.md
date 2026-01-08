> **WAKE-UP:** PHASE_6_DEBUG_VISUALS | 2026-01-07 | 2026-01-07-Phase6-GPU | RECONSTRUCTION: <15s

# 🧠 APIS-OVERSEER PROJECT STATE

**Last Updated:** 2026-01-07
**Current Phase:** Phase 6 - Debug Visuals & GPU Integration
**Status:** GPU-accelerated stress visualization system COMPLETE
**Performance Budget:** ≤1.0ms debug overhead / 14ms auto-throttle breach
**ARCHIVE_PULSE:** 🟢 | Last Checked: 2026-01-07 | Next Due: 2026-01-14

---

## 🎯 Quick-Scan Stats

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Avg Frame Time** | 5.67ms | ≤8ms | ✅ PASS |
| **Simulation Time** | ~2.5ms | ≤4ms | ✅ PASS |
| **FPS** | ~176 FPS | ≥120 FPS | ✅ PASS |
| **Bee Count** | 2000 | 2000 | ✅ |
| **Performance Headroom** | 2.33ms | - | ✅ Healthy |

**Critical Systems:**
- ✅ Pheromone System (128×128 grid, Numba-optimized)
- ✅ Resource Manager (5 flowers, dynamic nectar)
- ✅ LOD System (3-tier hysteresis)
- ✅ Density Field (spatial awareness)
- ✅ Debug Visuals (GPU distortion, stress halos, vignette) **← PHASE 6**

---

## 📐 Current Architecture

### Phase Progression
1. ✅ **Phase 1:** Foundation (Pygame, basic rendering)
2. ✅ **Phase 2:** The Swarm (density field, LOD system)
3. ✅ **Phase 3:** Agent intelligence (tier behaviors)
4. ✅ **Phase 4:** The Garden (pheromones, resources)
5. ✅ **Phase 5:** Archive Governance (documentation, handoff protocol)
6. ✅ **Phase 6:** Debug Visuals & GPU Integration **← YOU ARE HERE**

### Active Invariants
- **[ARCH-COMM-01]** Status Page Invariant: This file is the single source of truth
- **[ARCH-COMM-02]** 15s Reconstruction Goal: Any agent must reconstruct context in <15s
- **[ARCH-COMM-03]** Chronicle Schema: 140-char max entries with LOCK CHECK
- **[ARCH-COMM-04]** Failover Budget: Communication overhead ≤0.1% of simulation budget

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

### Phase 5 Governance (NEW)
- [docs/memos/governance/2026-01-07_GOV_Phase5_Archive_Governance.md](docs/memos/governance/2026-01-07_GOV_Phase5_Archive_Governance.md) - Archive governance protocol
- [docs/templates/MEMO_TEMPLATE.md](docs/templates/MEMO_TEMPLATE.md) - Standardized memo template with 140-char WHY cap
- [docs/templates/HANDOFF_TEMPLATE.md](docs/templates/HANDOFF_TEMPLATE.md) - Agent transition template
- [docs/baselines/phase-4-complete/MANIFEST.md](docs/baselines/phase-4-complete/MANIFEST.md) - Phase 4 frozen baseline

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

## 🔄 Active Agents & Roles

| Role | Agent | Responsibilities |
|------|-------|------------------|
| **Lead Architect** | Gemini 2.5 Pro | System design, invariant locks, phase planning |
| **Builder** | Claude Sonnet 4.5 | Implementation, testing, documentation |
| **Biologist** | Grok | Behavioral realism, ethological validation |
| **Performance** | DeepSeek | Optimization, profiling, budget enforcement |
| **Librarian** | The Brain | UX design, information architecture |
| **Coordinator** | Human (Merchant) | Final approval, priority decisions |

---

## 💡 Current Context (For Incoming Agents)

### What Just Happened
**Phase 6 + TRIAGE-004 completed on 2026-01-07**:
- GPU-accelerated debug visuals (ModernGL distortion, stress halos, vignette) with auto-throttle
- Vectorized flower interaction using (N×M) broadcasting (eliminated nested Python loops)
- Preserved biological harvest noise (±15% variation with nectar attenuation)
- Performance halt condition: Vanguard update >2.0ms triggers illusion risk warnings
- RAM monitoring at 2Hz via psutil

### What's Next
1. **Performance Validation:** Run test_phase4.py to verify ≤1.0ms debug overhead target
2. **GPU Fallback Testing:** Verify silent CPU fallback on systems without OpenGL 3.3+
3. **Awaiting Phase 7 Spec:** Lead Architect will define next evolution

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
