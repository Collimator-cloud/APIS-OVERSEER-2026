# PHASE 7 METRICS FRAMEWORK

**Date:** 2026-01-08
**Status:** ACTIVE
**Purpose:** Systematic measurement of AI team orchestration effectiveness

---

## OVERVIEW

Phase 7 introduces novel metrics to measure AI team collaboration quality. We collect quantitative data across multiple orchestration patterns (Supervisor-Worker, Swarm, Sequential) to identify effectiveness factors.

**Key Principle:** Metrics serve insight, not control. We measure to learn, not to game.

---

## METRIC CATEGORIES

### 1. CONSTRAINT PRESERVATION METRICS

#### Constraint Survival Rate
**Definition:** Percentage of constraints that remain intact across N handoffs

**Formula:**
```
CSR(N) = (Constraints verified intact after N handoffs) / (Total constraints at session start) × 100
```

**Collection Method:**
1. Hash CONSTRAINTS section of versioned contract at creation
2. Next agent verifies each constraint against current codebase
3. Count violations (constraint no longer enforced in code)
4. Report in next contract's METRICS section

**Thresholds:**
- 🟢 ≥95% — Excellent preservation
- 🟡 80-94% — Acceptable drift, investigate
- 🔴 <80% — Critical drift, halt and rebuild context

**Storage:** `docs/phase7/metrics/constraint_survival.csv`

**Example:**
```csv
Date,Session,Pattern,Constraints_Start,Constraints_Intact,CSR,Notes
2026-01-09,1,Supervisor-Worker,7,7,100%,Baseline session
2026-01-09,2,Supervisor-Worker,7,6,85.7%,Velocity lock relaxed in biology.py:440
```

---

#### Constraint Drift Velocity
**Definition:** Rate of constraint violation per session

**Formula:**
```
CDV = (Constraints violated in session) / (Session duration in hours)
```

**Collection Method:**
1. Count constraint violations during session (caught by tests, reviews, or agent self-report)
2. Divide by session duration
3. Track trend over time

**Thresholds:**
- 🟢 0 violations/hour — Perfect adherence
- 🟡 0.1-0.5 violations/hour — Acceptable, may indicate ambiguity
- 🔴 >0.5 violations/hour — Process failure, constraints unclear

**Storage:** `docs/phase7/metrics/constraint_drift.csv`

---

### 2. VELOCITY METRICS

#### Code Velocity Efficiency
**Definition:** Functional lines of code per 1000 tokens consumed

**Formula:**
```
CVE = (Functional LOC added or modified) / (Total tokens in session) × 1000
```

**Collection Method:**
1. Use `git diff --stat` to count LOC changes
2. Filter for functional code only:
   - INCLUDE: Logic, algorithms, data structures
   - EXCLUDE: Comments, docstrings, whitespace, imports
3. Divide by session token count (from API/SDK metrics)
4. Multiply by 1000 for readability

**Thresholds:**
- 🟢 ≥2.0 — High efficiency (typical for focused implementation)
- 🟡 1.0-2.0 — Moderate efficiency (typical for complex refactoring)
- 🔴 <1.0 — Low efficiency (investigate if multi-session trend)

**Storage:** `docs/phase7/metrics/code_velocity.csv`

**Example:**
```csv
Date,Session,Pattern,Functional_LOC,Tokens,CVE,Task_Type
2026-01-09,1,Supervisor-Worker,120,50000,2.4,Feature implementation
2026-01-09,2,Supervisor-Worker,45,60000,0.75,Debugging/optimization
```

---

#### Decision Throughput
**Definition:** Architectural or design decisions made per hour

**Formula:**
```
DT = (Decisions documented in DECISIONS section) / (Session duration in hours)
```

**Collection Method:**
1. Count entries in versioned contract DECISIONS section
2. Exclude trivial decisions (e.g., variable naming)
3. Include only architectural/design/constraint decisions
4. Normalize to per-hour rate

**Thresholds:**
- 🟢 2-4 decisions/hour — Healthy pace (not rushed, not stalled)
- 🟡 1-2 or 5-6 decisions/hour — Acceptable variation
- 🔴 <1 or >6 decisions/hour — Investigate (stall or thrashing)

**Storage:** `docs/phase7/metrics/decision_throughput.csv`

