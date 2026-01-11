"""
APIS-OVERSEER Configuration
Locked architecture constants for ~25,000 bee illusion
"""

import numpy as np

# ============================================================================
# POPULATION TIERS (Strict limits)
# ============================================================================
# PHASE 9.3: 1,200-BEE PRIMARY TARGET (v9.3 Safe-Colony Baseline)
# Phase 9.2 closed: 1,000 bees @ 7.99ms median, BJI 4.1-4.2 (LOCKED)
# Original: 300 Vanguard + 2000 Legion = ~25,000 illusion
# Phase 9.3: 100 Vanguard + 1100 Legion = 1,200 total (primary target)
MAX_VANGUARD = 100      # Full-detail bees (Phase 9: maintained at 100)
MAX_LEGION = 1100       # Mid-detail bees (Phase 9.3: scaled from 900 → 1100)
FIELD_RES = 128         # Density field resolution (128x128 chunks)
NEBULA_PARTICLES_PER_CHUNK = 0.6  # ~4,900 ephemeral particles (TEMP: was 1.4 → ~22,700)

# ============================================================================
# ARRAY COLUMN INDICES
# ============================================================================
# v2.1 VERSIONED CONTRACT: 8-Column Core + Extended Attributes
# Core columns (0-7) are the "Master State Matrix" (Architect-locked)
# Extended columns (8+) are implementation-specific

# ============================================================================
# VANGUARD TIER (100 bees, 20 columns total)
# ============================================================================
# Core Matrix (0-7): Position, Velocity, Health, Stress, Personality
V_POS_X = 0
V_POS_Y = 1
V_VEL_X = 2
V_VEL_Y = 3
V_HEALTH = 4         # v2.1: Core column 4 (was 8)
V_STRESS = 5         # v2.1: NEW - Stress accumulation [0.0-1.0]
V_REGEN_MOD = 6      # v2.1: NEW - Personality: regen modifier (1.1 = Vanguard default)
V_STRESS_RES = 7     # v2.1: NEW - Personality: stress resistance (0.9 = Sensitive default)

# Extended Attributes (8-19): Implementation-specific
V_TARGET_X = 8
V_TARGET_Y = 9
V_LOD_LEVEL = 10     # 0=Vanguard, 1=Legion, 2=Nebula
V_LOD_TIMER = 11     # Countdown for hysteresis
V_ENERGY = 12
V_TEMP = 13
V_STATE_FLAGS = 14   # Bitfield: 0=seeking_food, 1=returning, 2=warming, etc.
V_AGE = 15
V_COHESION = 16      # Neighbor density (illusion proxy)
V_TRAIL_PHASE = 17   # For animation continuity
V_REGEN_RATE = 18    # LEGACY: Individual health regen rate (0.0008-0.0012) - subsumed by REGEN_MOD
V_DEATH_THRESHOLD = 19  # LEGACY: Individual death threshold (0.08-0.12)

# ============================================================================
# LEGION TIER (500 bees, 15 columns total)
# ============================================================================
# Core Matrix (0-7): Position, Velocity, Health, Stress, Personality
L_POS_X = 0
L_POS_Y = 1
L_VEL_X = 2
L_VEL_Y = 3
L_HEALTH = 4         # v2.1: Core column 4 (was 6)
L_STRESS = 5         # v2.1: NEW - Stress accumulation [0.0-1.0]
L_REGEN_MOD = 6      # v2.1: NEW - Personality: regen modifier (0.9 = Legion default)
L_STRESS_RES = 7     # v2.1: NEW - Personality: stress resistance (1.1 = Resistant default)

# Extended Attributes (8-14): Implementation-specific
L_TARGET_X = 8
L_TARGET_Y = 9
L_LOD_TIMER = 10
L_STATE_FLAGS = 11   # PHASE 2: Bitfield for FLAG_ALIVE, FLAG_DEAD, etc.
L_LOD_LEVEL = 12     # PHASE 2: LOD level (always 1 for Legion tier)
L_REGEN_RATE = 13    # LEGACY: Individual health regen rate (0.0008-0.0012) - subsumed by REGEN_MOD
L_DEATH_THRESHOLD = 14  # LEGACY: Individual death threshold (0.08-0.12)

