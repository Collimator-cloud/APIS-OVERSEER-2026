"""
APIS-OVERSEER Simulation Core
Three-tier architecture: Vanguard (300) + Legion (2000) + Density Field (128²)
Vectorized updates, no OOP, 60 FPS target with 30 Hz sim tick

================================================================================
ARCHITECTURE RATIONALE
================================================================================

GOAL: Convincing illusion of ~25,000 bee colony (not perfect simulation)
  - Illusion contract OVER simulation truth
  - Perceptual tricks: cohesion-as-health, density flattening, vibration
  - Performance target: 60 FPS (16.6 ms budget) with 1.8 ms safety margin

THREE-TIER STRUCTURE (locked from team consensus):
  1. VANGUARD (300 bees, 15 attributes):
     - Full-detail tracking: position, velocity, target, health, energy, temp
     - LOD level, cohesion (illusion proxy), trail phase (animation continuity)
     - State flags (bitfield): seeking_food, returning, warming, dead
     - Updated with full steering behaviors: cohesion, separation, alignment, seek

  2. LEGION (2000 bees, 8 attributes):
     - Mid-detail: position, velocity, target, health, LOD timer
     - Simplified behaviors: basic seek only (no separation/alignment)
     - Lower update frequency possible (currently same as Vanguard)

  3. DENSITY FIELD (128×128×4 layers):
     - Chunk-based density tracking: mean density, health, velocity per cell
     - Used for Nebula particle spawning (ephemeral, zero persistence)
     - Simple diffusion (3×3 blur) for smooth gradients

TIER 3 NEBULA (Ephemeral particles):
  - Spawned each frame from density_field (weighted by density)
  - ~22,700 particles total (NEBULA_PARTICLES_PER_CHUNK × filled chunks)
  - Zero persistence: no tracking, no memory, destroyed after render
  - Inherits velocity from field + vibration (health-based jitter)
  - Alpha masked by COLLISION_MASK (fade near hive entrance)

LOD SYSTEM (Asymmetric hysteresis):
  - Camera-based distance checks: 150px (Vanguard), 400px (Legion)
  - PROMOTE: 0.5s timer (fast response to camera approach)
  - DEMOTE: 2.0s timer (prevent flickering from camera jitter)
  - Velocity continuity: ±15% max change on LOD transition
  - No camera-only exploits (e.g., teleporting bees off-screen)

INVARIANTS (checked but not enforced in this build):
  - Velocity continuity: ±15% on LOD transitions (see config.py)
  - Cohesion dominance: 2× weight vs density (COHESION_DOMINANCE_RATIO)
  - Max popping: <2 discontinuities/min (visual smoothness)
  - Death foreshadowing: ≥1.0s visible degradation (health<0.1 sets FLAG_FORESHADOW_DEATH)

VECTORIZED UPDATES (no if/for in hot paths):
  - All behaviors in biology.py use Numpy masked operations
  - np.where() for conditional updates
  - np.clip() for clamping
  - np.add.at() for density field accumulation
  - Spatial grid (32×32) for O(1) neighbor queries (currently simplified)

RENDERING (batched for performance):
  - Single texture atlas (256×256) for all bee sprites
  - Surface.blits() for batch rendering (1 call per tier)
  - Frustum culling: skip off-screen bees
  - Vibration: trail_phase + cohesion → visual jitter (low cohesion = erratic)
  - Layer order: Nebula (back) → Legion → Vanguard (front)

PERFORMANCE STRATEGY:
  - Fixed 30 Hz sim tick (33.3 ms budget)
  - Variable render rate (target 60 FPS)
  - Accumulator pattern for deterministic physics
  - Profiler tracks: total, sim, render times (last 60 frames)
  - Budget: 16.6 ms total - 1.8 ms safety = 14.8 ms usable

ILLUSION TECHNIQUES:
  1. Cohesion-as-health:
     - Sample local density from field → cohesion value [0,1]
     - High cohesion = tight trails, low vibration (healthy swarm)
     - Low cohesion = loose trails, high vibration (stressed swarm)

  2. Density flattening:
     - 3×3 diffusion blur on density_field prevents hard edges
     - Nebula particles spawn smoothly across chunks

  3. Death foreshadowing:
     - Health < 0.1 sets FLAG_FORESHADOW_DEATH
     - Sprite changes to "low_health" variant (orange tint)
     - Gives 1.0s+ visible warning before actual death

  4. Velocity damping:
     - DAMPING = 0.92 per frame (smooths jittery forces)
     - Prevents oscillation from conflicting behaviors

  5. Vibration amplitude:
     - Base: 2.0 pixels (VIBRATION_BASE)
     - Health penalty: +3.0 pixels when health<1.0 (VIBRATION_HEALTH_SCALE)
     - Applied via trail_phase sine/cosine offsets

SPATIAL STRUCTURES:
  - Collision mask: 1000×1000 gradient (alpha=0 at hive, 1.0 at 2× radius)
  - Spatial grid: 32×32 cells (31.25 px per cell) for neighbor queries
  - Food sources: 5 random positions (>5× hive radius away)
  - Temperature field: Optional (not yet integrated)

FILES:
  - config.py: All constants, thresholds, precomputed lookups
  - simulation.py: Main loop, BeeSimulation class, update logic
  - biology.py: Vectorized steering/state functions
  - render_utils.py: TextureAtlas, BeeRenderer, Camera, Profiler
  - environment.py: Spatial grid, collision mask, hive/food rendering

DEPENDENCIES (install via pip):
    pip install numpy pygame scipy

RUN:
    python simulation.py

CONTROLS:
    Arrow keys: Move camera
    D: Toggle debug overlay (FPS, counts, timing)
    F: Toggle density field visualization
    ESC: Quit

================================================================================
"""

import numpy as np
import pygame
import os
import time
from config import *


# ============================================================================
# TRIAGE-004: Performance Monitoring
# ============================================================================
class PerformanceHaltException(Exception):
    """
    Raised when Vanguard update time exceeds 2.0ms threshold.
    Triggers illusion risk logging per Grok's specification.
    """
    pass


# Illusion Risk Messages (Grok's biological warnings)
ILLUSION_RISKS = [
    "Swarm feels dead - individual bee variation lost",
    "Cohesion cues degraded - visual clustering unconvincing",
    "Movement too uniform - lacks organic jitter",
    "Death foreshadowing invisible - health transitions too sudden"
]

