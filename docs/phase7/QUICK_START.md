# PHASE 7 QUICK START GUIDE

**For Incoming Agents: Read This First**

---

## 🎯 What Is Phase 7?

Phase 7 is a **dual-purpose phase**:
1. **Primary:** Experiment with AI team orchestration patterns to develop validated measurement frameworks
2. **Secondary:** Continue advancing the bee simulation (target: 5000-10000 bees, advanced behaviors)

**Key Insight:** The bees are our canary. If collaboration fails, simulation progress stalls. If collaboration succeeds, bees thrive.

---

## ⚡ 30-Second Context Reconstruction

1. **Current State:** Phase 6 complete (2000 bees @ 5.67ms, GPU debug visuals working)
2. **Current Experiment:** Supervisor-Worker pattern (Experiment 1 of 3)
3. **Your Role:** Check [PROJECT_STATE.md](../../PROJECT_STATE.md) Active Agents table
4. **Next Task:** Read latest versioned contract in [docs/phase7/contracts/](contracts/)

---

## 📋 Session Workflow (Supervisor-Worker Pattern)

### Before Starting Work
1. Read latest versioned contract (file: `YYYY-MM-DD_sessionN_vX.Y.md`)
2. **Measure reconstruction time** (timestamp: start → "ready to work")
3. **Verify constraints** against current codebase (report violations if found)
4. Note context completeness (1-5 scale, report in your contract)

### During Work
5. Track token usage (for Code Velocity Efficiency metric)
6. Count AskUserQuestion calls (for Human Decision Load metric)
7. Note architectural/design decisions (for Decision Throughput metric)
8. Record functional LOC changes (use `git diff --stat` at end)

### After Completing Work
9. Create new versioned contract using template
10. Calculate and report all applicable metrics
11. Update metrics CSV files in [docs/phase7/metrics/](metrics/)
12. Commit contract to [docs/phase7/contracts/](contracts/)

---

## 📊 Required Metrics (Quick Reference)

| Metric | What to Track | Target |
|--------|---------------|--------|
| **CSR** | Constraints intact vs. total | ≥90% |
| **CVE** | Functional LOC / tokens × 1000 | TBD |
| **RTI** | Time to "ready to work" (seconds) | ≤30s |
| **HDL** | AskUserQuestion calls / hour | ≤3/hour |
| **FPR** | Features completed / session | ≥0.5 |
| **PDI** | Frame time increase per 1000 bees | ≤1.0ms |

See [docs/phase7/metrics_framework.md](metrics_framework.md) for full definitions.

---

## 🔬 Experiment 1: Supervisor-Worker Pattern

**Structure:**
- Human (Merchant) = Supervisor (high-level goals, constraint enforcement)
- AI agents = Specialized workers (implementation, testing, optimization)
- Synchronous handoffs via versioned contracts

**Current Progress:**
- Session 0: Preparation complete ✅
- Session 1: Scale to 3000 bees, establish memory baseline
- Session 2: Scale to 5000 bees, implement advanced behavior
- Session 3: Optimization pass, complete dataset

**Success Criteria:**
- CSR ≥90% across all sessions
- RTI ≤30s average
- HDL ≤3/hour average
- Simulation: 5000 bees @ ≤8ms frame time

---

## 🚨 Red Lines (Never Violate)

1. **Velocity Magnitude Lock** — simulation.py:437-440
2. **Frame Time ≤8ms Baseline** — PROJECT_STATE.md:58
3. **Debug Budget ≤1.0ms** — PROJECT_STATE.md:62
4. **Pheromone Grid 128×128** — config.py:85
5. **LOD Hysteresis 0.5s/2.0s** — PROJECT_STATE.md:57
6. **Simulation/Render Separation** — PROJECT_STATE.md:58
7. **Gradient Clamp ≤5.0** — PROJECT_STATE.md:60

**If you discover a constraint violation, halt work and report immediately.**

---

## 📖 Essential Reading (Priority Order)

**Must Read (5 min):**
1. Latest versioned contract — [docs/phase7/contracts/](contracts/)
2. [PROJECT_STATE.md](../../PROJECT_STATE.md) — Phase 7 section

**Should Read (10 min):**
3. [versioned_contracts.md](versioned_contracts.md) — Protocol & template
4. [experiment_design.md](experiment_design.md) — Experiment 1 details

**Reference (as needed):**
5. [metrics_framework.md](metrics_framework.md) — Full metric definitions
6. Phase 4-6 reports — Context on current systems

---

## ⚙️ Key Files for Scaling Work

**Configuration:**
- [config.py](../../config.py) — NUM_BEES_VANGUARD, NUM_BEES_LEGION

**Simulation Core:**
- [simulation.py](../../simulation.py) — LOD system, tier updates

**Performance:**
- [src/debug_visuals/performance_monitor.py](../../src/debug_visuals/performance_monitor.py) — RAM monitoring

**Testing:**
- [test_phase4.py](../../test_phase4.py) — Update expected bee counts if hardcoded

---

## 🎪 Common Questions

**Q: What if I can't meet the <30s reconstruction target?**
A: Report actual time in your contract. If consistently >60s, we may need to simplify contract format.

**Q: What if metric collection takes >10% of my session?**
A: Note this in RISKS section. If >25% for 3 sessions, we abort and revise framework.

**Q: What if I discover a constraint violation from previous session?**
A: Document in your contract's CSR metric (reduce intact count). Investigate cause, fix if possible, notify supervisor.

**Q: What if the simulation targets conflict with time budget?**
A: Simulation progress is secondary to process experimentation. Slow bee progress is acceptable if metrics are valid.

**Q: What if I need to make an architectural decision?**
A: In Supervisor-Worker pattern, escalate to human supervisor (Merchant) for approval. Document decision in contract.

---

## 🔄 Pattern-Specific Notes

**Supervisor-Worker (Current):**
- Wait for supervisor approval on architectural decisions
- Focus on assigned task (don't scope creep to other areas)
- Report blockers early (don't spin on unclear requirements)

**Swarm (Future):**
- Self-assign tasks from backlog
- Coordinate via PROJECT_STATE.md updates
- Use arbitration memos for conflicts

**Sequential Relay (Future):**
- Validate previous agent's work before proceeding
- Deep understanding expected (full system context)
- Longer sessions (60-90 min) typical

---

## 📞 Emergency Contacts

**Metric Questions:** See [metrics_framework.md](metrics_framework.md)
**Protocol Questions:** See [versioned_contracts.md](versioned_contracts.md)
**Experiment Design:** See [experiment_design.md](experiment_design.md)
**General Context:** See [PROJECT_STATE.md](../../PROJECT_STATE.md)

**Process Lead:** DeepSeek (Performance Guru & Process Analyst)
**Supervisor (Exp 1):** Human (Merchant)

---

**END OF QUICK START**

*Get context in <5 minutes. Start working in <30 seconds after reading contract.*
