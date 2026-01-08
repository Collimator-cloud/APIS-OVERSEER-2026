# BEE JOY INDEX (BJI) - ASSESSMENT GUIDELINES

**Purpose:** Measure whether bees "feel alive" and maintain project motivation per Dual-Track Constitution

---

## RATING SCALE (1-5)

### 5 - MESMERIZING
**Indicators:**
- Emergent behavior is captivating to watch
- Unpredictable but coherent patterns emerge
- Bees exhibit individual personality in movement
- Performance feels effortless (no visible lag/stutter)
- Visual aesthetic is polished and engaging
- You want to stop working and just watch the sim

**Examples:**
- Bees form natural foraging trails without being explicitly coded
- Guard bees patrol hive entrance with realistic vigilance
- Swarm exhibits coordinated "wave" motion during directional changes

---

### 4 - ENGAGING
**Indicators:**
- Clear emergent behavior visible
- System feels responsive and alive
- Minor visual issues don't detract from experience
- Performance is smooth (≤8ms, no perceptible lag)
- Occasional moments of surprise/delight

**Examples:**
- Pheromone trails create visible "highways" between hive and flowers
- Density field causes natural clustering/dispersal
- Individual bees occasionally do something unexpected but sensible

---

### 3 - FUNCTIONAL
**Indicators:**
- Bees move and behave correctly
- No obvious bugs or breakage
- Performance meets targets (≤8ms)
- System is "working" but not captivating
- You can watch for 30 seconds without boredom

**Examples:**
- Bees orbit flowers, harvest nectar, return to hive
- LOD system works but transitions are mechanical
- Pheromones exist but trails aren't compelling

---

### 2 - LIFELESS
**Indicators:**
- Technically functional but emotionally flat
- Bees feel like particles, not agents
- Movement is robotic or overly uniform
- Performance issues distract from behavior
- You feel no desire to watch for more than 10 seconds

**Examples:**
- All bees move in lockstep (no individual variation)
- Pheromone trails are invisible or nonsensical
- Performance stutters interrupt perception of life
- Bees clip through flowers or walls

---

### 1 - BROKEN
**Indicators:**
- Simulation crashes or freezes
- Major visual artifacts (missing bees, corruption)
- Performance collapse (>15ms, <30 FPS)
- Bees exhibit obviously wrong behavior (flying backward, teleporting)
- System is frustrating or unpleasant to watch

**Examples:**
- "Bullet bees" zip across screen at impossible speeds
- Pheromone grid causes visual glitches
- Bees pile up in corners and vibrate
- Simulation hangs or requires restart

---

## ASSESSMENT PROTOCOL

### When to Assess
- **End of every session** (both Coordinator and Active Agent)
- **Mid-session** if major behavior changes implemented
- **Ad-hoc** if something feels off or delightful

### Who Assesses
- **Coordinator (Primary):** Final BJI value, human aesthetic judgment
- **Active Agent (Secondary):** Technical assessment, self-report

### How to Assess
1. **Run simulation** for 60 seconds (full speed, no debug overlays)
2. **Observe without interference** (don't interact, just watch)
3. **Rate on 1-5 scale** using guidelines above
4. **Note specific observations** (e.g., "trails emerged at 0:35", "stutter at 3000 bees")

### Recording
- Update `docs/phase7/metrics/bji.csv` with both ratings
- Average: (Coordinator + Agent) / 2
- Include brief notes on what influenced rating

---

## THRESHOLDS & ACTIONS

| BJI | Status | Action |
|-----|--------|--------|
| **≥4.0** | Excellent | Continue current approach, celebrate wins |
| **3.0-3.9** | Acceptable | Monitor, consider bee-focused improvements |
| **2.0-2.9** | Concerning | Reprioritize Bee Track next session |
| **<2.0** | Critical | ABORT orchestration work, emergency Bee Track focus |

### Abort Condition (from DeepSeek memo)
- BJI <3 for **2 consecutive sessions** → Bee Track emergency priority
- BJI <2 for **2 consecutive sessions** → Halt all Orchestration work

---

## EXAMPLE ASSESSMENTS

### Session 1 Example (3000 bees, no new behaviors)
**Coordinator BJI:** 3
- "Bees are moving smoothly, trails visible, but nothing new or surprising. Feels like watching Phase 6 with more bees."

**Agent BJI:** 3
- "Performance solid (6.2ms avg), no bugs, but no emergent delight. Scaling worked technically but didn't add 'life'."

**Average:** 3.0 (FUNCTIONAL - acceptable for scaling session)

---

### Session 2 Example (waggle dance implemented)
**Coordinator BJI:** 5
- "WOW. Bees are dancing at hive entrance when returning from flowers. Didn't expect the circular pattern to emerge so naturally. Watched for 3 minutes."

**Agent BJI:** 4
- "Dance behavior implemented as planned, emergent spacing is beautiful. Minor clipping on overlapping dancers (fix next session)."

**Average:** 4.5 (MESMERIZING - huge bee progress)

---

### Session 3 Example (performance regression)
**Coordinator BJI:** 2
- "Stuttering at 5000 bees (12ms avg). Bees feel glitchy. Pheromone trails flickering. Not fun to watch."

**Agent BJI:** 2
- "Debug visuals breached budget, distortion shader causing artifacts. Frame time unacceptable. Need optimization."

**Average:** 2.0 (LIFELESS - trigger Bee Track reprioritization)

---

## INTEGRATION WITH CONTRACTS

Every versioned contract MUST include BJI in METRICS section:
```markdown
### METRICS (Phase 7)

#### Bee Track Metrics:
- Bee Joy Index (BJI): 3.5 (Coordinator: 3, Agent: 4)
```

If BJI <3, contract RISKS section must include mitigation plan.

---

## PHILOSOPHY

**BJI is not a technical metric.** It's a motivation safeguard.

The constitution states: *"If bees stop feeling alive, motivation dies."*

BJI operationalizes this truth. It forces us to ask every session:

**"Would I want to show this to someone and watch their face light up?"**

If the answer is no, we're losing track of why we built this.

---

**END OF BJI GUIDELINES**

*Bees are half the purpose. BJI measures whether that half is thriving.*