# Density Field (128, 128, 4) layers
D_DENSITY = 0        # Mean bee count per chunk
D_HEALTH = 1         # Mean health (for vibration amplitude)
D_VEL_X = 2          # Mean velocity X
D_VEL_Y = 3          # Mean velocity Y

# ============================================================================
# LOD SYSTEM (Asymmetric hysteresis)
# ============================================================================
LOD_PROMOTE_TIME = 0.5   # 0.5s to promote (faster response)
LOD_DEMOTE_TIME = 2.0    # 2.0s to demote (prevent flickering)
LOD_DISTANCE_VANGUARD = 150.0   # Camera radius for Vanguard tier
LOD_DISTANCE_LEGION = 400.0     # Camera radius for Legion tier

# ============================================================================
# INVARIANTS
# ============================================================================
VELOCITY_CONTINUITY = 0.15       # Max ±15% velocity change on LOD transition
COHESION_DOMINANCE_RATIO = 2.0   # Cohesion weight must be 2× density weight
MAX_POPPING_PER_MINUTE = 2.0     # Visual discontinuities limit
DEATH_FORESHADOW_TIME = 1.0      # Min 1.0s visible degradation before death

# ============================================================================
# WORLD DIMENSIONS
# ============================================================================
WORLD_WIDTH = 1000
WORLD_HEIGHT = 1000
HIVE_CENTER_X = 500
HIVE_CENTER_Y = 500
HIVE_ENTRANCE_RADIUS = 30

# ============================================================================
# SPATIAL GRID
# ============================================================================
GRID_CELLS = 32             # 32×32 grid for neighbor queries
GRID_CELL_SIZE = WORLD_WIDTH / GRID_CELLS
NEIGHBOR_QUERY_RADIUS = 50.0

# ============================================================================
# PHYSICS
# ============================================================================
MAX_SPEED = 80.0             # pixels/sec
COHESION_FORCE = 0.6
SEPARATION_FORCE = 0.4
ALIGNMENT_FORCE = 0.3
SEEK_FORCE = 0.5
DAMPING = 0.92               # Velocity damping per frame
VIBRATION_BASE = 2.0         # Base vibration amplitude (pixels)
VIBRATION_HEALTH_SCALE = 3.0 # Extra vibration when health low

# ============================================================================
# BIOLOGY
# ============================================================================
ENERGY_DECAY_RATE = 0.02     # per second
HEALTH_DECAY_RATE = 0.01     # per second when cold/hungry
WARMTH_THRESHOLD = 0.6
HUNGER_THRESHOLD = 0.5
FOOD_RESTORE_RATE = 0.3      # per second at food source
WARMTH_RESTORE_RATE = 0.4    # per second at hive

# TRIAGE-002: Individual Biology (Pre-seeded Personality) - LEGACY
REGEN_RATE_MIN = 0.0008      # Min health regeneration per second
REGEN_RATE_MAX = 0.0012      # Max health regeneration per second
DEATH_THRESHOLD_MIN = 0.08   # Min death threshold (health)
DEATH_THRESHOLD_MAX = 0.12   # Max death threshold (health)

# ============================================================================
# v2.1 VERSIONED CONTRACT: Stress & Personality System
# ============================================================================
# Stress Dynamics (Architect-locked piecewise power-law)
STRESS_DECAY_POWER = 1.5             # Power-law exponent for stress decay
STRESS_ACCUMULATION_RATE = 0.05      # Stress gain per second (base rate)
STRESS_RECOVERY_THRESHOLD = 0.3      # Below this, stress decays faster

# Personality Modifiers (Pre-seeded at spawn)
VANGUARD_REGEN_MOD = 1.1             # Vanguard: 10% faster health regen
VANGUARD_STRESS_RES = 0.9            # Vanguard: Sensitive (90% stress resistance, accumulates faster)
LEGION_REGEN_MOD = 0.9               # Legion: 10% slower health regen
LEGION_STRESS_RES = 1.1              # Legion: Resistant (110% stress resistance, accumulates slower)

