"""
PHASE 4: Pheromone System (The Garden)
128x128 pheromone grid with exponential decay and Sobel gradient field
"""

import numpy as np
from numba import njit
import config


class PheromoneSystem:
    """
    Manages pheromone home trail grid with gradient-based steering.

    Data Structure:
        grid: (128, 128) float32 - pheromone concentration
        gradient_field: (128, 128, 2) float32 - cached [dx, dy] Sobel gradient
        world_to_grid_scale: float - conversion factor from world to grid coords
    """

    def __init__(self):
        """Initialize pheromone grid and gradient field."""
        self.grid = np.zeros(
            (config.PHEROMONE_GRID_SIZE, config.PHEROMONE_GRID_SIZE),
            dtype=np.float32
        )
        self.gradient_field = np.zeros(
            (config.PHEROMONE_GRID_SIZE, config.PHEROMONE_GRID_SIZE, 2),
            dtype=np.float32
        )

        # Precompute world-to-grid conversion
        self.world_to_grid_scale = config.PHEROMONE_GRID_SIZE / config.WORLD_WIDTH

    def deposit_pulse(self, bee_positions, mask=None):
        """
        Deposit constant pheromone pulses at bee positions.

        Args:
            bee_positions: (N, 2) array of bee positions in world space
            mask: (N,) boolean array - only deposit for True entries (optional)
        """
        if mask is None:
            mask = np.ones(len(bee_positions), dtype=bool)

        # Convert world positions to grid indices
        grid_x = (bee_positions[:, 0] * self.world_to_grid_scale).astype(np.int32)
        grid_y = (bee_positions[:, 1] * self.world_to_grid_scale).astype(np.int32)

        # Clamp to grid bounds
        grid_x = np.clip(grid_x, 0, config.PHEROMONE_GRID_SIZE - 1)
        grid_y = np.clip(grid_y, 0, config.PHEROMONE_GRID_SIZE - 1)

        # Deposit pulses (vectorized accumulation)
        # Only deposit for masked bees
        masked_x = grid_x[mask]
        masked_y = grid_y[mask]

        # Use np.add.at for atomic accumulation
        np.add.at(
            self.grid,
            (masked_y, masked_x),  # Note: grid is [y, x] for image convention
            config.PHEROMONE_PULSE_AMPLITUDE
        )

    def update(self, dt=1.0):
        """
        Update pheromone grid: exponential decay + Gaussian blur + Sobel gradient.

        Args:
            dt: Delta time (typically 1.0 for 30Hz fixed updates)
        """
        # 1. Exponential decay (vectorized)
        self.grid *= config.PHEROMONE_DECAY_FACTOR

        # 2. Gaussian blur (3x3 kernel) for diffusion
        self.grid = gaussian_blur_3x3_njit(self.grid)

        # 3. Compute Sobel gradient field (cached for steering queries)
        self.gradient_field = sobel_gradient_njit(self.grid)

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
