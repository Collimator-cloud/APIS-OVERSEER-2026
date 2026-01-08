"""
APIS-OVERSEER Configuration
Locked architecture constants for ~25,000 bee illusion
"""

import numpy as np

# ============================================================================
# POPULATION TIERS (Strict limits)
# ============================================================================
# EMERGENCY PERFORMANCE SCALE REDUCTION (TRIAGE-001)
# Temporary 3x reduction to reach 30 FPS target
# Original: 300 Vanguard + 2000 Legion = ~25,000 illusion
# Current:  100 Vanguard +  500 Legion = ~8,300 illusion
MAX_VANGUARD = 100      # Full-detail bees (TEMP: was 300)
MAX_LEGION = 500        # Mid-detail bees (TEMP: was 2000)
FIELD_RES = 128         # Density field resolution (128x128 chunks)
NEBULA_PARTICLES_PER_CHUNK = 0.6  # ~4,900 ephemeral particles (TEMP: was 1.4 → ~22,700)

# ============================================================================
# ARRAY COLUMN INDICES
# ============================================================================
# Vanguard (300, 17) columns - TRIAGE-002: Added REGEN_RATE, DEATH_THRESHOLD
V_POS_X = 0
V_POS_Y = 1
V_VEL_X = 2
V_VEL_Y = 3
V_TARGET_X = 4
V_TARGET_Y = 5
V_LOD_LEVEL = 6      # 0=Vanguard, 1=Legion, 2=Nebula
V_LOD_TIMER = 7      # Countdown for hysteresis
V_HEALTH = 8
V_ENERGY = 9
V_TEMP = 10
V_STATE_FLAGS = 11   # Bitfield: 0=seeking_food, 1=returning, 2=warming, etc.
V_AGE = 12
V_COHESION = 13      # Neighbor density (illusion proxy)
V_TRAIL_PHASE = 14   # For animation continuity
V_REGEN_RATE = 15    # TRIAGE-002: Individual health regen rate (0.0008-0.0012)
V_DEATH_THRESHOLD = 16  # TRIAGE-002: Individual death threshold (0.08-0.12)

# Legion (2000, 12) columns - EXPANDED FOR PHASE 2 + TRIAGE-002
L_POS_X = 0
L_POS_Y = 1
L_VEL_X = 2
L_VEL_Y = 3
L_TARGET_X = 4
L_TARGET_Y = 5
L_HEALTH = 6
L_LOD_TIMER = 7
L_STATE_FLAGS = 8    # PHASE 2: Bitfield for FLAG_ALIVE, FLAG_DEAD, etc.
L_LOD_LEVEL = 9      # PHASE 2: LOD level (always 1 for Legion tier)
L_REGEN_RATE = 10    # TRIAGE-002: Individual health regen rate (0.0008-0.0012)
L_DEATH_THRESHOLD = 11  # TRIAGE-002: Individual death threshold (0.08-0.12)

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

# TRIAGE-002: Individual Biology (Pre-seeded Personality)
REGEN_RATE_MIN = 0.0008      # Min health regeneration per second
REGEN_RATE_MAX = 0.0012      # Max health regeneration per second
DEATH_THRESHOLD_MIN = 0.08   # Min death threshold (health)
DEATH_THRESHOLD_MAX = 0.12   # Max death threshold (health)

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
DISTORTION_ENABLED = True        # Enable GPU distortion shader (auto-disabled if GPU unavailable)
DISTORTION_AMPLITUDE = 8.0       # Max pixel displacement (pixels)
DISTORTION_FREQUENCY = 0.5       # Perlin noise frequency

# Halo System (Bee stress indicators)
HALO_ENABLED = True              # Enable stress halos around bees
HALO_RADIUS = 32                 # Halo texture size (pixels)
HALO_CULL_DISTANCE = 1.5         # Cull factor (1.5x diagonal = visible bees only)

# Vignette System (Screen-space stress overlay)
VIGNETTE_ENABLED = True          # Enable stress vignette
VIGNETTE_INNER_RADIUS = 0.6      # Inner radius (normalized 0-1)
VIGNETTE_OUTER_RADIUS = 1.0      # Outer radius (normalized 0-1)

# ============================================================================
# INITIALIZATION
# ============================================================================
SIGMOID_LUT = create_sigmoid_lut()
COLLISION_MASK = create_collision_mask()
