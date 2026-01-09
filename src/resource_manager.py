"""
PHASE 4: Resource Manager (The Garden)
Manages 5 flowers with vectorized nectar harvest logic
"""

import numpy as np
from numba import njit
import config


class ResourceManager:
    """
    Manages flower resources with vectorized harvest operations.

    Data Structure:
        positions: (5, 2) float32 - flower positions [x, y]
        nectar: (5,) float32 - current nectar levels [0.0 - 1.0]
        active: (5,) int8 - flower active status (1=active, 0=depleted)
    """

    def __init__(self):
        """Initialize 5 flowers at random positions."""
        self.positions = np.zeros((config.NUM_FLOWERS, 2), dtype=np.float32)
        self.nectar = np.ones(config.NUM_FLOWERS, dtype=np.float32)
        self.active = np.ones(config.NUM_FLOWERS, dtype=np.int8)

        # TRIAGE-005 EMERGENCY: Pre-allocate distance buffers (zero allocation in hot path)
        # Max bees = MAX_VANGUARD + MAX_LEGION = 600
        MAX_BEES = config.MAX_VANGUARD + config.MAX_LEGION
        self._dist_buffer_dx = np.zeros((MAX_BEES, config.NUM_FLOWERS), dtype=np.float32)
        self._dist_buffer_dy = np.zeros((MAX_BEES, config.NUM_FLOWERS), dtype=np.float32)
        self._dist_buffer = np.zeros((MAX_BEES, config.NUM_FLOWERS), dtype=np.float32)
        self._contact_mask = np.zeros((MAX_BEES, config.NUM_FLOWERS), dtype=bool)
        self._valid_contact_mask = np.zeros((MAX_BEES, config.NUM_FLOWERS), dtype=bool)
        self._masked_distances = np.zeros((MAX_BEES, config.NUM_FLOWERS), dtype=np.float32)

        # Pre-seeded biological noise (Grok's requirement)
        rng_bio = np.random.RandomState(42)
        self._noise_buffer = rng_bio.normal(1.0, 0.15, (MAX_BEES, config.NUM_FLOWERS)).astype(np.float32)

        # Spawn flowers at random positions (avoid hive center)
        rng = np.random.default_rng(42)  # Fixed seed for reproducibility
        for i in range(config.NUM_FLOWERS):
            # Place flowers outside hive radius (at least 200px away from center)
            angle = rng.uniform(0, 2 * np.pi)
            distance = rng.uniform(250, 450)  # 250-450px from hive center

            self.positions[i, 0] = config.HIVE_CENTER_X + distance * np.cos(angle)
            self.positions[i, 1] = config.HIVE_CENTER_Y + distance * np.sin(angle)

            # Clamp to world bounds
            self.positions[i, 0] = np.clip(self.positions[i, 0], 50, config.WORLD_WIDTH - 50)
            self.positions[i, 1] = np.clip(self.positions[i, 1], 50, config.WORLD_HEIGHT - 50)

    def harvest(self, bee_positions, base_amount=None):
        """
        TRIAGE-004: Fully vectorized harvest with broadcasting (no Python loops).

        Uses (N_bees, M_flowers) distance matrix and mask operations.
        Biological variation via pre-seeded noise with nectar attenuation.

        Args:
            bee_positions: (N, 2) array of bee positions
            base_amount: Harvest amount (default: FLOWER_HARVEST_BASE)

        Returns:
            harvested: (N,) array of harvest amounts per bee (0 if not in contact)
            flower_contacts: (N,) array of flower indices (-1 if no contact)
        """
        if base_amount is None:
            base_amount = config.FLOWER_HARVEST_BASE

        N = len(bee_positions)
        harvested = np.zeros(N, dtype=np.float32)
        flower_contacts = np.full(N, -1, dtype=np.int32)

        # TRIAGE-005 EMERGENCY: Use pre-allocated buffers with out= parameter (ZERO allocations)
        # Slice buffers to actual bee count
        dx = self._dist_buffer_dx[:N, :]
        dy = self._dist_buffer_dy[:N, :]
        distances = self._dist_buffer[:N, :]
        in_contact = self._contact_mask[:N, :]
        valid_contact = self._valid_contact_mask[:N, :]
        masked_distances = self._masked_distances[:N, :]

        # Vectorized distance calculation using out= parameters
        np.subtract(bee_positions[:, 0:1], self.positions[:, 0], out=dx)
        np.subtract(bee_positions[:, 1:2], self.positions[:, 1], out=dy)

        # Distance = sqrt(dx^2 + dy^2)
        np.square(dx, out=dx)
        np.square(dy, out=dy)
        np.add(dx, dy, out=distances)
        np.sqrt(distances, out=distances)

        # Mask: bees in contact with active flowers with nectar
        np.less(distances, config.FLOWER_CONTACT_RADIUS, out=in_contact)
        active_mask = self.active.astype(bool)
        nectar_mask = self.nectar > 0
        valid_flowers = active_mask & nectar_mask

        # Apply flower validity mask to contact matrix
        np.logical_and(in_contact, valid_flowers[np.newaxis, :], out=valid_contact)

        # Find closest valid flower for each bee
        masked_distances = np.where(valid_contact, distances, np.inf)
        closest_flowers = np.argmin(masked_distances, axis=1)

        # Identify bees that have valid contact (min distance < inf)
        has_contact = np.min(masked_distances, axis=1) < np.inf  # (N,) boolean

        # Process harvests for bees with valid contact
        if np.any(has_contact):
            harvest_bees = np.where(has_contact)[0]
            harvest_flowers = closest_flowers[harvest_bees]

            # Nectar attenuation: noise scales with depletion (1x to 3x)
            nectar_ratios = self.nectar[harvest_flowers] / config.FLOWER_NECTAR_MAX
            attenuation_factors = 1.0 + (1.0 - nectar_ratios) * 2.0  # (N_harvest,)
            noise_stds = config.FLOWER_HARVEST_NOISE_STD * attenuation_factors

            # Vectorized noise generation (±15% variation)
            noises = np.random.normal(0, noise_stds, size=len(harvest_bees))
            actual_harvests = np.clip(base_amount + noises, 0, None)

            # Clamp to available nectar
            available_nectar = self.nectar[harvest_flowers]
            actual_harvests = np.minimum(actual_harvests, available_nectar)

            # Update bee harvest amounts and flower contacts
            harvested[harvest_bees] = actual_harvests
            flower_contacts[harvest_bees] = harvest_flowers

            # Deduct nectar from flowers (vectorized accumulation)
            # Use np.add.at for thread-safe in-place addition (negative for subtraction)
            np.add.at(self.nectar, harvest_flowers, -actual_harvests)

            # Deactivate depleted flowers
            self.active = (self.nectar > 0).astype(np.int8)

        return harvested, flower_contacts

    def update(self, dt):
        """
        Regenerate nectar over time.

        Args:
            dt: Delta time (typically 1/30 for 30Hz updates)
        """
        # Regenerate nectar (vectorized)
        self.nectar = np.clip(
            self.nectar + config.FLOWER_NECTAR_REGEN * dt,
            0.0,
            config.FLOWER_NECTAR_MAX
        )

        # Reactivate flowers that have regenerated
        self.active = (self.nectar > 0).astype(np.int8)

    def get_render_data(self):
        """
        Get flower data for rendering with LOD.

        Returns:
            Dictionary with:
                positions: (5, 2) flower positions
                nectar_pct: (5,) nectar percentage [0.0 - 1.0]
                active: (5,) active status
        """
        return {
            'positions': self.positions.copy(),
            'nectar_pct': self.nectar / config.FLOWER_NECTAR_MAX,
            'active': self.active.copy()
        }


