"""
APIS-OVERSEER Biology Behaviors
Vectorized steering and state updates (no loops)
All functions operate on Numpy arrays
"""

import numpy as np
from config import *

# ============================================================================
# STEERING BEHAVIORS (Vectorized)
# ============================================================================

def apply_cohesion(positions, velocities, spatial_grid):
    """
    Cohesion: steer toward average position of neighbors.

    Args:
        positions: (N, 2) array of [x, y]
        velocities: (N, 2) array of [vx, vy]
        spatial_grid: List of neighbor indices per grid cell

    Returns:
        (N, 2) force vectors
    """
    N = len(positions)
    forces = np.zeros((N, 2), dtype=np.float32)

    # Simplified: for performance, use global average instead of per-neighbor query
    # Full implementation would use spatial_grid for local neighbors
    center_of_mass = np.mean(positions, axis=0)
    desired = center_of_mass - positions

    # Normalize and scale
    norms = np.linalg.norm(desired, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)  # Avoid divide by zero
    desired = desired / norms * MAX_SPEED

    forces = desired - velocities
    return forces


def apply_separation(positions, velocities, spatial_grid):
    """
    Separation: steer away from nearby neighbors.
    TRIAGE-005 ROLLBACK: Legacy vectorized approximation (no O(N²) loop)

    Args:
        positions: (N, 2) array
        velocities: (N, 2) array
        spatial_grid: List of neighbor indices

    Returns:
        (N, 2) force vectors
    """
    N = len(positions)
    forces = np.zeros((N, 2), dtype=np.float32)

    # LEGACY APPROACH: Simple repulsion from center of mass
    # This is much faster than pairwise distance checks
    # Trade-off: Less accurate but avoids O(N²) performance collapse
    center_of_mass = np.mean(positions, axis=0)

    # Repel weakly from center (creates spreading effect)
    diff = positions - center_of_mass
    dist = np.linalg.norm(diff, axis=1, keepdims=True)

    # Avoid divide by zero
    dist = np.where(dist > 0, dist, 1.0)

    # Normalize and scale (weaker than cohesion)
    forces = (diff / dist) * MAX_SPEED * 0.3

    return forces