# Organic Jitter (BJI restoration)
ORGANIC_JITTER_STD = 0.12            # Gaussian noise std (12% of MAX_SPEED)
ORGANIC_JITTER_THRESHOLD = 0.70      # Apply jitter when alignment ≥ 70%

# ============================================================================
# RENDERING
# ============================================================================
FPS_TARGET = 60
SIM_TICK_HZ = 30             # 30 Hz physics updates
FRAME_BUDGET_MS = 16.6
SAFETY_MARGIN_MS = 1.8
BEE_SPRITE_SIZE = 8          # pixels (before scaling)
TEXTURE_ATLAS_SIZE = 256     # Single atlas for all bee states

# Render layers (draw order)
LAYER_NEBULA = 0
LAYER_LEGION = 1
LAYER_VANGUARD = 2

# ============================================================================
# NEBULA TIER 3 (Ephemeral particles)
# ============================================================================
NEBULA_SPAWN_THRESHOLD = 0.1  # Min density to spawn particles
NEBULA_ALPHA_BASE = 0.3       # Base alpha for distant particles
NEBULA_ALPHA_FADE = 0.7       # Alpha multiplier near exclusion zones
NEBULA_LIFETIME = 0.0         # Zero persistence (destroyed each frame)

# ============================================================================
# PRECOMPUTED LOOKUPS
# ============================================================================
SIGMOID_LUT_STEPS = 60        # For smooth LOD blends
COLLISION_MASK_RES = 1000     # Collision gradient resolution

# ============================================================================
# STATE FLAGS (Bitfield encoding)
# ============================================================================
FLAG_SEEKING_FOOD = 1 << 0
FLAG_RETURNING = 1 << 1
FLAG_WARMING = 1 << 2
FLAG_DEAD = 1 << 3
FLAG_FORESHADOW_DEATH = 1 << 4

# ============================================================================
# PHASE 10: CASTE SYSTEM (v11.0 - Trinity of Roles)
# ============================================================================
# Caste IDs stored in bits 5-6 of STATE_FLAGS (3 states need 2 bits)
# Extraction: (flags >> 5) & 0b11
CASTE_SCOUT = 0      # 10% of population - Explorers
CASTE_FORAGER = 1    # 60% of population - Resource gatherers
CASTE_NURSE = 2      # 30% of population - Hive workers/guards

# Caste bit masks for STATE_FLAGS manipulation
CASTE_BITS_OFFSET = 5
CASTE_BITS_MASK = 0b11 << CASTE_BITS_OFFSET  # Bits 5-6

# Caste behavioral modifiers (branchless scalar multipliers)
# Scout modifiers (10% - fast, erratic explorers)
SCOUT_SPEED_MULT = 1.2        # 20% faster movement
SCOUT_JITTER_MULT = 2.0       # 2× organic jitter (high exploration randomness)
SCOUT_PHEROMONE_MULT = 1.5    # 50% stronger pheromone deposits

# Forager modifiers (60% - standard resource gatherers)
FORAGER_SPEED_MULT = 1.0      # Standard speed
FORAGER_JITTER_MULT = 1.0     # Standard jitter
FORAGER_GRADIENT_MULT = 1.3   # 30% more sensitive to pheromone gradients

# Nurse/Guard modifiers (30% - hive-bound workers)
NURSE_SPEED_MULT = 0.5        # 50% slower (hive workers)
NURSE_JITTER_MULT = 0.6       # 40% less jitter (stable workers)
NURSE_COHESION_MULT = 2.0     # 2× cohesion force (tight clustering)
NURSE_HIVE_RADIUS = 250.0     # Max distance from hive center (pixels)

# ============================================================================
# PHASE 4: PHEROMONE SYSTEM (The Garden)
# ============================================================================
PHEROMONE_GRID_SIZE = 128        # 128x128 pheromone grid
PHEROMONE_UPDATE_HZ = 30         # Update frequency (matches sim tick)
PHEROMONE_DECAY_FACTOR = 0.94    # Exponential decay per frame (30 Hz)
PHEROMONE_PULSE_AMPLITUDE = 1.0  # Constant pulse strength (vanguard only)
PHEROMONE_GRADIENT_WEIGHT = 0.3  # Steering influence (persuasion, not command)
PHEROMONE_GRADIENT_CLAMP = 5.0   # Max gradient magnitude for steering

