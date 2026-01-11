"""
PHASE 4: Pheromone System (The Garden)
128x128 pheromone grid with exponential decay and Sobel gradient field
"""

import numpy as np
from numba import njit
import config


class PheromoneSystem:
    """
    Manages dual-channel pheromone grids with gradient-based steering.

    PHASE 12.0: Two-channel information flow:
        - Resource grid (Forager trails): Stable, slow decay
        - Exploration grid (Scout markers): Volatile, fast decay

    Data Structure:
        resource_grid: (128, 128) float32 - stable food-to-hive trails
        exploration_grid: (128, 128) float32 - volatile territory markers
        resource_gradient: (128, 128, 2) float32 - cached [dx, dy] resource gradient
        exploration_gradient: (128, 128, 2) float32 - cached [dx, dy] exploration gradient
        world_to_grid_scale: float - conversion factor from world to grid coords
    """

    def __init__(self):
        """Initialize dual-channel pheromone grids and gradient fields."""
        # PHASE 12.0: Dual-channel grids
        self.resource_grid = np.zeros(
            (config.PHEROMONE_GRID_SIZE, config.PHEROMONE_GRID_SIZE),
            dtype=np.float32
        )
        self.exploration_grid = np.zeros(
            (config.PHEROMONE_GRID_SIZE, config.PHEROMONE_GRID_SIZE),
            dtype=np.float32
        )

        # Gradient fields for each channel
        self.resource_gradient = np.zeros(
            (config.PHEROMONE_GRID_SIZE, config.PHEROMONE_GRID_SIZE, 2),
            dtype=np.float32
        )
        self.exploration_gradient = np.zeros(
            (config.PHEROMONE_GRID_SIZE, config.PHEROMONE_GRID_SIZE, 2),
            dtype=np.float32
        )

        # Legacy compatibility: grid points to resource_grid
        self.grid = self.resource_grid
        self.gradient_field = self.resource_gradient

        # Precompute world-to-grid conversion
        self.world_to_grid_scale = config.PHEROMONE_GRID_SIZE / config.WORLD_WIDTH

        # PHASE 12.0: Frame counter for alternating updates (optimization)
        self.frame_counter = 0

    def deposit_pulse(self, bee_positions, mask=None):
        """
        LEGACY: Deposit to resource grid (backward compatibility).

        Args:
            bee_positions: (N, 2) array of bee positions in world space
            mask: (N,) boolean array - only deposit for True entries (optional)
        """
        self.deposit_resource(bee_positions, mask)

    def deposit_resource(self, bee_positions, mask=None, amplitude=None):
        """
        PHASE 12.0: Deposit pheromones to resource grid (Forager trails).

        Args:
            bee_positions: (N, 2) array of bee positions in world space
            mask: (N,) boolean array - only deposit for True entries (optional)
            amplitude: Pulse strength (default: FORAGER_RESOURCE_AMPLITUDE)
        """
        if amplitude is None:
            amplitude = config.FORAGER_RESOURCE_AMPLITUDE

        if mask is None:
            mask = np.ones(len(bee_positions), dtype=bool)

        # Convert world positions to grid indices
        grid_x = (bee_positions[:, 0] * self.world_to_grid_scale).astype(np.int32)
        grid_y = (bee_positions[:, 1] * self.world_to_grid_scale).astype(np.int32)

        # Clamp to grid bounds
        grid_x = np.clip(grid_x, 0, config.PHEROMONE_GRID_SIZE - 1)
        grid_y = np.clip(grid_y, 0, config.PHEROMONE_GRID_SIZE - 1)

        # Deposit pulses (vectorized accumulation)
        masked_x = grid_x[mask]
        masked_y = grid_y[mask]

        # Use np.add.at for atomic accumulation
        np.add.at(
            self.resource_grid,
            (masked_y, masked_x),  # Note: grid is [y, x] for image convention
            amplitude
        )

    def deposit_exploration(self, bee_positions, mask=None, amplitude=None):
        """
        PHASE 12.0: Deposit pheromones to exploration grid (Scout markers).

        Args:
            bee_positions: (N, 2) array of bee positions in world space
            mask: (N,) boolean array - only deposit for True entries (optional)
            amplitude: Pulse strength (default: SCOUT_EXPLORATION_AMPLITUDE)
        """
        if amplitude is None:
            amplitude = config.SCOUT_EXPLORATION_AMPLITUDE

        if mask is None:
            mask = np.ones(len(bee_positions), dtype=bool)

        # Convert world positions to grid indices
        grid_x = (bee_positions[:, 0] * self.world_to_grid_scale).astype(np.int32)
        grid_y = (bee_positions[:, 1] * self.world_to_grid_scale).astype(np.int32)

        # Clamp to grid bounds
        grid_x = np.clip(grid_x, 0, config.PHEROMONE_GRID_SIZE - 1)
        grid_y = np.clip(grid_y, 0, config.PHEROMONE_GRID_SIZE - 1)

        # Deposit pulses (vectorized accumulation)
        masked_x = grid_x[mask]
        masked_y = grid_y[mask]

        # Use np.add.at for atomic accumulation
        np.add.at(
            self.exploration_grid,
            (masked_y, masked_x),  # Note: grid is [y, x] for image convention
            amplitude
        )

    def update(self, dt=1.0):
        """
        PHASE 12.0: Update dual-channel pheromone grids with separate decay rates.
        OPTIMIZATION: Alternating updates to halve computational cost (0.5ms saved per frame).

        Args:
            dt: Delta time (typically 1.0 for 30Hz fixed updates)
        """
        # Alternate between grids to halve blur+gradient cost
        if self.frame_counter % 2 == 0:
            # Even frames: Update resource grid (Forager trails)
            self.resource_grid *= config.RESOURCE_DECAY_FACTOR
            self.resource_grid = gaussian_blur_3x3_njit(self.resource_grid)
            self.resource_gradient = sobel_gradient_njit(self.resource_grid)
        else:
            # Odd frames: Update exploration grid (Scout markers)
            self.exploration_grid *= config.EXPLORATION_DECAY_FACTOR
            self.exploration_grid = gaussian_blur_3x3_njit(self.exploration_grid)
            self.exploration_gradient = sobel_gradient_njit(self.exploration_grid)

        self.frame_counter += 1

        # Legacy compatibility: grid points to resource_grid
        self.gradient_field = self.resource_gradient

    def sample_gradient(self, bee_positions):
        """
        Sample gradient vectors for bee steering.

        Args:
            bee_positions: (N, 2) array of bee positions in world space

        Returns:
            gradients: (N, 2) array of gradient vectors [dx, dy]
                       Clamped to PHEROMONE_GRADIENT_CLAMP magnitude
        """
        N = len(bee_positions)
        gradients = np.zeros((N, 2), dtype=np.float32)

        # Convert to grid coordinates
        grid_x = (bee_positions[:, 0] * self.world_to_grid_scale).astype(np.int32)
        grid_y = (bee_positions[:, 1] * self.world_to_grid_scale).astype(np.int32)

        # Clamp to valid grid indices
        grid_x = np.clip(grid_x, 0, config.PHEROMONE_GRID_SIZE - 1)
        grid_y = np.clip(grid_y, 0, config.PHEROMONE_GRID_SIZE - 1)

        # Sample from cached gradient field
        gradients[:, 0] = self.gradient_field[grid_y, grid_x, 0]
        gradients[:, 1] = self.gradient_field[grid_y, grid_x, 1]

        # Clamp gradient magnitude (persuasion, not command)
        magnitudes = np.sqrt(gradients[:, 0]**2 + gradients[:, 1]**2)
        too_large = magnitudes > config.PHEROMONE_GRADIENT_CLAMP

        if np.any(too_large):
            scale = config.PHEROMONE_GRADIENT_CLAMP / magnitudes[too_large]
            gradients[too_large, 0] *= scale
            gradients[too_large, 1] *= scale

        return gradients

    def sample_resource_gradient(self, bee_positions):
        """
        PHASE 12.0: Sample resource gradient (for Foragers - attraction to peaks).

        Args:
            bee_positions: (N, 2) array of bee positions in world space

        Returns:
            gradients: (N, 2) array of gradient vectors [dx, dy]
        """
        N = len(bee_positions)
        gradients = np.zeros((N, 2), dtype=np.float32)

        # Convert to grid coordinates
        grid_x = (bee_positions[:, 0] * self.world_to_grid_scale).astype(np.int32)
        grid_y = (bee_positions[:, 1] * self.world_to_grid_scale).astype(np.int32)

        # Clamp to valid grid indices
        grid_x = np.clip(grid_x, 0, config.PHEROMONE_GRID_SIZE - 1)
        grid_y = np.clip(grid_y, 0, config.PHEROMONE_GRID_SIZE - 1)

        # Sample from resource gradient field
        gradients[:, 0] = self.resource_gradient[grid_y, grid_x, 0]
        gradients[:, 1] = self.resource_gradient[grid_y, grid_x, 1]

        # Clamp gradient magnitude
        magnitudes = np.sqrt(gradients[:, 0]**2 + gradients[:, 1]**2)
        too_large = magnitudes > config.PHEROMONE_GRADIENT_CLAMP

        if np.any(too_large):
            scale = config.PHEROMONE_GRADIENT_CLAMP / magnitudes[too_large]
            gradients[too_large, 0] *= scale
            gradients[too_large, 1] *= scale

        return gradients

    def sample_exploration_gradient(self, bee_positions, invert=True):
        """
        PHASE 12.0: Sample exploration gradient (for Scouts - repulsion from peaks).

        Args:
            bee_positions: (N, 2) array of bee positions in world space
            invert: If True, invert gradient (scouts seek voids, not peaks)

        Returns:
            gradients: (N, 2) array of gradient vectors [dx, dy]
        """
        N = len(bee_positions)
        gradients = np.zeros((N, 2), dtype=np.float32)

        # Convert to grid coordinates
        grid_x = (bee_positions[:, 0] * self.world_to_grid_scale).astype(np.int32)
        grid_y = (bee_positions[:, 1] * self.world_to_grid_scale).astype(np.int32)

        # Clamp to valid grid indices
        grid_x = np.clip(grid_x, 0, config.PHEROMONE_GRID_SIZE - 1)
        grid_y = np.clip(grid_y, 0, config.PHEROMONE_GRID_SIZE - 1)

        # Sample from exploration gradient field
        gradients[:, 0] = self.exploration_gradient[grid_y, grid_x, 0]
        gradients[:, 1] = self.exploration_gradient[grid_y, grid_x, 1]

        # Invert for scouts (seek LOW concentration areas = exploratory drive)
        if invert:
            gradients *= -1.0

        # Clamp gradient magnitude
        magnitudes = np.sqrt(gradients[:, 0]**2 + gradients[:, 1]**2)
        too_large = magnitudes > config.PHEROMONE_GRADIENT_CLAMP

        if np.any(too_large):
            scale = config.PHEROMONE_GRADIENT_CLAMP / magnitudes[too_large]
            gradients[too_large, 0] *= scale
            gradients[too_large, 1] *= scale

        return gradients

    def get_heatmap(self):
        """
        Get pheromone grid for debug visualization.

        Returns:
            grid: (128, 128) float32 array (copy for safety)
        """
        return self.grid.copy()