---

### 3. CONTEXT RECONSTRUCTION METRICS

#### Reconstruction Time Index
**Definition:** Time for incoming agent to reach "ready to work" state

**Formula:**
```
RTI = Time from contract read start to "context complete" declaration (seconds)
```

**Collection Method:**
1. Incoming agent timestamps when starting contract read
2. Agent reads versioned contract + referenced files/commits
3. Agent timestamps when ready to work (no more context needed)
4. Self-report in new session's first contract

**Thresholds:**
- 🟢 ≤30s — Excellent (Phase 7 target)
- 🟡 31-60s — Acceptable, check contract clarity
- 🔴 >60s — Contract failure, rebuild needed

**Storage:** `docs/phase7/metrics/reconstruction_time.csv`

**Example:**
```csv
Date,Session,Pattern,Agent,Contract_Version,RTI,Blockers
2026-01-09,2,Supervisor-Worker,Grok,v1.2,28s,None
2026-01-09,3,Supervisor-Worker,DeepSeek,v1.3,45s,Missing memory baseline reference
```

---

#### Context Completeness Score
**Definition:** Subjective agent assessment of context adequacy (1-5 scale)

**Collection Method:**
1. Incoming agent rates context completeness after reconstruction:
   - 5 = Perfect, no ambiguity, ready to execute
   - 4 = Minor gaps, easily inferred
   - 3 = Moderate gaps, needed clarification
   - 2 = Major gaps, required deep file reading
   - 1 = Context failure, could not proceed
2. Self-report in METRICS section
3. Include notes on specific gaps

**Thresholds:**
- 🟢 ≥4.0 average — Excellent handoffs
- 🟡 3.0-3.9 average — Acceptable, improve documentation
- 🔴 <3.0 average — Handoff protocol failing

**Storage:** `docs/phase7/metrics/context_completeness.csv`

---

### 4. HUMAN INTERACTION METRICS

#### Human Decision Load
**Definition:** Questions or decisions requiring human input per hour

**Formula:**
```
HDL = (AskUserQuestion calls + explicit decision requests) / (Session duration in hours)
```

**Collection Method:**
1. Count AskUserQuestion tool calls
2. Count explicit "awaiting human decision" states in contracts
3. Exclude clarifications on requirements (normal)
4. Include only decisions that agents should autonomously handle
5. Normalize to per-hour rate

**Thresholds:**
- 🟢 ≤3/hour — High autonomy (goal state)
- 🟡 4-6/hour — Moderate autonomy, check constraint clarity
- 🔴 >6/hour — Low autonomy, process failure

**Storage:** `docs/phase7/metrics/human_decision_load.csv`

**Note:** Low HDL is desirable (indicates agents work autonomously within constraints)

---

#### Approval Latency
**Definition:** Time from human decision request to approval received

**Formula:**
```
AL = Time from AskUserQuestion call to user response (minutes)
```

**Collection Method:**
1. Timestamp when AskUserQuestion is invoked
2. Timestamp when user response received
3. Calculate delta in minutes
4. Track distribution (median, P95)

**Thresholds:**
- 🟢 ≤5min median — Fast feedback loop
- 🟡 6-15min median — Acceptable for async work
- 🔴 >15min median — Blocking, reduce decision load

**Storage:** `docs/phase7/metrics/approval_latency.csv`

---

### 5. SIMULATION PROGRESS METRICS

#### Functional Progress Rate
**Definition:** Bee simulation features completed per session

**Collection Method:**
1. Define features in advance with measurable criteria (e.g., "waggle dance implemented with test")
2. Track completion in contracts
3. Count features completed per session
4. Normalize to features/hour if sessions vary in length

**Thresholds:**
- 🟢 ≥0.5 features/session — Strong progress
- 🟡 0.25-0.49 features/session — Steady progress
- 🔴 <0.25 features/session — Stalling (3+ session trend = abort)

**Storage:** `docs/phase7/metrics/functional_progress.csv`

**Example Features:**
- Scale to 3000 bees (≤8ms maintained)
- Scale to 5000 bees (≤8ms maintained)
- Implement waggle dance behavior
- Implement guard bee behavior
- Implement hive entry/exit logic
- Add multi-pheromone trails (food vs alarm)

---