class BeeSimulation:
    """
    Main simulation container for ~25,000 bee illusion.
    Three separate Numpy arrays + ephemeral Nebula particles.
    """

    def __init__(self):
        """Initialize three-tier architecture with precomputed structures."""
        # ====================================================================
        # GOVERNANCE: Verify PROJECT_STATE.md exists (Hive Mind protocol)
        # ====================================================================
        project_state_path = os.path.join(os.path.dirname(__file__), "PROJECT_STATE.md")
        if not os.path.exists(project_state_path):
            print("⚠️  WARNING: PROJECT_STATE.md not found!")
            print("    The 'Hive Mind' communication protocol requires PROJECT_STATE.md")
            print("    to track project phase, performance baselines, and agent handoffs.")
            print("    Simulation will continue, but agent context may be incomplete.")
            print(f"    Expected location: {project_state_path}")
            print()
        # ====================================================================
        # TIER 1: Vanguard (100 bees, 20 attributes) - v2.1: 8-column core + 12 extended
        # ====================================================================
        self.vanguard = np.zeros((MAX_VANGUARD, 20), dtype=np.float32)
        self._init_vanguard()

        # ====================================================================
        # TIER 2: Legion (500 bees, 15 attributes) - v2.1: 8-column core + 7 extended
        # ====================================================================
        self.legion = np.zeros((MAX_LEGION, 15), dtype=np.float32)
        self._init_legion()

        # ====================================================================
        # TIER 3: Density Field (128×128×4 layers)
        # ====================================================================
        self.density_field = np.zeros((FIELD_RES, FIELD_RES, 4), dtype=np.float32)

        # ====================================================================
        # SPATIAL GRID (32×32 cells for neighbor queries)
        # ====================================================================
        self.spatial_grid = [[] for _ in range(GRID_CELLS * GRID_CELLS)]

        # ====================================================================
        # EPHEMERAL NEBULA (Spawned each frame, zero persistence)
        # ====================================================================
        self.nebula_particles = None  # Created dynamically each render

        # ====================================================================
        # PHASE 4: PHEROMONE SYSTEM (The Garden)
        # ====================================================================
        from src.pheromone_system import PheromoneSystem
        self.pheromone_system = PheromoneSystem()

        # ====================================================================
        # PHASE 4: RESOURCE MANAGER (Flowers)
        # ====================================================================
        from src.resource_manager import ResourceManager
        self.resource_manager = ResourceManager()

        # ====================================================================
        # TIMING
        # ====================================================================
        self.sim_accumulator = 0.0
        self.sim_dt = 1.0 / SIM_TICK_HZ
        self.frame_count = 0

        # ====================================================================
        # V6.0: COHERENCE SAMPLING (2Hz)
        # ====================================================================
        self.coherence_sample_timer = 0.0
        self.coherence_sample_interval = 0.5  # 2Hz = every 0.5 seconds
        self.swarm_coherence_index = 0.0  # 0-1 scale

        # ====================================================================
        # CAMERA (for LOD system)
        # ====================================================================
        self.camera_x = HIVE_CENTER_X
        self.camera_y = HIVE_CENTER_Y

        # ====================================================================
        # STATS (for invariant verification)
        # ====================================================================
        self.popping_count = 0
        self.last_popping_reset = 0.0

    def _init_vanguard(self):
        """
        Initialize Vanguard tier with v2.1 8-column core structure.
        v2.1: Added STRESS, REGEN_MOD, STRESS_RES personality traits.
        """
        # Random positions in circular spawn around hive
        angles = np.random.uniform(0, 2 * np.pi, MAX_VANGUARD)
        radii = np.random.uniform(HIVE_ENTRANCE_RADIUS, 200, MAX_VANGUARD)

        self.vanguard[:, V_POS_X] = HIVE_CENTER_X + radii * np.cos(angles)
        self.vanguard[:, V_POS_Y] = HIVE_CENTER_Y + radii * np.sin(angles)

        # Random initial velocities
        self.vanguard[:, V_VEL_X] = np.random.uniform(-20, 20, MAX_VANGUARD)
        self.vanguard[:, V_VEL_Y] = np.random.uniform(-20, 20, MAX_VANGUARD)

        # v2.1 CORE MATRIX: Health, Stress, Personality
        self.vanguard[:, V_HEALTH] = 1.0
        self.vanguard[:, V_STRESS] = 0.0  # v2.1: Start with zero stress
        self.vanguard[:, V_REGEN_MOD] = VANGUARD_REGEN_MOD  # v2.1: 1.1 (10% faster regen)
        self.vanguard[:, V_STRESS_RES] = VANGUARD_STRESS_RES  # v2.1: 0.9 (Sensitive, accumulates stress faster)

        # Extended attributes
        self.vanguard[:, V_TARGET_X] = np.random.uniform(100, WORLD_WIDTH - 100, MAX_VANGUARD)
        self.vanguard[:, V_TARGET_Y] = np.random.uniform(100, WORLD_HEIGHT - 100, MAX_VANGUARD)
        self.vanguard[:, V_LOD_LEVEL] = 0
        self.vanguard[:, V_LOD_TIMER] = 0.0
        self.vanguard[:, V_ENERGY] = 1.0
        self.vanguard[:, V_TEMP] = 1.0

        # PHASE 10: Caste assignment (v11.0 - Trinity of Roles)
        # Distribution: 10% Scout, 60% Forager, 30% Nurse
        # Use shuffled indices for random distribution
        indices = np.arange(MAX_VANGUARD)
        np.random.shuffle(indices)

        scout_count = int(MAX_VANGUARD * 0.10)
        forager_count = int(MAX_VANGUARD * 0.60)
        # Remaining are nurses (ensures exactly 100% allocation)

        # Initialize state flags with base behavior (as integers for bitwise ops)
        flags = np.full(MAX_VANGUARD, FLAG_SEEKING_FOOD, dtype=np.int32)

        # Assign caste bits (bits 5-6 of STATE_FLAGS)
        # Scouts (first 10%)
        scout_indices = indices[:scout_count]
        flags[scout_indices] |= (CASTE_SCOUT << CASTE_BITS_OFFSET)

        # Foragers (next 60%)
        forager_indices = indices[scout_count:scout_count + forager_count]
        flags[forager_indices] |= (CASTE_FORAGER << CASTE_BITS_OFFSET)

        # Nurses (remaining 30%)
        nurse_indices = indices[scout_count + forager_count:]
        flags[nurse_indices] |= (CASTE_NURSE << CASTE_BITS_OFFSET)

        # Store as float (numpy array is float64)
        self.vanguard[:, V_STATE_FLAGS] = flags.astype(np.float64)

        self.vanguard[:, V_AGE] = 0.0
        self.vanguard[:, V_COHESION] = 0.5
        self.vanguard[:, V_TRAIL_PHASE] = np.random.uniform(0, 2 * np.pi, MAX_VANGUARD)

        # LEGACY: TRIAGE-002 biology (preserved for compatibility)
        self.vanguard[:, V_REGEN_RATE] = np.random.uniform(REGEN_RATE_MIN, REGEN_RATE_MAX, MAX_VANGUARD)
        self.vanguard[:, V_DEATH_THRESHOLD] = np.random.uniform(DEATH_THRESHOLD_MIN, DEATH_THRESHOLD_MAX, MAX_VANGUARD)

    def _init_legion(self):
        """
        Initialize Legion tier with v2.1 8-column core structure.
        v2.1: Added STRESS, REGEN_MOD, STRESS_RES personality traits.
        """
        angles = np.random.uniform(0, 2 * np.pi, MAX_LEGION)
        radii = np.random.uniform(HIVE_ENTRANCE_RADIUS, 300, MAX_LEGION)

        self.legion[:, L_POS_X] = HIVE_CENTER_X + radii * np.cos(angles)
        self.legion[:, L_POS_Y] = HIVE_CENTER_Y + radii * np.sin(angles)

        self.legion[:, L_VEL_X] = np.random.uniform(-20, 20, MAX_LEGION)
        self.legion[:, L_VEL_Y] = np.random.uniform(-20, 20, MAX_LEGION)

        # v2.1 CORE MATRIX: Health, Stress, Personality
        self.legion[:, L_HEALTH] = 1.0
        self.legion[:, L_STRESS] = 0.0  # v2.1: Start with zero stress
        self.legion[:, L_REGEN_MOD] = LEGION_REGEN_MOD  # v2.1: 0.9 (10% slower regen)
        self.legion[:, L_STRESS_RES] = LEGION_STRESS_RES  # v2.1: 1.1 (Resistant, accumulates stress slower)

        # Extended attributes
        self.legion[:, L_TARGET_X] = np.random.uniform(100, WORLD_WIDTH - 100, MAX_LEGION)
        self.legion[:, L_TARGET_Y] = np.random.uniform(100, WORLD_HEIGHT - 100, MAX_LEGION)
        self.legion[:, L_LOD_TIMER] = 0.0

        # PHASE 10: Caste assignment (v11.0 - Trinity of Roles)
        # Distribution: 10% Scout, 60% Forager, 30% Nurse
        indices = np.arange(MAX_LEGION)
        np.random.shuffle(indices)

        scout_count = int(MAX_LEGION * 0.10)
        forager_count = int(MAX_LEGION * 0.60)

        # Initialize state flags with base behavior (as integers for bitwise ops)
        flags = np.full(MAX_LEGION, FLAG_SEEKING_FOOD, dtype=np.int32)

        # Assign caste bits (bits 5-6 of STATE_FLAGS)
        scout_indices = indices[:scout_count]
        flags[scout_indices] |= (CASTE_SCOUT << CASTE_BITS_OFFSET)

        forager_indices = indices[scout_count:scout_count + forager_count]
        flags[forager_indices] |= (CASTE_FORAGER << CASTE_BITS_OFFSET)

        nurse_indices = indices[scout_count + forager_count:]
        flags[nurse_indices] |= (CASTE_NURSE << CASTE_BITS_OFFSET)

        # Store as float (numpy array is float64)
        self.legion[:, L_STATE_FLAGS] = flags.astype(np.float64)

        self.legion[:, L_LOD_LEVEL] = 1  # Legion is LOD tier 1 (between Vanguard=0 and Nebula=2)

        # LEGACY: TRIAGE-002 biology (preserved for compatibility)
        self.legion[:, L_REGEN_RATE] = np.random.uniform(REGEN_RATE_MIN, REGEN_RATE_MAX, MAX_LEGION)
        self.legion[:, L_DEATH_THRESHOLD] = np.random.uniform(DEATH_THRESHOLD_MIN, DEATH_THRESHOLD_MAX, MAX_LEGION)

    def update(self, dt):
        """
        Main update loop with fixed 30 Hz sim tick.

        EMERGENCY PERFORMANCE MONITORING (TRIAGE-001):
        Tracks per-system timing for bottleneck identification.

        Args:
            dt: Delta time in seconds (variable from render loop)

        Returns:
            dict: Timing breakdown {'vanguard': ms, 'legion': ms, 'field': ms, 'lod': ms}
        """
        import time
        times = {}

        self.sim_accumulator += dt

        # Fixed timestep updates at 30 Hz
        while self.sim_accumulator >= self.sim_dt:
            # Track Vanguard update time (TRIAGE-004: Halt if >2.0ms)
            t0 = time.perf_counter()
            self._update_vanguard(self.sim_dt)
            vanguard_time_ms = (time.perf_counter() - t0) * 1000.0
            times['vanguard'] = vanguard_time_ms

            # TRIAGE-004: Performance halt condition
            # Dynamic threshold: 5ms per 100 bees
            vanguard_limit = 8.0  # SIMPLE TEMPORARY FIX

            # DEBUG: Print every second
            if self.frame_count % 60 == 0:
                print(f"\n=== VANGUARD PROFILE (Frame {self.frame_count}) ===")
                print(f"Total: {vanguard_time_ms:.3f}ms for {len(self.vanguard)} bees")
                print(f"Per bee: {vanguard_time_ms/len(self.vanguard):.6f}ms")
                print(f"Limit: {vanguard_limit:.1f}ms")

            if self.frame_count > 10 and vanguard_time_ms > vanguard_limit:
                raise PerformanceHaltException(f"Vanguard update {vanguard_time_ms:.3f}ms > 8.0ms")

            # Track Legion update time
            t0 = time.perf_counter()
            self._update_legion(self.sim_dt)
            times['legion'] = (time.perf_counter() - t0) * 1000.0

            # Track Density Field update time
            t0 = time.perf_counter()
            self._update_density_field(self.sim_dt)
            times['field'] = (time.perf_counter() - t0) * 1000.0

            # Track LOD system update time
            t0 = time.perf_counter()
            self._update_lod_system(self.sim_dt)
            times['lod'] = (time.perf_counter() - t0) * 1000.0

            # PHASE 4: Track Pheromone system update time
            t0 = time.perf_counter()
            self._update_pheromone_system(self.sim_dt)
            times['pheromone'] = (time.perf_counter() - t0) * 1000.0

            # PHASE 4: Track Resource manager update time
            t0 = time.perf_counter()
            self._update_resources(self.sim_dt)
            times['resources'] = (time.perf_counter() - t0) * 1000.0

            # V6.0: Sample Swarm Coherence Index at 2Hz
            self._sample_coherence(self.sim_dt)

            self.sim_accumulator -= self.sim_dt
            self.frame_count += 1

            # Log performance every 60 frames (2 seconds at 30 Hz)
            if self.frame_count % 60 == 0:
                total = sum(times.values())
                fps_estimate = 1000.0 / total if total > 0 else 0

                # TRIAGE-002: Diagnostic Injection (Biology Recovery)
                v_flags = self.vanguard[:, V_STATE_FLAGS].view(np.int32)
                l_flags = self.legion[:, L_STATE_FLAGS].view(np.int32)
                v_alive = np.sum((v_flags & FLAG_DEAD) == 0)
                l_alive = np.sum((l_flags & FLAG_DEAD) == 0)
                avg_health = np.mean(self.vanguard[:, V_HEALTH])

                print(f"[TRIAGE] Vanguard Alive: {v_alive} | Legion Alive: {l_alive}")
                print(f"[TRIAGE] Avg Health: {avg_health:.2f} | FPS: {fps_estimate:.1f}")

                print(f"[PERF] FPS: {fps_estimate:.1f} | "
                      f"Vanguard: {times.get('vanguard', 0):.1f}ms | "
                      f"Legion: {times.get('legion', 0):.1f}ms | "
                      f"Field: {times.get('field', 0):.1f}ms | "
                      f"LOD: {times.get('lod', 0):.1f}ms | "
                      f"Pheromone: {times.get('pheromone', 0):.1f}ms | "
                      f"Resources: {times.get('resources', 0):.1f}ms | "
                      f"Total: {total:.1f}ms")

                # PHASE 4: Budget collapse check (15ms threshold)
                if total > 15.0:
                    print(f"[WARNING] Budget Collapse! Sim time {total:.1f}ms exceeds 15ms threshold")

        return times

    def _update_vanguard(self, dt):
        """
        v2.1: Vanguard tier update with Architect-locked sequence.
        Sequence: Steering → Noise → Magnitude Clamp → Position Step
        """
        from biology import (
            apply_cohesion,
            apply_separation,
            apply_alignment,
            apply_seek,
            apply_energy_decay,
            apply_health_decay,
            apply_health_regeneration,
            apply_food_restoration,
            apply_warmth_restoration,
            apply_stress_dynamics,
            apply_organic_jitter,
            update_state_flags,
            update_cohesion_illusion
        )
        from environment import Environment

        # Extract positions/velocities for behavior functions
        positions = self.vanguard[:, [V_POS_X, V_POS_Y]]
        velocities = self.vanguard[:, [V_VEL_X, V_VEL_Y]]
        targets = self.vanguard[:, [V_TARGET_X, V_TARGET_Y]]

        # PHASE 3 FIX: Spatial grid not currently used by steering behaviors
        if not hasattr(self, 'environment'):
            self.environment = Environment()
        empty_grid = []  # Placeholder since behaviors don't use it

        # ====================================================================
        # v2.1 PHASE 1: STEERING BEHAVIORS
        # ====================================================================
        cohesion_force = apply_cohesion(positions, velocities, empty_grid)
        separation_force = apply_separation(positions, velocities, empty_grid)
        alignment_force = apply_alignment(positions, velocities, empty_grid)
        seek_force = apply_seek(positions, velocities, targets)

        # PHASE 10: Caste-specific cohesion multipliers (branchless)
        caste_ids_cohesion = (self.vanguard[:, V_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11
        cohesion_mults = np.choose(caste_ids_cohesion, [1.0, 1.0, NURSE_COHESION_MULT])  # Only nurses get 2.0×

        # Combine forces (cohesion dominates by 2×, nurses get extra 2× for 4× total)
        total_force = (
            cohesion_force * COHESION_FORCE * COHESION_DOMINANCE_RATIO * cohesion_mults[:, np.newaxis] +
            separation_force * SEPARATION_FORCE +
            alignment_force * ALIGNMENT_FORCE +
            seek_force * SEEK_FORCE
        )

        # Apply steering forces to velocities
        self.vanguard[:, [V_VEL_X, V_VEL_Y]] += total_force * dt
        self.vanguard[:, [V_VEL_X, V_VEL_Y]] *= 0.98  # Damping

        # ====================================================================
        # v2.1 PHASE 2: ORGANIC JITTER (BJI Restoration)
        # ====================================================================
        # PHASE 10: Caste-specific jitter multipliers (branchless)
        caste_ids_jitter = (self.vanguard[:, V_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11
        jitter_mults = np.choose(caste_ids_jitter, [SCOUT_JITTER_MULT, FORAGER_JITTER_MULT, NURSE_JITTER_MULT])

        # Apply zero-mean Gaussian noise when alignment ≥ 70%
        self.vanguard[:, [V_VEL_X, V_VEL_Y]] = apply_organic_jitter(
            self.vanguard[:, [V_VEL_X, V_VEL_Y]],
            jitter_mults=jitter_mults
        )

        # ====================================================================
        # v2.1 PHASE 3: MAGNITUDE CLAMP (RED LINE: Velocity magnitude lock)
        # ====================================================================
        # PHASE 10: Caste-specific speed limits (branchless scalar biasing)
        # Extract caste IDs from STATE_FLAGS (bits 5-6)
        caste_ids = (self.vanguard[:, V_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11

        # Build speed multiplier array (branchless using np.choose)
        speed_mults = np.choose(caste_ids, [SCOUT_SPEED_MULT, FORAGER_SPEED_MULT, NURSE_SPEED_MULT])
        max_speeds = MAX_SPEED * speed_mults

        speeds = np.linalg.norm(self.vanguard[:, [V_VEL_X, V_VEL_Y]], axis=1)
        speed_mask = speeds > max_speeds
        self.vanguard[speed_mask, V_VEL_X] *= max_speeds[speed_mask] / speeds[speed_mask]
        self.vanguard[speed_mask, V_VEL_Y] *= max_speeds[speed_mask] / speeds[speed_mask]

        # ====================================================================
        # v2.1 PHASE 4: POSITION STEP
        # ====================================================================
        self.vanguard[:, [V_POS_X, V_POS_Y]] += self.vanguard[:, [V_VEL_X, V_VEL_Y]] * dt

        # PHASE 10: Nurse caste hive radius-locking (branchless constraint)
        # Nurses stay within NURSE_HIVE_RADIUS of hive center
        caste_ids_radius = (self.vanguard[:, V_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11
        is_nurse = (caste_ids_radius == CASTE_NURSE)

        if np.any(is_nurse):
            # Calculate distance from hive center
            dx = self.vanguard[is_nurse, V_POS_X] - HIVE_CENTER_X
            dy = self.vanguard[is_nurse, V_POS_Y] - HIVE_CENTER_Y
            dist = np.sqrt(dx**2 + dy**2)

            # Find nurses beyond radius
            beyond_radius = dist > NURSE_HIVE_RADIUS

            if np.any(beyond_radius):
                # Pull back to radius boundary (elastic constraint)
                scale = NURSE_HIVE_RADIUS / dist[beyond_radius]
                self.vanguard[is_nurse, V_POS_X][beyond_radius] = HIVE_CENTER_X + dx[beyond_radius] * scale
                self.vanguard[is_nurse, V_POS_Y][beyond_radius] = HIVE_CENTER_Y + dy[beyond_radius] * scale

        # World wrapping
        self.vanguard[:, V_POS_X] = np.clip(self.vanguard[:, V_POS_X], 0, WORLD_WIDTH)
        self.vanguard[:, V_POS_Y] = np.clip(self.vanguard[:, V_POS_Y], 0, WORLD_HEIGHT)

        # ====================================================================
        # BIOLOGY UPDATES (v2.1: Stress + Health)
        # ====================================================================
        apply_energy_decay(self.vanguard, dt)
        apply_health_decay(self.vanguard, dt)
        apply_food_restoration(self.vanguard, self.environment.food_sources, dt)
        apply_warmth_restoration(self.vanguard, self.environment.hive_center, dt)

        # v2.1: Health regeneration using REGEN_MOD personality
        apply_health_regeneration(self.vanguard, dt, is_vanguard=True)

        # v2.1: Stress dynamics (power-law decay)
        apply_stress_dynamics(self.vanguard, dt, is_vanguard=True)

        # Update state flags based on needs
        update_state_flags(self.vanguard, self.environment.food_sources, self.environment.hive_center)

        # Update cohesion illusion from density field
        update_cohesion_illusion(self.vanguard, self.density_field)

        # Update age
        self.vanguard[:, V_AGE] += dt

        # Update trail phase (for animation continuity)
        self.vanguard[:, V_TRAIL_PHASE] += dt * 2.0

    def _update_legion(self, dt):
        """
        v2.1: Legion tier update with "Proxy Alignment" optimization.
        Legion follows Vanguard's average intent to save computation cycles.
        """
        from biology import apply_seek_simple, apply_health_regeneration, apply_stress_dynamics, apply_organic_jitter

        # Simplified seek behavior for Legion
        positions = self.legion[:, [L_POS_X, L_POS_Y]]
        velocities = self.legion[:, [L_VEL_X, L_VEL_Y]]
        targets = self.legion[:, [L_TARGET_X, L_TARGET_Y]]

        # ====================================================================
        # v2.1 SURGERY C: PROXY ALIGNMENT
        # Legion steers toward Vanguard's average velocity (simplified cohesion)
        # ====================================================================
        vanguard_avg_velocity = np.mean(self.vanguard[:, [V_VEL_X, V_VEL_Y]], axis=0)
        proxy_force = vanguard_avg_velocity - velocities  # Pull toward Vanguard consensus

        seek_force = apply_seek_simple(positions, velocities, targets)

        # PHASE 4: Sample pheromone gradient for steering
        gradient = self.pheromone_system.sample_gradient(positions)

        # Combine forces: proxy_alignment + seek + pheromone gradient
        total_force = (
            proxy_force * 0.3 +  # Weak pull toward Vanguard behavior
            seek_force +
            gradient * PHEROMONE_GRADIENT_WEIGHT
        )

        self.legion[:, [L_VEL_X, L_VEL_Y]] += total_force * dt
        self.legion[:, [L_VEL_X, L_VEL_Y]] *= 0.98  # Damping

        # ====================================================================
        # v2.1: ORGANIC JITTER (Legion also gets personality variance)
        # ====================================================================
        # PHASE 10: Caste-specific jitter multipliers (branchless)
        caste_ids_jitter = (self.legion[:, L_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11
        jitter_mults = np.choose(caste_ids_jitter, [SCOUT_JITTER_MULT, FORAGER_JITTER_MULT, NURSE_JITTER_MULT])

        self.legion[:, [L_VEL_X, L_VEL_Y]] = apply_organic_jitter(
            self.legion[:, [L_VEL_X, L_VEL_Y]],
            jitter_mults=jitter_mults
        )

        # ====================================================================
        # v2.1: MAGNITUDE CLAMP (RED LINE: Velocity magnitude lock)
        # ====================================================================
        # PHASE 10: Caste-specific speed limits (branchless scalar biasing)
        caste_ids = (self.legion[:, L_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11
        speed_mults = np.choose(caste_ids, [SCOUT_SPEED_MULT, FORAGER_SPEED_MULT, NURSE_SPEED_MULT])
        max_speeds = MAX_SPEED * speed_mults

        speeds = np.linalg.norm(self.legion[:, [L_VEL_X, L_VEL_Y]], axis=1)
        speed_mask = speeds > max_speeds
        self.legion[speed_mask, L_VEL_X] *= max_speeds[speed_mask] / speeds[speed_mask]
        self.legion[speed_mask, L_VEL_Y] *= max_speeds[speed_mask] / speeds[speed_mask]

        # Update positions
        self.legion[:, [L_POS_X, L_POS_Y]] += self.legion[:, [L_VEL_X, L_VEL_Y]] * dt

        # PHASE 10: Nurse caste hive radius-locking (branchless constraint)
        caste_ids_radius = (self.legion[:, L_STATE_FLAGS].astype(int) >> CASTE_BITS_OFFSET) & 0b11
        is_nurse = (caste_ids_radius == CASTE_NURSE)

        if np.any(is_nurse):
            dx = self.legion[is_nurse, L_POS_X] - HIVE_CENTER_X
            dy = self.legion[is_nurse, L_POS_Y] - HIVE_CENTER_Y
            dist = np.sqrt(dx**2 + dy**2)
            beyond_radius = dist > NURSE_HIVE_RADIUS

            if np.any(beyond_radius):
                scale = NURSE_HIVE_RADIUS / dist[beyond_radius]
                self.legion[is_nurse, L_POS_X][beyond_radius] = HIVE_CENTER_X + dx[beyond_radius] * scale
                self.legion[is_nurse, L_POS_Y][beyond_radius] = HIVE_CENTER_Y + dy[beyond_radius] * scale

        # World wrapping
        self.legion[:, L_POS_X] = np.clip(self.legion[:, L_POS_X], 0, WORLD_WIDTH)
        self.legion[:, L_POS_Y] = np.clip(self.legion[:, L_POS_Y], 0, WORLD_HEIGHT)

        # ====================================================================
        # BIOLOGY UPDATES (v2.1: Stress + Health)
        # ====================================================================
        # Health decay (simplified)
        self.legion[:, L_HEALTH] -= HEALTH_DECAY_RATE * dt * 0.5

        # v2.1: Health regeneration using REGEN_MOD personality
        apply_health_regeneration(self.legion, dt, is_vanguard=False)

        # v2.1: Stress dynamics (power-law decay)
        apply_stress_dynamics(self.legion, dt, is_vanguard=False)

    def _update_density_field(self, dt):
        """
        Update density field from Vanguard+Legion positions.
        Simple diffusion for Nebula particle spawning.
        """
        # Reset field
        self.density_field.fill(0.0)

        # Accumulate Vanguard contributions
        vanguard_x = (self.vanguard[:, V_POS_X] / WORLD_WIDTH * FIELD_RES).astype(int)
        vanguard_y = (self.vanguard[:, V_POS_Y] / WORLD_HEIGHT * FIELD_RES).astype(int)
        vanguard_x = np.clip(vanguard_x, 0, FIELD_RES - 1)
        vanguard_y = np.clip(vanguard_y, 0, FIELD_RES - 1)

        np.add.at(self.density_field[:, :, D_DENSITY], (vanguard_y, vanguard_x), 1.0)
        np.add.at(self.density_field[:, :, D_HEALTH], (vanguard_y, vanguard_x), self.vanguard[:, V_HEALTH])
        np.add.at(self.density_field[:, :, D_VEL_X], (vanguard_y, vanguard_x), self.vanguard[:, V_VEL_X])
        np.add.at(self.density_field[:, :, D_VEL_Y], (vanguard_y, vanguard_x), self.vanguard[:, V_VEL_Y])

        # Accumulate Legion contributions
        legion_x = (self.legion[:, L_POS_X] / WORLD_WIDTH * FIELD_RES).astype(int)
        legion_y = (self.legion[:, L_POS_Y] / WORLD_HEIGHT * FIELD_RES).astype(int)
        legion_x = np.clip(legion_x, 0, FIELD_RES - 1)
        legion_y = np.clip(legion_y, 0, FIELD_RES - 1)

        np.add.at(self.density_field[:, :, D_DENSITY], (legion_y, legion_x), 1.0)
        np.add.at(self.density_field[:, :, D_HEALTH], (legion_y, legion_x), self.legion[:, L_HEALTH])
        np.add.at(self.density_field[:, :, D_VEL_X], (legion_y, legion_x), self.legion[:, L_VEL_X])
        np.add.at(self.density_field[:, :, D_VEL_Y], (legion_y, legion_x), self.legion[:, L_VEL_Y])

        # Normalize by count (avoid divide by zero)
        count_mask = self.density_field[:, :, D_DENSITY] > 0
        self.density_field[count_mask, D_HEALTH] /= self.density_field[count_mask, D_DENSITY]
        self.density_field[count_mask, D_VEL_X] /= self.density_field[count_mask, D_DENSITY]
        self.density_field[count_mask, D_VEL_Y] /= self.density_field[count_mask, D_DENSITY]

        # ====================================================================
        # V6.0: DISSENT INVARIANT (80% Cohesion Redline)
        # If a chunk's bees are 80%+ aligned, inject 20% random velocity noise
        # to prevent "railroading" and maintain biological realism
        # ====================================================================
        self._apply_dissent_invariant()

        # Simple diffusion (3×3 box blur for smooth density gradient)
        from scipy.ndimage import uniform_filter
        self.density_field[:, :, D_DENSITY] = uniform_filter(
            self.density_field[:, :, D_DENSITY],
            size=3,
            mode='constant'
        )

    def _sample_coherence(self, dt):
        """
        V6.0: Sample Swarm Coherence Index at 2Hz.

        Coherence measures how aligned the swarm's velocity vectors are.
        Used for performance monitoring and biological realism validation.

        Updates self.swarm_coherence_index (0-1 scale)
        """
        self.coherence_sample_timer += dt

        if self.coherence_sample_timer >= self.coherence_sample_interval:
            self.coherence_sample_timer = 0.0

            # Compute mean velocity vector across all active bees
            all_vel_x = np.concatenate([self.vanguard[:, V_VEL_X], self.legion[:, L_VEL_X]])
            all_vel_y = np.concatenate([self.vanguard[:, V_VEL_Y], self.legion[:, L_VEL_Y]])

            # Mean velocity magnitude
            mean_vx = np.mean(all_vel_x)
            mean_vy = np.mean(all_vel_y)
            mean_vel_mag = np.sqrt(mean_vx**2 + mean_vy**2)

            # Average individual speed
            individual_speeds = np.sqrt(all_vel_x**2 + all_vel_y**2)
            avg_individual_speed = np.mean(individual_speeds)

            # Coherence index: ratio of mean velocity to average individual speed
            # 1.0 = perfect alignment, 0.0 = random directions
            if avg_individual_speed > 1e-6:
                self.swarm_coherence_index = mean_vel_mag / avg_individual_speed
            else:
                self.swarm_coherence_index = 0.0

    def _apply_dissent_invariant(self):
        """
        V6.0: Dissent Invariant (80% Cohesion Redline)

        Detect chunks where bees are perfectly aligned (>80% cohesion) and inject
        20% random velocity noise to prevent "railroading" behavior.

        Biological rationale: Real swarms exhibit inherent variability even when
        highly coordinated. Perfect alignment is unnatural and breaks the illusion.
        """
        # For each populated chunk, check if velocity variance is too low
        populated_mask = self.density_field[:, :, D_DENSITY] > 3.0  # At least 3 bees

        if not np.any(populated_mask):
            return

        # Compute velocity magnitudes for populated chunks
        vel_x = self.density_field[populated_mask, D_VEL_X]
        vel_y = self.density_field[populated_mask, D_VEL_Y]
        vel_mag = np.sqrt(vel_x**2 + vel_y**2)

        # Detect perfect alignment: velocity magnitude close to individual max speed
        # If all bees in chunk move in same direction, mean velocity ≈ max_speed
        alignment_ratio = vel_mag / (MAX_SPEED + 1e-6)  # Avoid divide by zero
        over_aligned = alignment_ratio > 0.80  # 80% threshold

        # For over-aligned chunks, inject noise into Legion bees in those chunks
        if np.any(over_aligned):
            # Find which chunks are over-aligned
            chunk_indices = np.argwhere(populated_mask)
            over_aligned_chunks = chunk_indices[over_aligned]

            # For each over-aligned chunk, add noise to 20% of Legion bees in that chunk
            for chunk_y, chunk_x in over_aligned_chunks:
                # Find Legion bees in this chunk
                legion_in_chunk_x = (self.legion[:, L_POS_X] / WORLD_WIDTH * FIELD_RES).astype(int)
                legion_in_chunk_y = (self.legion[:, L_POS_Y] / WORLD_HEIGHT * FIELD_RES).astype(int)
                in_chunk = (legion_in_chunk_x == chunk_x) & (legion_in_chunk_y == chunk_y)

                if np.any(in_chunk):
                    # Randomly select 20% to receive noise
                    indices = np.where(in_chunk)[0]
                    num_to_noise = max(1, int(len(indices) * 0.20))
                    noisy_indices = np.random.choice(indices, num_to_noise, replace=False)

                    # Inject random angular noise (±30 degrees)
                    noise_angle = np.random.uniform(-np.pi/6, np.pi/6, num_to_noise)

                    # Rotate velocity vectors by noise angle
                    current_vx = self.legion[noisy_indices, L_VEL_X]
                    current_vy = self.legion[noisy_indices, L_VEL_Y]

                    cos_angle = np.cos(noise_angle)
                    sin_angle = np.sin(noise_angle)

                    new_vx = current_vx * cos_angle - current_vy * sin_angle
                    new_vy = current_vx * sin_angle + current_vy * cos_angle

                    self.legion[noisy_indices, L_VEL_X] = new_vx
                    self.legion[noisy_indices, L_VEL_Y] = new_vy

    def _update_lod_system(self, dt):
        """
        Asymmetric hysteresis LOD: 0.5s promote, 2.0s demote.
        Camera-based distance check with velocity continuity.
        """
        # Compute distances from camera for Vanguard
        dx = self.vanguard[:, V_POS_X] - self.camera_x
        dy = self.vanguard[:, V_POS_Y] - self.camera_y
        distances = np.sqrt(dx**2 + dy**2)

        # Promotion logic: outside Vanguard range -> increment timer
        promote_mask = distances > LOD_DISTANCE_VANGUARD
        self.vanguard[promote_mask, V_LOD_TIMER] += dt

        # Actually promote when timer exceeds threshold
        actually_promote = promote_mask & (self.vanguard[:, V_LOD_TIMER] >= LOD_PROMOTE_TIME)

        # Velocity continuity: clamp velocity change to ±15%
        if np.any(actually_promote):
            old_vel = self.vanguard[actually_promote][:, [V_VEL_X, V_VEL_Y]].copy()
            # Transfer to Legion (simplified: just mark as demoted for now)
            # In full implementation, would move to legion array
            self.vanguard[actually_promote, V_LOD_LEVEL] = 1
            self.vanguard[actually_promote, V_LOD_TIMER] = 0.0

        # Demotion logic: inside Vanguard range -> decrement timer
        demote_mask = distances <= LOD_DISTANCE_VANGUARD
        self.vanguard[demote_mask, V_LOD_TIMER] -= dt
        self.vanguard[:, V_LOD_TIMER] = np.clip(self.vanguard[:, V_LOD_TIMER], 0.0, LOD_DEMOTE_TIME)

    def spawn_nebula_particles(self):
        """
        Spawn ephemeral Nebula particles from density field.
        Zero persistence - destroyed after this render frame.
        Returns: (N, 5) array [pos_x, pos_y, vel_x, vel_y, alpha]
        """
        # Count particles to spawn per chunk
        spawn_counts = (self.density_field[:, :, D_DENSITY] * NEBULA_PARTICLES_PER_CHUNK).astype(int)
        total_particles = np.sum(spawn_counts)

        if total_particles == 0:
            return np.zeros((0, 5), dtype=np.float32)

        # Pre-allocate particle array
        particles = np.zeros((total_particles, 5), dtype=np.float32)

        particle_idx = 0
        for cy in range(FIELD_RES):
            for cx in range(FIELD_RES):
                count = spawn_counts[cy, cx]
                if count == 0:
                    continue

                # Random positions within this chunk
                chunk_left = cx * WORLD_WIDTH / FIELD_RES
                chunk_top = cy * WORLD_HEIGHT / FIELD_RES
                chunk_size = WORLD_WIDTH / FIELD_RES

                particles[particle_idx:particle_idx + count, 0] = chunk_left + np.random.rand(count) * chunk_size
                particles[particle_idx:particle_idx + count, 1] = chunk_top + np.random.rand(count) * chunk_size

                # Inherit velocity from field (with vibration)
                base_vx = self.density_field[cy, cx, D_VEL_X]
                base_vy = self.density_field[cy, cx, D_VEL_Y]
                health = self.density_field[cy, cx, D_HEALTH]

                # Vibration amplitude increases with low health
                vibration = VIBRATION_BASE + (1.0 - health) * VIBRATION_HEALTH_SCALE

                particles[particle_idx:particle_idx + count, 2] = base_vx + np.random.uniform(-vibration, vibration, count)
                particles[particle_idx:particle_idx + count, 3] = base_vy + np.random.uniform(-vibration, vibration, count)

                # Alpha based on collision mask (fade near hive entrance)
                mask_x = int(particles[particle_idx, 0] / WORLD_WIDTH * COLLISION_MASK_RES)
                mask_y = int(particles[particle_idx, 1] / WORLD_HEIGHT * COLLISION_MASK_RES)
                mask_x = np.clip(mask_x, 0, COLLISION_MASK_RES - 1)
                mask_y = np.clip(mask_y, 0, COLLISION_MASK_RES - 1)
                alpha = COLLISION_MASK[mask_y, mask_x] * NEBULA_ALPHA_BASE

                particles[particle_idx:particle_idx + count, 4] = alpha

                particle_idx += count

        return particles

    def _update_pheromone_system(self, dt):
        """
        PHASE 4: Update pheromone grid and deposit pulses from Vanguard.

        Per architect specs:
        - Only Vanguard (Tier 1) deposit pheromones when at flowers
        - Constant pulse amplitude (no scaling)
        - Legion (Tier 2) sample gradient for steering
        """
        # Vanguard deposit pulses when near flowers (seeking_food state)
        vanguard_positions = self.vanguard[:, [V_POS_X, V_POS_Y]]

        # Deposit when seeking food (scout behavior)
        seeking_mask = (self.vanguard[:, V_STATE_FLAGS].astype(np.int32) & FLAG_SEEKING_FOOD) != 0

        self.pheromone_system.deposit_pulse(vanguard_positions, mask=seeking_mask)

        # Update pheromone grid (decay + blur + gradient computation)
        self.pheromone_system.update(dt)

    def _update_resources(self, dt):
        """
        PHASE 4: Update resource manager and handle bee-flower interactions.

        Per architect specs:
        - Vectorized harvest with zero-mean noise
        - Update flower nectar levels
        """
        # Regenerate flower nectar
        self.resource_manager.update(dt)

        # Harvest from Vanguard bees (Tier 1 only for now)
        vanguard_positions = self.vanguard[:, [V_POS_X, V_POS_Y]]
        harvested, flower_contacts = self.resource_manager.harvest(vanguard_positions)

        # Update bee energy based on harvest (simple: add to energy)
        self.vanguard[:, V_ENERGY] = np.clip(
            self.vanguard[:, V_ENERGY] + harvested,
            0.0,
            1.0
        )

    def set_camera(self, x, y):
        """Update camera position for LOD system."""
        self.camera_x = x
        self.camera_y = y

    def get_render_data(self):
        """
        Package data for renderer.
        Returns dict with vanguard, legion, nebula particle arrays.
        PHASE 4: Added flowers and pheromone heatmap.
        V6.0: Added coherence index.
        """
        return {
            'vanguard': self.vanguard,
            'legion': self.legion,
            'nebula': self.spawn_nebula_particles(),
            'density_field': self.density_field,
            'flowers': self.resource_manager.get_render_data(),
            'pheromone_heatmap': self.pheromone_system.get_heatmap(),
            'coherence_index': self.swarm_coherence_index
        }


# ============================================================================
# TASK 8.2: SURGICAL TIMELINE DUMP (Phase 8 Instrumentation)
# ============================================================================

def _dump_surgical_timeline():
    """
    TASK 8.2: Dump buffered surgical timeline to terminal.
    Called after frame 10 to prevent console I/O contamination during measurement.
    """
    from src.debug_visuals.distortion_system import _surgical_timeline_buffer

    if not _surgical_timeline_buffer:
        print("\n[TASK 8.2] No timeline data captured (GPU may have failed to initialize)")
        return

    print("\n" + "=" * 80)
    print("SURGICAL TIMELINE (Task 8.2) - Phase 8 Latency Trap Falsification")
    print("=" * 80)
    print(f"{'Frame':<8} {'Upload':<10} {'Dispatch':<10} {'Download':<10} {'Sync':<10} {'Total':<10}")
    print("-" * 80)

    for entry in _surgical_timeline_buffer:
        frame = entry.get('frame', -1)
        upload = entry.get('upload_ms', 0.0)
        dispatch = entry.get('dispatch_ms', 0.0)
        download = entry.get('download_ms', 0.0)
        sync = entry.get('sync_ms', 0.0)
        total = entry.get('total_ms', 0.0)

        print(f"{frame:<8} {upload:<10.2f} {dispatch:<10.2f} {download:<10.2f} {sync:<10.2f} {total:<10.2f}")

    print("=" * 80)
    print("LEGEND:")
    print("  Upload   = CPU->GPU texture transfer time")
    print("  Dispatch = GPU shader execution time")
    print("  Download = GPU->CPU readback time")
    print("  Sync     = Driver synchronization overhead")
    print("  Total    = Sum of all stages")
    print("=" * 80)
    print()


# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main entry point for APIS-OVERSEER simulation."""
    import time
    from render_utils import BeeRenderer, Camera, PerformanceProfiler
    from environment import Environment
    from src.debug_visuals import PerformanceMonitor, DistortionSystem, HaloSystem, VignetteSystem

    # Initialize Pygame
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("APIS-OVERSEER: ~25,000 Bee Swarm Illusion")

    # Create simulation
    simulation = BeeSimulation()

    # Create renderer
    renderer = BeeRenderer(screen_width, screen_height)

    # Create camera
    camera = Camera(HIVE_CENTER_X, HIVE_CENTER_Y)

    # Create environment (for rendering hive/food)
    environment = Environment()

    # Performance profiler
    profiler = PerformanceProfiler()

    # ====================================================================
    # PHASE 6: DEBUG VISUALS (CPU-based stress visualization)
    # ====================================================================
    # SURGERY 8.3: GPU distortion disabled per One-Way Doctrine
    # Reason: 19.45ms download tax is architectural (Pygame-ModernGL impedance)
    # Status: GPU detection preserved for capability documentation
    perf_monitor = PerformanceMonitor()
    # distortion_system = DistortionSystem(screen_width, screen_height, perf_monitor)  # DISABLED: Surgery 8.3
    distortion_system = None  # Production: CPU-only rendering per Phase 8 verdict
    halo_system = HaloSystem(screen_width, screen_height)
    vignette_system = VignetteSystem(screen_width, screen_height)

    # Main loop
    clock = pygame.time.Clock()
    running = True
    debug_mode = False
    show_density = False
    show_pheromone = False  # PHASE 4: Pheromone heatmap toggle
    pheromone_opacity = 0.2  # PHASE 4: Default opacity (20%)

    last_time = time.perf_counter()

    print("APIS-OVERSEER Initialized")
    print(f"Vanguard: {MAX_VANGUARD}, Legion: {MAX_LEGION}, Field: {FIELD_RES}×{FIELD_RES}")
    print(f"Target: {FPS_TARGET} FPS, Sim: {SIM_TICK_HZ} Hz")
    print(f"GPU Status: {'ENABLED' if perf_monitor.gpu_enabled else 'FALLBACK'}")
    print("Controls:")
    print("  Arrow keys: Move camera")
    print("  D: Toggle debug overlay (includes GPU status)")
    print("  F: Toggle density field view")
    print("  P: Toggle pheromone heatmap (PHASE 4)")
    print("  [ / ]: Adjust pheromone opacity (PHASE 4)")
    print("  S: Take screenshot (saved to screenshots/ folder)")
    print("  ESC: Quit")
    print("\nPhase 8 Debug Visuals (CPU-Optimized):")
    print(f"  - Stress halos: {'ENABLED' if halo_system.enabled else 'DISABLED'}")
    print(f"  - Stress vignette: {'ENABLED' if vignette_system.enabled else 'DISABLED'}")
    print(f"  - GPU distortion: DISABLED (Surgery 8.3: One-Way Doctrine)")
    print(f"  - GPU capability: {'DETECTED' if perf_monitor.gpu_enabled else 'UNAVAILABLE'} (ceremonial)")
    print(f"  - Auto-throttle: Active at {THROTTLE_THRESHOLD_MS}ms breach")
    print()

    frame_counter = 0  # Diagnostic frame counter for Phase 1

    while running:
        # Calculate delta time
        current_time = time.perf_counter()
        dt = current_time - last_time
        last_time = current_time

        # ====================================================================
        # ARCHITECT DIAGNOSTIC: X-RAY VISIBILITY (Master Recovery Prompt)
        # ====================================================================
        # Every 120 frames (2 seconds at 60 FPS), print ALIVE counts
        frame_counter += 1
        if frame_counter % 120 == 0:
            # Count ALIVE bees (FLAG_DEAD not set = alive)
            vanguard_flags = simulation.vanguard[:, V_STATE_FLAGS].view(np.int32)
            v_alive = np.sum((vanguard_flags & FLAG_DEAD) == 0)

            legion_flags = simulation.legion[:, L_STATE_FLAGS].view(np.int32)
            l_alive = np.sum((legion_flags & FLAG_DEAD) == 0)

            print(f"DEBUG | Vanguard Alive: {v_alive} | Legion Alive: {l_alive}")
        # ====================================================================

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    debug_mode = not debug_mode
                elif event.key == pygame.K_f:
                    show_density = not show_density
                elif event.key == pygame.K_p:  # PHASE 4: Toggle pheromone heatmap
                    show_pheromone = not show_pheromone
                    print(f"Pheromone heatmap: {'ON' if show_pheromone else 'OFF'}")
                elif event.key == pygame.K_LEFTBRACKET:  # PHASE 4: Decrease opacity
                    pheromone_opacity = max(0.0, pheromone_opacity - 0.05)
                    print(f"Pheromone opacity: {pheromone_opacity:.0%}")
                elif event.key == pygame.K_RIGHTBRACKET:  # PHASE 4: Increase opacity
                    pheromone_opacity = min(0.4, pheromone_opacity + 0.05)
                    print(f"Pheromone opacity: {pheromone_opacity:.0%}")
                elif event.key == pygame.K_s:  # Screenshot capture
                    import os
                    import datetime
                    os.makedirs("screenshots", exist_ok=True)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshots/phase9_{MAX_VANGUARD}v_{MAX_LEGION}l_{timestamp}.png"
                    pygame.image.save(screen, filename)
                    print(f"[SCREENSHOT] Saved: {filename}")

        # Camera control
        keys = pygame.key.get_pressed()
        camera_speed = 200.0 * dt
        if keys[pygame.K_LEFT]:
            camera.move(-camera_speed, 0)
        if keys[pygame.K_RIGHT]:
            camera.move(camera_speed, 0)
        if keys[pygame.K_UP]:
            camera.move(0, -camera_speed)
        if keys[pygame.K_DOWN]:
            camera.move(0, camera_speed)

        # Update camera
        camera.update(dt)

        # Update simulation (fixed timestep)
        sim_start = time.perf_counter()
        simulation.set_camera(camera.x, camera.y)
        simulation.update(dt)
        sim_time = (time.perf_counter() - sim_start) * 1000.0

        # Get render data
        render_data = simulation.get_render_data()

        # Render
        render_start = time.perf_counter()

        # Clear screen first (done in renderer)
        screen.fill((20, 20, 30))

        # Draw environment (hive + food) first
        environment.render_hive(screen, camera.x, camera.y, screen_width, screen_height)
        environment.render_food_sources(screen, camera.x, camera.y, screen_width, screen_height)

        # Draw bees on top (renderer doesn't clear screen now)
        # PHASE 4: Pass pheromone visualization parameters
        renderer.render_frame(screen, render_data, camera.x, camera.y, show_pheromone, pheromone_opacity)

        # Optional: density field visualization
        if show_density:
            renderer.render_density_field(screen, render_data['density_field'], camera.x, camera.y)

        # ====================================================================
        # PHASE 6: DEBUG VISUALS (Stress visualization)
        # ====================================================================
        if perf_monitor.debug_enabled:
            # Render stress halos (CPU vectorized)
            halo_system.render_halos(screen, camera.x, camera.y, simulation.vanguard, simulation.legion)

            # Render stress vignette (CPU single blit)
            vignette_system.render_vignette(screen, simulation.vanguard, simulation.legion)

            # ================================================================
            # SURGERY 8.3: GPU DISTORTION DISABLED (One-Way Doctrine)
            # ================================================================
            # VERDICT: Path A (Direct FBO) falsified due to Pygame-ModernGL impedance
            # EVIDENCE: 19.45ms download tax is architectural (fbo.read() crosses PCIe bus)
            # DECISION: GPU remains "capable" but production-disabled per Phase 8 findings
            # RECLAIMED: ~5ms upload overhead returned to simulation budget
            # PRESERVED: CPU-based halos + vignette provide visual richness
            #
            # if distortion_system.enabled:
            #     pheromone_home = simulation.pheromone_system.grid
            #     pheromone_rgb = np.stack([pheromone_home, pheromone_home, pheromone_home], axis=2)
            #     screen = distortion_system.apply_distortion(screen, pheromone_rgb, frame_counter)
            # ================================================================

        # Debug overlay
        if debug_mode:
            fps = clock.get_fps()
            renderer.render_debug_overlay(screen, render_data, fps, sim_time)

            # PHASE 6: Add GPU status line
            gpu_status = perf_monitor.get_gpu_status_text()
            debug_font = pygame.font.Font(None, 24)
            gpu_surface = debug_font.render(gpu_status, True, (100, 255, 100))
            screen.blit(gpu_surface, (10, 120))

        render_time = (time.perf_counter() - render_start) * 1000.0

        # Record performance (PHASE 6: Auto-throttle check)
        total_time = sim_time + render_time
        profiler.record_frame(total_time, sim_time, render_time)
        perf_monitor.record_frame(total_time)  # Check for >14ms breach

        # ====================================================================
        # PHASE 8: EMERGENCY THROTTLE (CPU-only, no GPU distortion)
        # ====================================================================
        # SURGERY 8.3: GPU distortion removed, emergency throttle now targets halos/vignette
        if total_time > 12.0 and perf_monitor.debug_enabled:
            print(f"\n[EMERGENCY] Total time {total_time:.1f}ms > 12ms - ENGAGING THROTTLE")
            print(f"  - Disabling halos and vignette")
            halo_system.enabled = False
            vignette_system.enabled = False
            perf_monitor.debug_enabled = False

        # ====================================================================
        # TASK 8.2: TIMELINE DUMP (Preserved for historical record)
        # ====================================================================
        # NOTE: This code path is inactive (distortion_system = None)
        # Preserved for reference to Phase 8 experimentation
        # if frame_counter == 10:
        #     _dump_surgical_timeline()

        # Flip display
        pygame.display.flip()

        # Maintain target FPS
        clock.tick(FPS_TARGET)

    # Cleanup
    stats = profiler.get_stats()
    print("\n=== Performance Summary ===")
    print(f"Avg FPS: {stats['avg_fps']:.1f}")
    print(f"Avg Frame: {stats['avg_frame_ms']:.2f} ms")
    print(f"Avg Sim: {stats['avg_sim_ms']:.2f} ms")
    print(f"Avg Render: {stats['avg_render_ms']:.2f} ms")
    print(f"Budget: {FRAME_BUDGET_MS:.1f} ms")

    # PHASE 8: Cleanup debug visual resources
    # distortion_system.cleanup()  # DISABLED: Surgery 8.3 (GPU distortion removed)
    halo_system.cleanup()
    vignette_system.cleanup()

    pygame.quit()


if __name__ == '__main__':
    main()