@njit
def gaussian_blur_3x3_njit(grid):
    """
    Apply 3x3 Gaussian blur with reflecting boundary conditions.

    Kernel:
        1  2  1
        2  4  2  * (1/16)
        1  2  1

    Args:
        grid: (H, W) float32 array

    Returns:
        blurred: (H, W) float32 array
    """
    H, W = grid.shape
    blurred = np.zeros_like(grid)

    # Gaussian kernel weights
    kernel = np.array([
        [1.0, 2.0, 1.0],
        [2.0, 4.0, 2.0],
        [1.0, 2.0, 1.0]
    ], dtype=np.float32) / 16.0

    for y in range(H):
        for x in range(W):
            acc = 0.0

            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    # Reflecting boundary conditions
                    ny = y + ky
                    nx = x + kx

                    if ny < 0:
                        ny = -ny
                    elif ny >= H:
                        ny = 2 * H - ny - 2

                    if nx < 0:
                        nx = -nx
                    elif nx >= W:
                        nx = 2 * W - nx - 2

                    # Clamp to valid range (safety)
                    ny = max(0, min(H - 1, ny))
                    nx = max(0, min(W - 1, nx))

                    acc += grid[ny, nx] * kernel[ky + 1, kx + 1]

            blurred[y, x] = acc

    return blurred


