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

    Args:
        positions: (N, 2) array
        velocities: (N, 2) array
        spatial_grid: List of neighbor indices

    Returns:
        (N, 2) force vectors
    """
    N = len(positions)
    forces = np.zeros((N, 2), dtype=np.float32)

    # Simplified pairwise repulsion (full version uses spatial grid)
    for i in range(N):
        diff = positions[i] - positions
        dist = np.linalg.norm(diff, axis=1)

        # Only repel from very close neighbors (< 20 pixels)
        close_mask = (dist > 0) & (dist < 20.0)
        if np.any(close_mask):
            diff[close_mask] /= dist[close_mask, np.newaxis]  # Normalize
            diff[close_mask] /= dist[close_mask, np.newaxis]  # Weight by inverse distance
            forces[i] = np.sum(diff[close_mask], axis=0)

    # Normalize
    norms = np.linalg.norm(forces, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    forces = forces / norms * MAX_SPEED * 0.5

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
    TRIAGE-002: Apply individual health regeneration to all alive bees.

    This is the "Zero-Allocation Biology" fix that restores the hollow hive.
    Each bee regenerates health at their pre-seeded individual rate.

    Args:
        state_array: (N, 17) Vanguard or (N, 12) Legion array
        dt: Delta time in seconds
        is_vanguard: True for Vanguard tier, False for Legion tier

    Returns:
        None (modifies state_array in place)
    """
    if is_vanguard:
        health_col = V_HEALTH
        regen_col = V_REGEN_RATE
        flag_col = V_STATE_FLAGS
    else:
        health_col = L_HEALTH
        regen_col = L_REGEN_RATE
        flag_col = L_STATE_FLAGS

    # Only regenerate health for ALIVE bees (FLAG_DEAD not set)
    flags = state_array[:, flag_col].view(np.int32)
    alive_mask = (flags & FLAG_DEAD) == 0

    # Vectorized regeneration using individual rates
    state_array[alive_mask, health_col] += state_array[alive_mask, regen_col] * dt

    # Clamp to [0, 1]
    state_array[:, health_col] = np.clip(state_array[:, health_col], 0.0, 1.0)


def update_cohesion_illusion(vanguard, density_field):
    """
    Update cohesion values based on local density (illusion proxy).
    Trail tightness and vibration are driven by this value.

    Args:
        vanguard: (N, 15) array
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

    # Seeking food: target nearest food - TRIAGE-002: view as int32
    flags_int = vanguard[:, V_STATE_FLAGS].view(np.int32)
    seeking_food = (flags_int & FLAG_SEEKING_FOOD) > 0
    if np.any(seeking_food) and len(food_positions) > 0:
        for i in np.where(seeking_food)[0]:
            # Find nearest food
            dists = np.linalg.norm(food_positions - positions[i], axis=1)
            nearest_idx = np.argmin(dists)
            vanguard[i, V_TARGET_X] = food_positions[nearest_idx, 0]
            vanguard[i, V_TARGET_Y] = food_positions[nearest_idx, 1]

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
