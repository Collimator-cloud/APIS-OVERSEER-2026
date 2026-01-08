# DUAL-TRACK TIME TRACKING METHODOLOGY

**Purpose:** Measure time allocation across Bee Track, Orchestration Track, and Overhead to enforce 70/20/10 balance

---

## TARGET ALLOCATION (Phase 7 Standard)

| Track | Target % | Typical Activities |
|-------|----------|-------------------|
| **Bee Track** | 70% | Scaling, optimization, behavior implementation, performance tuning, visual polish |
| **Orchestration** | 20% | Metrics collection, contract creation, documentation, pattern analysis |
| **Overhead** | 10% | Setup, debugging tools, communication, git operations, environment issues |

**Note:** Targets are guidelines, not hard limits. Variance of ±10% acceptable per session.

---

## TRACKING METHOD

### Simple Timestamped Log

Create a session log (plain text or markdown) with start/end timestamps for each activity:

```markdown
## SESSION 1 TIME LOG - 2026-01-09

### BEE TRACK
- 14:00-14:15 (15min) - Baseline memory measurement @ 2000 bees
- 14:15-14:30 (15min) - Scale to 3000 bees (config.py, simulation.py)
- 14:30-14:45 (15min) - Performance validation (frame time, visual check)
SUBTOTAL: 45 minutes

### ORCHESTRATION TRACK
- 14:45-14:55 (10min) - Collect CSR, HDL, RTI metrics
- 14:55-15:05 (10min) - Create contract v1.2
SUBTOTAL: 20 minutes

### OVERHEAD
- 13:55-14:00 (5min) - Session setup (read contract v1.0, verify constraints)
- 15:05-15:10 (5min) - Git commit, push
SUBTOTAL: 10 minutes

### TOTALS
- Bee Track: 45min (60%)
- Orchestration: 20min (26.7%)
- Overhead: 10min (13.3%)
- **TOTAL SESSION:** 75 minutes
```

### Categorization Rules

**BEE TRACK counts as Bee Track:**
- Writing code in simulation.py, biology.py, config.py for bee behaviors
- Performance profiling/optimization (frame time, memory)
- Visual improvements (render_utils.py, debug visuals)
- Testing bee behaviors (manual or automated)
- Feature implementation (waggle dance, guards, etc.)

**ORCHESTRATION TRACK counts as Orchestration:**
- Calculating metrics (CSR, CVE, RTI, HDL)
- Writing versioned contracts
- Updating metrics CSV files
- Analyzing orchestration patterns
- Process documentation (memos, reports)

**OVERHEAD counts as Overhead:**
- Reading contracts/memos to reconstruct context
- Git operations (add, commit, push, branch management)
- Environment debugging (imports, dependencies)
- Tool setup (profilers, debuggers)
- Communication clarifications with supervisor

**AMBIGUOUS CASES:**
- **BJI assessment:** Bee Track (it measures bee quality)
- **Memory baseline measurement:** Bee Track (performance optimization)
- **Updating PROJECT_STATE.md:** Orchestration Track (process documentation)
- **Debugging constraint violations:** Overhead (process compliance)

---

## CALCULATION

At session end:

1. **Sum time per track** from timestamped log
2. **Calculate percentages:**
   - Bee % = (Bee minutes / Total minutes) × 100
   - Orchestration % = (Orchestration minutes / Total minutes) × 100
   - Overhead % = (Overhead minutes / Total minutes) × 100
3. **Compare to 70/20/10 target**
4. **Record in contract v1.X** under METRICS section:
   ```markdown
   - Time Allocation Balance: Bee 60% / Orchestration 27% / Overhead 13%
   ```

---

## THRESHOLDS & ACTIONS

| Allocation | Status | Action |
|------------|--------|--------|
| **Bee ≥60%** | Healthy | Continue current approach |
| **Bee 50-59%** | Borderline | Review next session's priorities |
| **Bee <50%** | Imbalanced | Reprioritize Bee Track next session |
| **Orchestration >40%** | Red Flag | Metrics overhead too high, simplify |
| **Overhead >20%** | Process Issue | Investigate friction points, streamline |

### Abort Condition (from DeepSeek memo)
- **Time Imbalance:** >80% Orchestration for **2 consecutive sessions** → Abort pattern, refocus on bees

---

## EXAMPLE SESSION ANALYSIS

### Session 1 (Well-Balanced)
```
Bee: 45min (60%) ✅ HEALTHY
Orchestration: 20min (26.7%) ✅ ACCEPTABLE
Overhead: 10min (13.3%) ✅ ACCEPTABLE
Total: 75min
```
**Assessment:** Excellent balance. Bee progress prioritized, metrics collected efficiently.

---

### Session 2 (Orchestration-Heavy)
```
Bee: 30min (40%) ⚠️ BORDERLINE
Orchestration: 35min (46.7%) ⚠️ HIGH
Overhead: 10min (13.3%) ✅ ACCEPTABLE
Total: 75min
```
**Assessment:** Too much time on metrics/documentation. Simplify metrics collection next session.

---

### Session 3 (Overhead-Heavy)
```
Bee: 40min (53.3%) ✅ ACCEPTABLE
Orchestration: 15min (20%) ✅ HEALTHY
Overhead: 20min (26.7%) 🔴 HIGH
Total: 75min
```
**Assessment:** Overhead excessive. Likely due to git conflicts, environment issues, or context reconstruction problems. Investigate and streamline.

---

## INTEGRATION WITH CONTRACTS

Every versioned contract MUST include time allocation in two places:

### 1. Metadata (Top)
```markdown
**Track:** Both + Time Allocation: Bee 60% / Orchestration 27% / Overhead 13%
```

### 2. Metrics Section
```markdown
#### Orchestration Track Metrics:
- Time Allocation Balance: Bee 60% / Orchestration 27% / Overhead 13%
```

---

## TIPS FOR EFFICIENT TRACKING

### During Session
- **Keep log open** in a text editor alongside IDE
- **Timestamp as you switch tasks** (don't reconstruct from memory)
- **Round to nearest 5 minutes** (precision not critical, trends matter)
- **Don't overthink categorization** (when in doubt, pick closest match)

### Common Patterns
- **First 5-10 minutes:** Always Overhead (context reconstruction, setup)
- **Last 5-10 minutes:** Usually Orchestration (contract creation) + Overhead (git commit)
- **Middle bulk:** Should be dominated by Bee Track (70% target)

### Red Flags to Watch
- **Spending >10 minutes reading previous contract:** Contract too verbose, simplify
- **Spending >15 minutes on metrics:** Measurement overhead too high, automate or cut
- **Spending >15 minutes on git operations:** Process friction, investigate
- **Spending <30 minutes on Bee Track:** Session imbalanced, reprioritize

---

## AUTOMATION (Future Enhancement)

**Manual tracking is sufficient for Phase 7 Experiment 1.**

Future enhancements could include:
- Simple Python script to parse log and calculate percentages
- Integration with IDE time tracking plugins
- Automated git commit message parsing for categorization

**For now:** Keep it simple. Timestamped text log + manual calculation.

---

## PHILOSOPHY

Time tracking serves **insight, not control.**

We track to answer:
- "Are we actually prioritizing bees, or just talking about it?"
- "Is metrics collection becoming a burden?"
- "Where is the friction in our process?"

If time tracking itself becomes >5% of session time, we're doing it wrong.

**Keep it lightweight. Make it useful. Don't let measurement become the work.**

---

**END OF TIME TRACKING METHODOLOGY**

*Track to learn. Learn to improve. Improve to thrive.*