@njit
def sobel_gradient_njit(grid):
    """
    Compute Sobel gradient field for steering.

    Sobel operators:
        Gx:        Gy:
        -1  0  1   -1 -2 -1
        -2  0  2    0  0  0
        -1  0  1    1  2  1

    Args:
        grid: (H, W) float32 array

    Returns:
        gradient: (H, W, 2) float32 array with [dx, dy] at each cell
    """
    H, W = grid.shape
    gradient = np.zeros((H, W, 2), dtype=np.float32)

    # Sobel kernels
    sobel_x = np.array([
        [-1.0, 0.0, 1.0],
        [-2.0, 0.0, 2.0],
        [-1.0, 0.0, 1.0]
    ], dtype=np.float32)

    sobel_y = np.array([
        [-1.0, -2.0, -1.0],
        [ 0.0,  0.0,  0.0],
        [ 1.0,  2.0,  1.0]
    ], dtype=np.float32)

    for y in range(H):
        for x in range(W):
            gx = 0.0
            gy = 0.0

            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    # Reflecting boundary conditions
                    ny = y + ky
                    nx = x + kx

                    if ny < 0:
                        ny = -ny
                    elif ny >= H:
                        ny = 2 * H - ny - 2

                    if nx < 0:
                        nx = -nx
                    elif nx >= W:
                        nx = 2 * W - nx - 2

                    # Clamp to valid range (safety)
                    ny = max(0, min(H - 1, ny))
                    nx = max(0, min(W - 1, nx))

                    val = grid[ny, nx]
                    gx += val * sobel_x[ky + 1, kx + 1]
                    gy += val * sobel_y[ky + 1, kx + 1]

            gradient[y, x, 0] = gx
            gradient[y, x, 1] = gy

    return gradient
