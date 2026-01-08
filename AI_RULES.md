# APIS-OVERSEER: Project Governance & Rules

## 🏛️ CORE ARCHITECTURE
- **Temporal Decoupling:** Simulation (Logic/Physics) runs at **30Hz**. Rendering and LOD Hysteresis run at **60Hz**.
- **Data-Oriented Design:** NO individual "Bee" objects or classes. Use **NumPy Master State Matrices** (float32).
- **Three-Tier System:** 
  1. Vanguard (300 Detailed)
  2. Legion (2,000 Batched)
  3. Nebula (25k+ Statistical/Particles)

## ⚡ PERFORMANCE CONSTITUTION (DeepSeek Invariants)
- **Frame Budget:** 16.6ms (Total). Simulation must stay under **8ms**.
- **Vectorization:** Zero Python loops in hot paths. Use NumPy broadcasting or Numba `@njit`.
- **Memory:** Use memory pooling. No array allocations inside the main loop.
- **Rendering:** Use `pygame.Surface.blits()` with a texture atlas.

## 🧬 BIOLOGICAL REALISM (Grok Invariants)
- **Consensual Flow:** Bees use "Invisible Causes" (Pheromones/Fields). No "hard-snapping" to paths.
- **LOD Hysteresis:** 0.5s for promotion (Near), 2.0s for demotion (Far).
- **Biological Noise:** Seeded per-bee randomness to ensure organic movement.

## 🛠️ TOOLING
- **Runtime:** Python 3.12 (Pinned).
- **Engine:** `pygame-ce` (Community Edition).
- **Auth:** `selectedAuthType: USE_GEMINI` (API Key via environment variable).

## 🤖 ROLE PROTOCOL
- **Lead Architect (Gemini 2.5 Pro):** Final authority on structure and data flow.
- **Performance Guru (DeepSeek):** Veto power over any inefficient code.
- **Surgeon (Grok):** Logic and biological validation.
- **Builder (Claude Code):** Surgical implementation. DO NOT suggest refactors unless they adhere to these rules.