#### Performance Degradation Index
**Definition:** Frame time increase per 1000 additional bees

**Formula:**
```
PDI = (Frame time at N bees - Frame time at baseline) / ((N - baseline) / 1000)
```

**Collection Method:**
1. Baseline: 2000 bees @ 5.67ms (Phase 6)
2. Measure frame time after scaling
3. Calculate ms increase per 1000 bees
4. Track trend to predict limits

**Thresholds:**
- 🟢 ≤1.0 ms/1000 bees — Excellent scaling
- 🟡 1.1-2.0 ms/1000 bees — Acceptable, monitor
- 🔴 >2.0 ms/1000 bees — Scaling failure, optimize before adding more

**Storage:** `docs/phase7/metrics/performance_scaling.csv`

**Example:**
```csv
Date,Bee_Count,Frame_Time_Avg,Frame_Time_P95,PDI,Notes
2026-01-08,2000,5.67ms,8.2ms,0.0,Baseline (Phase 6)
2026-01-09,3000,6.45ms,9.1ms,0.78,After LOD tuning
2026-01-09,5000,8.20ms,11.5ms,0.84,Within budget, slight degradation
```

---

## DATA COLLECTION WORKFLOW

### Session Start
1. Incoming agent reads previous versioned contract
2. Records reconstruction time (RTI)
3. Rates context completeness (CCS)
4. Notes any constraint violations discovered

### During Session
5. Track token usage (API/SDK provides)
6. Count AskUserQuestion calls (HDL metric)
7. Timestamp human decision requests (AL metric)
8. Note functional LOC changes (for CVE)

### Session End
9. Create new versioned contract
10. Document decisions made (for DT metric)
11. Verify constraints intact (for CSR metric)
12. Calculate and report all applicable metrics
13. Commit contract to `docs/phase7/contracts/`

### Weekly Review
14. Aggregate metrics to CSV files
15. Generate summary charts (optional)
16. Identify trends and anomalies
17. Adjust process if thresholds breached

---

## STORAGE STRUCTURE

```
docs/phase7/
├── metrics/
│   ├── constraint_survival.csv
│   ├── constraint_drift.csv
│   ├── code_velocity.csv
│   ├── decision_throughput.csv
│   ├── reconstruction_time.csv
│   ├── context_completeness.csv
│   ├── human_decision_load.csv
│   ├── approval_latency.csv
│   ├── functional_progress.csv
│   └── performance_scaling.csv
├── contracts/
│   ├── 2026-01-09_session1_v1.0.md
│   ├── 2026-01-09_session2_v1.1.md
│   └── ...
└── analysis/
    ├── weekly_summary_2026-01-08.md
    └── ...
```

---

## CROSS-PATTERN COMPARISON

After collecting 3+ sessions per pattern (Supervisor-Worker, Swarm, Sequential), compare:

| Metric | Supervisor-Worker | Swarm | Sequential | Winner |
|--------|-------------------|-------|------------|--------|
| CSR (avg) | TBD | TBD | TBD | TBD |
| CVE (avg) | TBD | TBD | TBD | TBD |
| RTI (median) | TBD | TBD | TBD | TBD |
| HDL (avg) | TBD | TBD | TBD | TBD |
| FPR (avg) | TBD | TBD | TBD | TBD |

**Goal:** Identify which pattern(s) optimize for:
- Autonomy (low HDL)
- Velocity (high CVE, high FPR)
- Coherence (high CSR)
- Efficiency (low RTI)

---

## ABORT CONDITIONS

If any of these persist for 3+ sessions:
- CSR drops below 80%
- FPR drops below 0.25 features/session
- HDL exceeds 6 decisions/hour
- Metric collection time exceeds 25% of session duration

**Action:** Document failure mode, reset to known-good pattern, iterate.

---

## VALIDATION

Metrics framework is valid if:
- ✅ Data is collectible without specialized tools
- ✅ Metrics are reproducible (same data → same score)
- ✅ Overhead is <10% of session time
- ✅ Insights emerge after 3 sessions (trends visible)

**Checkpoint:** After 3 sessions, assess if metrics provide actionable insights. If not, revise framework.

---

**END OF METRICS FRAMEWORK**

*This document defines how we measure AI team effectiveness in Phase 7.*
*Metrics are tools for learning, not targets to game.*