# ============================================================================
# PHASE 4: RESOURCE MANAGER (Flowers)
# ============================================================================
NUM_FLOWERS = 5                  # Fixed flower count
FLOWER_HARVEST_BASE = 0.1        # Base harvest amount per contact
FLOWER_HARVEST_NOISE_STD = 0.15  # Noise standard deviation
FLOWER_CONTACT_RADIUS = 20.0     # Contact distance (pixels)
FLOWER_NECTAR_MAX = 1.0          # Max nectar per flower
FLOWER_NECTAR_REGEN = 0.01       # Nectar regeneration per frame (30 Hz)

# ============================================================================
# PRECOMPUTE HELPERS
# ============================================================================
def create_sigmoid_lut():
    """Precompute sigmoid for smooth LOD transitions."""
    x = np.linspace(-6, 6, SIGMOID_LUT_STEPS)
    return 1.0 / (1.0 + np.exp(-x))

def create_collision_mask():
    """Precompute gradient falloff around hive entrance (Zone 3 alpha=0 near choke)."""
    mask = np.ones((COLLISION_MASK_RES, COLLISION_MASK_RES), dtype=np.float32)
    y, x = np.ogrid[:COLLISION_MASK_RES, :COLLISION_MASK_RES]
    center_x = HIVE_CENTER_X / WORLD_WIDTH * COLLISION_MASK_RES
    center_y = HIVE_CENTER_Y / WORLD_HEIGHT * COLLISION_MASK_RES
    dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)

    # Gradient falloff: alpha=0 within entrance, linear to 1.0 at 2× radius
    entrance_cells = HIVE_ENTRANCE_RADIUS / WORLD_WIDTH * COLLISION_MASK_RES
    mask = np.clip((dist - entrance_cells) / entrance_cells, 0.0, 1.0)
    return mask

# ============================================================================
# PHASE 6: DEBUG VISUALS & GPU INTEGRATION
# ============================================================================
# Per Architect Spec [ARCH-SDL-PHASE6-002]:
# - ModernGL standalone context for shader-based stress visuals
# - ≤1.0ms total debug budget, ≤0.3ms GPU shader budget
# - Auto-throttle at 14ms frame time breach

# Debug Visual Limits
MAX_DEBUG_HALOS = 3000           # Max bees to render halos for (culled by distance)
THROTTLE_THRESHOLD_MS = 14.0     # Auto-disable debug if frame time exceeds this
GPU_TEXTURE_BUDGET_MB = 10       # Maximum GPU texture memory usage
GPU_SHADER_BUDGET_MS = 0.3       # Maximum GPU shader time per frame

# GPU Requirements (checked by performance_monitor.py)
GPU_MIN_OPENGL_VERSION = (3, 3)  # ModernGL requires OpenGL 3.3+
GPU_MIN_TEXTURE_SIZE = 2048      # Minimum texture dimension support

# Distortion System (Pheromone-driven stress shimmer)
DISTORTION_ENABLED = False       # Enable GPU distortion shader (auto-disabled if GPU unavailable)
DISTORTION_AMPLITUDE = 8.0       # Max pixel displacement (pixels)
DISTORTION_FREQUENCY = 0.5       # Perlin noise frequency

# Halo System (Bee stress indicators)
HALO_ENABLED = False             # Enable stress halos around bees
HALO_RADIUS = 32                 # Halo texture size (pixels)
HALO_CULL_DISTANCE = 1.5         # Cull factor (1.5x diagonal = visible bees only)

# Vignette System (Screen-space stress overlay)
VINGNETTE_ENABLED = False         # Enable stress vignette
VIGNETTE_INNER_RADIUS = 0.6      # Inner radius (normalized 0-1)
VIGNETTE_OUTER_RADIUS = 1.0      # Outer radius (normalized 0-1)

# ============================================================================
# INITIALIZATION
# ============================================================================
SIGMOID_LUT = create_sigmoid_lut()
COLLISION_MASK = create_collision_mask()