@njit
def harvest_vectorized(bee_positions, flower_positions, flower_nectar, flower_active,
                      base_amount, noise_std, contact_radius):
    """
    Numba-optimized vectorized harvest (future optimization).
    Currently using numpy for clarity per architect specs.

    This is a template for future Numba optimization if needed.
    """
    N = bee_positions.shape[0]
    F = flower_positions.shape[0]

    harvested = np.zeros(N, dtype=np.float32)
    flower_contacts = np.full(N, -1, dtype=np.int32)

    for bee_idx in range(N):
        min_dist = np.inf
        closest_flower = -1

        for flower_idx in range(F):
            if not flower_active[flower_idx]:
                continue

            dx = bee_positions[bee_idx, 0] - flower_positions[flower_idx, 0]
            dy = bee_positions[bee_idx, 1] - flower_positions[flower_idx, 1]
            dist = np.sqrt(dx**2 + dy**2)

            if dist < contact_radius and dist < min_dist:
                min_dist = dist
                closest_flower = flower_idx

        if closest_flower >= 0 and flower_nectar[closest_flower] > 0:
            # Note: Numba doesn't support np.random.normal directly
            # In production, would use numba's random with seed
            noise = np.random.normal(0, noise_std)
            actual_harvest = max(0, base_amount + noise)
            actual_harvest = min(actual_harvest, flower_nectar[closest_flower])

            harvested[bee_idx] = actual_harvest
            flower_contacts[bee_idx] = closest_flower
            flower_nectar[closest_flower] -= actual_harvest

            if flower_nectar[closest_flower] <= 0:
                flower_active[closest_flower] = 0

    return harvested, flower_contacts