def apply_alignment(positions, velocities, spatial_grid):
    """
    Alignment: steer toward average heading of neighbors.

    Args:
        positions: (N, 2) array
        velocities: (N, 2) array
        spatial_grid: List of neighbor indices

    Returns:
        (N, 2) force vectors
    """
    N = len(positions)

    # Simplified: use global average velocity
    avg_velocity = np.mean(velocities, axis=0)
    desired = np.tile(avg_velocity, (N, 1))

    # Normalize
    norms = np.linalg.norm(desired, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    desired = desired / norms * MAX_SPEED

    forces = desired - velocities
    return forces


def apply_seek(positions, velocities, targets):
    """
    Seek: steer toward target position.

    Args:
        positions: (N, 2) array
        velocities: (N, 2) array
        targets: (N, 2) array of target [x, y]

    Returns:
        (N, 2) force vectors
    """
    desired = targets - positions

    # Normalize and scale to max speed
    norms = np.linalg.norm(desired, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    desired = desired / norms * MAX_SPEED

    forces = desired - velocities
    return forces


def apply_seek_simple(positions, velocities, targets):
    """
    Simplified seek for Legion tier (less precise).

    Args:
        positions: (N, 2) array
        velocities: (N, 2) array
        targets: (N, 2) array

    Returns:
        (N, 2) force vectors
    """
    desired = targets - positions

    # Normalize
    norms = np.linalg.norm(desired, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    desired = desired / norms * MAX_SPEED * 0.7  # Slower response

    forces = desired - velocities
    return forces * 0.5  # Weaker force for Legion


# ============================================================================
# BIOLOGY UPDATES (Vectorized)
# ============================================================================

def apply_energy_decay(vanguard, dt):
    """
    Decay energy over time (vectorized).

    Args:
        vanguard: (N, 17) array - TRIAGE-002: Updated to 17 columns
        dt: Delta time in seconds
    """
    vanguard[:, V_ENERGY] -= ENERGY_DECAY_RATE * dt

    # Clamp to [0, 1]
    vanguard[:, V_ENERGY] = np.clip(vanguard[:, V_ENERGY], 0.0, 1.0)

    # Mark low-energy bees for death foreshadowing - TRIAGE-002: view as int32
    low_energy_mask = vanguard[:, V_ENERGY] < 0.2
    flags_int = vanguard[low_energy_mask, V_STATE_FLAGS].view(np.int32)
    vanguard[low_energy_mask, V_STATE_FLAGS] = (flags_int | FLAG_FORESHADOW_DEATH).view(np.float32)


def apply_health_decay(vanguard, dt):
    """
    Decay health when cold or hungry (vectorized).
    TRIAGE-002: Uses individual death thresholds.

    Args:
        vanguard: (N, 17) array - TRIAGE-002: Now 17 columns with REGEN_RATE, DEATH_THRESHOLD
        dt: Delta time in seconds
    """
    # Health decays when temp < threshold OR energy < threshold
    cold_mask = vanguard[:, V_TEMP] < WARMTH_THRESHOLD
    hungry_mask = vanguard[:, V_ENERGY] < HUNGER_THRESHOLD

    decay_mask = cold_mask | hungry_mask
    vanguard[decay_mask, V_HEALTH] -= HEALTH_DECAY_RATE * dt

    # Clamp to [0, 1]
    vanguard[:, V_HEALTH] = np.clip(vanguard[:, V_HEALTH], 0.0, 1.0)

    # TRIAGE-002: Mark for death foreshadowing using individual thresholds
    # Each bee has its own death threshold (0.08-0.12)
    critical_mask = vanguard[:, V_HEALTH] < vanguard[:, V_DEATH_THRESHOLD]
    if np.any(critical_mask):
        flags_int = vanguard[critical_mask, V_STATE_FLAGS].view(np.int32)
        vanguard[critical_mask, V_STATE_FLAGS] = (flags_int | FLAG_FORESHADOW_DEATH).view(np.float32)

    # Actually mark as dead when health reaches 0
    dead_mask = vanguard[:, V_HEALTH] <= 0.0
    if np.any(dead_mask):
        flags_int = vanguard[dead_mask, V_STATE_FLAGS].view(np.int32)
        vanguard[dead_mask, V_STATE_FLAGS] = (flags_int | FLAG_DEAD).view(np.float32)


def apply_food_restoration(vanguard, food_positions, dt):
    """
    TRIAGE-004: Fully vectorized food restoration (no Python loops).

    Uses broadcasting to create (N_bees, M_food) distance matrix.

    Args:
        vanguard: (N, 17) array - TRIAGE-002: Updated to 17 columns
        food_positions: (M, 2) array of food source locations
        dt: Delta time in seconds
    """
    if len(food_positions) == 0:
        return

    positions = vanguard[:, [V_POS_X, V_POS_Y]]  # (N, 2)

    # Vectorized distance calculation: (N, M) matrix via broadcasting
    # positions: (N, 2) → (N, 1, 2)
    # food_positions: (M, 2) → (1, M, 2)
    # Result: (N, M) distance matrix
    dx = positions[:, np.newaxis, 0] - food_positions[np.newaxis, :, 0]  # (N, M)
    dy = positions[:, np.newaxis, 1] - food_positions[np.newaxis, :, 1]  # (N, M)
    distances = np.sqrt(dx**2 + dy**2)  # (N, M)

    # Find bees near ANY food source (within 30px)
    near_any_food = np.any(distances < 30.0, axis=1)  # (N,) boolean

    # Restore energy for bees near food
    vanguard[near_any_food, V_ENERGY] += FOOD_RESTORE_RATE * dt

    # Clamp energy
    vanguard[:, V_ENERGY] = np.clip(vanguard[:, V_ENERGY], 0.0, 1.0)


def apply_warmth_restoration(vanguard, hive_center, dt):
    """
    Restore temperature when near hive (vectorized).

    Args:
        vanguard: (N, 15) array
        hive_center: (2,) array [x, y]
        dt: Delta time in seconds
    """
    positions = vanguard[:, [V_POS_X, V_POS_Y]]
    dist = np.linalg.norm(positions - hive_center, axis=1)

    near_hive = dist < HIVE_ENTRANCE_RADIUS * 2.0
    vanguard[near_hive, V_TEMP] += WARMTH_RESTORE_RATE * dt

    # Clamp temperature
    vanguard[:, V_TEMP] = np.clip(vanguard[:, V_TEMP], 0.0, 1.0)


def apply_health_regeneration(state_array, dt, is_vanguard=True):
    """
    v2.1: Health regeneration using personality-driven REGEN_MOD.
    Replaces TRIAGE-002's individual REGEN_RATE with uniform personality tiers.

    Args:
        state_array: (N, 20) Vanguard or (N, 15) Legion array
        dt: Delta time in seconds
        is_vanguard: True for Vanguard tier, False for Legion tier

    Returns:
        None (modifies state_array in place)
    """
    if is_vanguard:
        health_col = V_HEALTH
        regen_mod_col = V_REGEN_MOD
        flag_col = V_STATE_FLAGS
    else:
        health_col = L_HEALTH
        regen_mod_col = L_REGEN_MOD
        flag_col = L_STATE_FLAGS

    # Only regenerate health for ALIVE bees (FLAG_DEAD not set)
    flags = state_array[:, flag_col].view(np.int32)
    alive_mask = (flags & FLAG_DEAD) == 0

    # v2.1: Base regen rate modulated by personality (REGEN_MOD)
    # Vanguard: 1.1 (10% faster), Legion: 0.9 (10% slower)
    base_regen = REGEN_RATE_MAX  # Use legacy max as base (0.0012)
    state_array[alive_mask, health_col] += (
        base_regen * state_array[alive_mask, regen_mod_col] * dt
    )

    # Clamp to [0, 1]
    state_array[:, health_col] = np.clip(state_array[:, health_col], 0.0, 1.0)


def apply_stress_dynamics(state_array, dt, is_vanguard=True):
    """
    v2.1: Stress accumulation and power-law decay.

    Stress equation: decay = 0.1*x + 0.9*x^1.5
    - Below 0.3: Fast decay (power-law dominates)
    - Above 0.3: Slower decay (linear component stabilizes)

    Args:
        state_array: (N, 20) Vanguard or (N, 15) Legion array
        dt: Delta time in seconds
        is_vanguard: True for Vanguard tier, False for Legion tier
    """
    if is_vanguard:
        stress_col = V_STRESS
        stress_res_col = V_STRESS_RES
        health_col = V_HEALTH
        flag_col = V_STATE_FLAGS
    else:
        stress_col = L_STRESS
        stress_res_col = L_STRESS_RES
        health_col = L_HEALTH
        flag_col = L_STATE_FLAGS

    # Only apply stress to ALIVE bees
    flags = state_array[:, flag_col].view(np.int32)
    alive_mask = (flags & FLAG_DEAD) == 0

    # Stress accumulation (modulated by personality resistance)
    # Vanguard (0.9): accumulates 11% faster, Legion (1.1): 10% slower
    stress_gain = STRESS_ACCUMULATION_RATE * dt / state_array[alive_mask, stress_res_col]
    state_array[alive_mask, stress_col] += stress_gain

    # Power-law decay: 0.1*x + 0.9*x^1.5
    x = state_array[alive_mask, stress_col]
    decay_amount = (0.1 * x + 0.9 * np.power(x, STRESS_DECAY_POWER)) * dt
    state_array[alive_mask, stress_col] -= decay_amount

    # Clamp to [0, 1]
    state_array[:, stress_col] = np.clip(state_array[:, stress_col], 0.0, 1.0)

    # Stress affects health (optional degradation)
    # High stress (>0.7) slowly damages health
    high_stress = (state_array[:, stress_col] > 0.7) & alive_mask
    if np.any(high_stress):
        state_array[high_stress, health_col] -= 0.002 * dt


def apply_organic_jitter(velocities, alignment_threshold=ORGANIC_JITTER_THRESHOLD, jitter_mults=None):
    """
    v2.1: Inject Gaussian noise when swarm alignment is high.
    v11.0 (PHASE 10): Added caste-specific jitter multipliers.

    Prevents "railroading" by adding zero-mean jitter to velocity.
    Applied AFTER steering forces but BEFORE magnitude clamping.

    Args:
        velocities: (N, 2) array of velocity vectors
        alignment_threshold: Trigger jitter when alignment ≥ this value (0.70 default)
        jitter_mults: (N,) array of caste-specific jitter multipliers (PHASE 10)

    Returns:
        (N, 2) modified velocities with jitter
    """
    N = len(velocities)

    # Compute global alignment: how uniform are velocity directions?
    avg_velocity = np.mean(velocities, axis=0)
    avg_vel_mag = np.linalg.norm(avg_velocity)

    if avg_vel_mag < 1e-6:
        return velocities  # No alignment if swarm is stationary

    # Normalized average direction
    avg_direction = avg_velocity / avg_vel_mag

    # Compute alignment for each bee (dot product with avg direction)
    vel_mags = np.linalg.norm(velocities, axis=1, keepdims=True)
    vel_mags = np.where(vel_mags > 0, vel_mags, 1.0)
    normalized_vel = velocities / vel_mags

    alignment = np.abs(np.sum(normalized_vel * avg_direction, axis=1))

    # Inject jitter for highly aligned bees
    high_alignment = alignment >= alignment_threshold

    if np.any(high_alignment):
        # PHASE 10: Apply caste-specific jitter multipliers
        if jitter_mults is not None:
            # Extract multipliers for high-alignment bees
            active_mults = jitter_mults[high_alignment]
            # Vectorized Gaussian noise with caste-specific std deviation
            noise = np.random.normal(0, 1.0, size=(np.sum(high_alignment), 2))
            noise *= (ORGANIC_JITTER_STD * MAX_SPEED * active_mults[:, np.newaxis])
            velocities[high_alignment] += noise
        else:
            # Legacy path: uniform jitter
            noise = np.random.normal(0, ORGANIC_JITTER_STD * MAX_SPEED, size=(np.sum(high_alignment), 2))
            velocities[high_alignment] += noise

    return velocities


def update_cohesion_illusion(vanguard, density_field):
    """
    Update cohesion values based on local density (illusion proxy).
    Trail tightness and vibration are driven by this value.

    Args:
        vanguard: (N, 20) array - v2.1: expanded to 20 columns
        density_field: (128, 128, 4) array
    """
    positions = vanguard[:, [V_POS_X, V_POS_Y]]

    # Map positions to density field
    field_x = (positions[:, 0] / WORLD_WIDTH * FIELD_RES).astype(int)
    field_y = (positions[:, 1] / WORLD_HEIGHT * FIELD_RES).astype(int)
    field_x = np.clip(field_x, 0, FIELD_RES - 1)
    field_y = np.clip(field_y, 0, FIELD_RES - 1)

    # Sample density at each bee's position
    local_density = density_field[field_y, field_x, D_DENSITY]

    # Normalize to [0, 1] and store as cohesion
    # Higher density = tighter trails, less vibration
    vanguard[:, V_COHESION] = np.clip(local_density / 10.0, 0.0, 1.0)


# ============================================================================
# STATE MACHINE (Vectorized)
# ============================================================================

def update_state_flags(vanguard, food_positions, hive_center):
    """
    Update state flags based on energy/temp thresholds (vectorized).

    Args:
        vanguard: (N, 15) array
        food_positions: (M, 2) array
        hive_center: (2,) array
    """
    # Clear old state flags (except death flags) - TRIAGE-002: view as int32
    flags_int = vanguard[:, V_STATE_FLAGS].view(np.int32)
    death_flags = (flags_int & (FLAG_DEAD | FLAG_FORESHADOW_DEATH)).view(np.float32)
    vanguard[:, V_STATE_FLAGS] = death_flags

    # Low energy -> seek food
    low_energy = vanguard[:, V_ENERGY] < HUNGER_THRESHOLD
    if np.any(low_energy):
        flags_int = vanguard[low_energy, V_STATE_FLAGS].view(np.int32)
        vanguard[low_energy, V_STATE_FLAGS] = (flags_int | FLAG_SEEKING_FOOD).view(np.float32)

    # Low temp -> seek warmth (return to hive)
    low_temp = vanguard[:, V_TEMP] < WARMTH_THRESHOLD
    if np.any(low_temp):
        flags_int = vanguard[low_temp, V_STATE_FLAGS].view(np.int32)
        vanguard[low_temp, V_STATE_FLAGS] = (flags_int | (FLAG_WARMING | FLAG_RETURNING)).view(np.float32)

    # Update targets based on state
    positions = vanguard[:, [V_POS_X, V_POS_Y]]

    # --- SEEKING FOOD: PURE VECTORIZED NEAREST-NEIGHBOR ---
    flags_int = vanguard[:, V_STATE_FLAGS].view(np.int32)
    seeking_food_mask = (flags_int & FLAG_SEEKING_FOOD) > 0  # (N,) boolean

    if np.any(seeking_food_mask) and len(food_positions) > 0:
        # 1. Extract seeking positions
        seeking_positions = positions[seeking_food_mask]  # (K, 2)

        # 2. Broadcast squared distances (K, M)
        dx = seeking_positions[:, np.newaxis, 0] - food_positions[np.newaxis, :, 0]
        dy = seeking_positions[:, np.newaxis, 1] - food_positions[np.newaxis, :, 1]
        dist_sq = dx**2 + dy**2

        # 3. Single argmin call
        nearest_indices = np.argmin(dist_sq, axis=1)

        # 4. Direct assignment (no intermediates)
        vanguard[seeking_food_mask, V_TARGET_X] = food_positions[nearest_indices, 0]
        vanguard[seeking_food_mask, V_TARGET_Y] = food_positions[nearest_indices, 1]

    # Warming: target hive center - TRIAGE-002: view as int32
    warming = (flags_int & FLAG_WARMING) > 0
    vanguard[warming, V_TARGET_X] = hive_center[0]
    vanguard[warming, V_TARGET_Y] = hive_center[1]


# ============================================================================
# SPATIAL GRID UTILITIES
# ============================================================================

def rebuild_spatial_grid(positions, grid_cells=GRID_CELLS):
    """
    Rebuild spatial hash grid for neighbor queries.

    Args:
        positions: (N, 2) array
        grid_cells: Number of grid cells per axis

    Returns:
        List of lists containing bee indices per cell
    """
    spatial_grid = [[] for _ in range(grid_cells * grid_cells)]

    cell_size = WORLD_WIDTH / grid_cells

    for i, pos in enumerate(positions):
        cell_x = int(pos[0] / cell_size)
        cell_y = int(pos[1] / cell_size)
        cell_x = np.clip(cell_x, 0, grid_cells - 1)
        cell_y = np.clip(cell_y, 0, grid_cells - 1)

        cell_idx = cell_y * grid_cells + cell_x
        spatial_grid[cell_idx].append(i)

    return spatial_grid


def query_neighbors(position, spatial_grid, grid_cells=GRID_CELLS, radius=NEIGHBOR_QUERY_RADIUS):
    """
    Query neighbors within radius using spatial grid.

    Args:
        position: (2,) array [x, y]
        spatial_grid: List of lists
        grid_cells: Number of grid cells
        radius: Query radius

    Returns:
        List of neighbor indices
    """
    cell_size = WORLD_WIDTH / grid_cells
    cell_x = int(position[0] / cell_size)
    cell_y = int(position[1] / cell_size)

    # Query surrounding 3×3 cells
    neighbors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            cx = cell_x + dx
            cy = cell_y + dy

            if 0 <= cx < grid_cells and 0 <= cy < grid_cells:
                cell_idx = cy * grid_cells + cx
                neighbors.extend(spatial_grid[cell_idx])

    return neighbors
