# Development Loops (Authoritative)

> NOTE: This document supersedes all previous informal loop descriptions.
> Earlier loop references remain historically valid but are no longer normative.
> This file defines the **only approved development loops** and how to select them.

---

## 🎯 PURPOSE

APIS-OVERSEER operates under **explicit development loops** to prevent:
- Decision paralysis
- Loop sprawl
- Governance fatigue
- Infinite consensus cycles

Loops are **tools**, not rituals.  
They exist to move work forward safely, not to be followed dogmatically.

---

## 🧭 LOOP SELECTOR — DECISION TREE

Use this decision tree **before starting any work**.

### Step 1 — What is the size of the change?

| Question | Answer |
|--------|--------|
| Is this a small, local change? | → Go to Step 2 |
| Is this a new feature / system / rule? | → Use **FULL DEVELOPMENT LOOP (SDL)** |

---

### Step 2 — Does this change affect performance, architecture, or governance?

| Affects… | Loop |
|-------|------|
| Performance, memory, render time | **FAST PATCH LOOP (PML)** |
| Architecture, loops, governance | **FULL DEVELOPMENT LOOP (SDL)** |
| Pure idea exploration / UX feel | **EXPLORATORY LOOP (EL)** |

---

### Step 3 — Are you blocked or unsure?

| Situation | Action |
|--------|--------|
| You’re unsure which loop applies | Start **EXPLORATORY LOOP (EL)** |
| You discover higher risk mid-loop | Escalate to **SDL** |
| Work is spinning without convergence | Trigger **Converged Loop Termination** |

---

## 🔁 APPROVED LOOP TYPES

---

## 1️⃣ EXPLORATORY LOOP (EL)
**Purpose:** Sensemaking, brainstorming, research, idea shaping  
**Speed:** Fast  
**Docs:** None required  
**Exit:** Insight gained or discarded

**Typical Flow:**


Coordinator ↔ Any Agent(s)


**Rules:**
- No enforcement
- No consensus required
- May terminate at any time
- Output is *optional insight*, not commitments

**Escalation Trigger:**  
If an idea shows promise or risk → escalate to SDL or PML.

---

## 2️⃣ FAST PATCH LOOP (PML)
**Purpose:** Small, low-risk fixes or refinements  
**Speed:** Very fast  
**Docs:** Minimal (commit message or memo note)

**Canonical Order:**


ChatGPT → DeepSeek → Claude


**Characteristics:**
- Performance-safe by default
- No new systems, rules, or governance
- No architectural changes
- No new directories or tooling

**Hard Constraints:**
- Must not increase cognitive load
- Must not require new documentation
- Must remain reversible

**Escalation Trigger:**  
If scope expands → escalate immediately to SDL.

---

## 3️⃣ FULL DEVELOPMENT LOOP (SDL)
**Purpose:** Features, systems, governance, architecture  
**Speed:** Deliberate  
**Docs:** Required  
**This is the default loop for real work**

**Canonical Order:**


Perplexity → Gemini → ChatGPT → Grok → DeepSeek → Gemini → Claude


**Roles by Stage:**
- **Perplexity (Librarian):** Precedents, risks, omissions
- **Gemini (Architect):** Structure, constraints, invariants
- **ChatGPT (Conceptual Director):** UX, perceptual intent, clarity
- **Grok (Realism Validator):** Biological / behavioral sanity
- **DeepSeek (Performance Guru):** Cost, guardrails, red lines
- **Gemini (Architect):** Final synthesis → God Prompt
- **Claude (Builder):** Implementation

**Exit Condition:**  
Claude implementation + lock check = ✅

---

## 🛑 CONVERGED LOOP TERMINATION PATTERN

A loop **must terminate** when **any** of the following are true:

### Automatic Termination
- All required reviewers approve
- No red lines remain
- Lock Check = YES

### Forced Termination
- Loop exceeds its scope
- Same feedback repeats twice
- Coordinator invokes override

### Termination Rules
- Termination is **success**, not failure
- Unresolved ideas may be logged and deferred
- No loop may continue “just in case”

---

## 🔄 BACKTRACKING & ESCALATION

Loops are **not linear**. Backtracking is expected.

### Allowed Transitions
| From | To | When |
|----|----|----|
| EL | PML | Small actionable fix |
| EL | SDL | Idea proves important |
| PML | SDL | Scope expands |
| SDL | EL | Stuck or unclear |

**Rule:**  
Backtracking must be explicit and intentional, not accidental.

---

## 🧯 ESCAPE HATCH — COORDINATOR OVERRIDE

At any point, the Coordinator may:
- Abort a loop
- Change loop type
- Skip stages
- Force termination

This exists to prevent:
- Fatigue
- Over-governance
- Lost momentum

---

## 📊 LOOP BUDGETS (HARD CAPS)

| Loop | Max Iterations |
|----|----|
| Exploratory | Unlimited (but disposable) |
| Fast Patch | 1 pass |
| Full Dev | 1 full circuit |

Exceeding a budget requires explicit Coordinator approval.

---

## 🧠 DESIGN PRINCIPLES

- **Clarity beats completeness**
- **Termination is a feature**
- **Loops serve work, not identity**
- **If it feels heavy, it’s wrong**

---

## 🔗 REFERENCES

- Visual Map: `/docs/governance/visuals/DEV_LOOP_MAP_V1.png`
- Governance Quick Ref: `/docs/templates/GOVERNANCE_QUICK_REFERENCE.md`

---

**Status:** ACTIVE  
**Last Updated:** 2026-01-07  
**Lock Check:** YES