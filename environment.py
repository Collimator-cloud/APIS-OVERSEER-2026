"""
APIS-OVERSEER Environment
Spatial grid, collision mask, food sources, hive structure
"""

import numpy as np
import pygame
from config import *

# ============================================================================
# WORLD ENVIRONMENT
# ============================================================================

class Environment:
    """
    World environment with hive, food sources, and spatial structures.
    """

    def __init__(self):
        """Initialize environment with hive and food sources."""
        # Hive center (already defined in config)
        self.hive_center = np.array([HIVE_CENTER_X, HIVE_CENTER_Y], dtype=np.float32)

        # Food sources (scattered around world)
        self.food_sources = self._generate_food_sources()

        # Collision mask (precomputed in config)
        self.collision_mask = COLLISION_MASK

        # Spatial grid (initialized empty, rebuilt each frame)
        self.spatial_grid = None

        # Tree hollow entrance assets (loaded lazily)
        self._tree_hollow_loaded = False
        self._bark_texture = None
        self._hollow_mask = None
        self._glow_surface = None
        self._glow_cache = {}  # HOTFIX: Pre-modulated glow surfaces by opacity level (64 levels)
        self._glow_timer = 0.0  # For flicker animation
        
        # HOTFIX: Pre-compute sin values for flicker (avoid math.sin in hot path)
        import math
        self._sin_lookup = [math.sin(i * 0.5) for i in range(1000)]

    def _generate_food_sources(self, num_sources=5):
        """
        Generate random food source positions.

        Args:
            num_sources: Number of food sources to create

        Returns:
            (N, 2) array of food positions
        """
        # Avoid placing food too close to hive
        food_sources = []

        for _ in range(num_sources):
            while True:
                x = np.random.uniform(100, WORLD_WIDTH - 100)
                y = np.random.uniform(100, WORLD_HEIGHT - 100)

                # Check distance from hive
                dist = np.sqrt((x - HIVE_CENTER_X)**2 + (y - HIVE_CENTER_Y)**2)
                if dist > HIVE_ENTRANCE_RADIUS * 5:  # At least 5× entrance radius away
                    food_sources.append([x, y])
                    break

        return np.array(food_sources, dtype=np.float32)

    def rebuild_spatial_grid(self, positions):
        """
        Rebuild spatial grid from bee positions.

        Args:
            positions: (N, 2) array of bee positions

        Returns:
            List of lists (grid cells containing bee indices)
        """
        from biology import rebuild_spatial_grid
        self.spatial_grid = rebuild_spatial_grid(positions, GRID_CELLS)
        return self.spatial_grid

    def get_collision_alpha(self, x, y):
        """
        Get collision mask alpha at world position (for Nebula fade).

        Args:
            x, y: World coordinates

        Returns:
            Alpha value [0, 1]
        """
        mask_x = int(x / WORLD_WIDTH * COLLISION_MASK_RES)
        mask_y = int(y / WORLD_HEIGHT * COLLISION_MASK_RES)

        mask_x = np.clip(mask_x, 0, COLLISION_MASK_RES - 1)
        mask_y = np.clip(mask_y, 0, COLLISION_MASK_RES - 1)

        return self.collision_mask[mask_y, mask_x]

    def render_hive(self, screen, camera_x, camera_y, screen_width, screen_height, coherence=0.0, dt=0.016):
        """
        Render hive structure with tree hollow entrance.

        Args:
            screen: Pygame surface
            camera_x, camera_y: Camera position
            screen_width, screen_height: Screen dimensions
            coherence: Swarm coherence index [0, 1] for glow flicker
            dt: Delta time for flicker animation
        """
        # Transform to screen space
        screen_x = self.hive_center[0] - camera_x + screen_width / 2
        screen_y = self.hive_center[1] - camera_y + screen_height / 2

        # Load tree hollow assets if needed
        if not self._tree_hollow_loaded:
            self._load_tree_hollow_assets()

        # Update glow flicker timer
        self._glow_timer += dt

        # HOTFIX: Batch all tree hollow layers in ONE scissor block (minimize OpenGL state changes)
        if self._bark_texture and self._hollow_mask and self._glow_surface:
            # Single scissor test for all layers
            scissor_width = int(screen_width * 0.25)
            clip_rect = pygame.Rect(0, 0, scissor_width, screen_height)
            original_clip = screen.get_clip()
            screen.set_clip(clip_rect)
            
            # Layer 1: Bark (background)
            bark_rect = self._bark_texture.get_rect(center=(int(screen_x), int(screen_y)))
            screen.blit(self._bark_texture, bark_rect)
            
            # Layer 2: Hollow mask (dark interior)
            hollow_rect = self._hollow_mask.get_rect(center=(int(screen_x), int(screen_y)))
            screen.blit(self._hollow_mask, hollow_rect, special_flags=pygame.BLEND_RGBA_MULT)
            
            # Layer 3: Glow (use pre-cached modulated surface)
            # Flicker: opacity = 0.25 + 0.05*sin(time*0.5)*coherence
            time_idx = int(self._glow_timer) % 1000
            flicker = self._sin_lookup[time_idx] * 0.05 * coherence
            opacity = max(0.0, min(1.0, 0.25 + flicker))
            
            # Get cached glow surface (or create if new opacity level)
            opacity_key = int(opacity * 63)  # 64 levels (0-63)
            if opacity_key not in self._glow_cache:
                glow_cached = self._glow_surface.copy()
                glow_cached.set_alpha(int(opacity_key * 4))  # Map to 0-252
                self._glow_cache[opacity_key] = glow_cached
            
            glow_rect = self._glow_cache[opacity_key].get_rect(center=(int(screen_x), int(screen_y)))
            screen.blit(self._glow_cache[opacity_key], glow_rect)
            
            screen.set_clip(original_clip)

        # Fallback: Original hive rendering (always visible, provides compatibility)
        # Draw hive entrance (dark circle)
        pygame.draw.circle(
            screen,
            (80, 60, 40),
            (int(screen_x), int(screen_y)),
            HIVE_ENTRANCE_RADIUS,
            0  # Filled
        )

        # Draw entrance border (brighter)
        pygame.draw.circle(
            screen,
            (120, 100, 60),
            (int(screen_x), int(screen_y)),
            HIVE_ENTRANCE_RADIUS,
            2  # Outline
        )

        # Draw inner entrance (darker, for depth)
        pygame.draw.circle(
            screen,
            (40, 30, 20),
            (int(screen_x), int(screen_y)),
            int(HIVE_ENTRANCE_RADIUS * 0.6),
            0
        )

    def _load_tree_hollow_assets(self):
        """Load tree hollow PNG assets with GPU fallback compatibility."""
        import os

        asset_path = 'assets/environment/tree_hollow/'
        
        try:
            if os.path.exists(asset_path + 'bark_texture.png'):
                self._bark_texture = pygame.image.load(asset_path + 'bark_texture.png')
                self._bark_texture = pygame.transform.smoothscale(self._bark_texture, (512, 512))
                self._bark_texture = self._bark_texture.convert_alpha()
            
            if os.path.exists(asset_path + 'hollow_mask.png'):
                self._hollow_mask = pygame.image.load(asset_path + 'hollow_mask.png')
                self._hollow_mask = pygame.transform.smoothscale(self._hollow_mask, (512, 512))
                self._hollow_mask = self._hollow_mask.convert_alpha()
            
            if os.path.exists(asset_path + 'glow_surface.png'):
                # HOTFIX: Reduce glow to 256×256 (4× memory reduction, faster blit)
                glow_raw = pygame.image.load(asset_path + 'glow_surface.png')
                self._glow_surface = pygame.transform.smoothscale(glow_raw, (256, 256))
                self._glow_surface = self._glow_surface.convert_alpha()
                print(f"   [INFO] Glow texture downsampled to 256x256 for performance")

            self._tree_hollow_loaded = True
            print(f"[OK] Tree hollow assets loaded from {asset_path}")
        except Exception as e:
            print(f"[WARN] Tree hollow asset loading failed: {e}")
            print("   Falling back to original hive rendering")
            self._tree_hollow_loaded = True  # Mark as attempted to avoid retry loop

    def render_food_sources(self, screen, camera_x, camera_y, screen_width, screen_height):
        """
        PHASE 14.0-REVISED: Render food sources as vibrant Meadow Clusters.

        Replaces large green orbs with small filled circles (radius 8px) using
        primary colors (Yellow/Red/Purple) to create organic meadow texture.

        Args:
            screen: Pygame surface
            camera_x, camera_y: Camera position
            screen_width, screen_height: Screen dimensions
        """
        # Meadow patch colors (vibrant primaries - NO PINK)
        meadow_colors = [
            (255, 255, 50),   # Bright Yellow (pollen)
            (255, 80, 80),    # Warm Red (berries)
            (180, 80, 255),   # Deep Violet (flowers) - distinct from pink
            (255, 200, 60),   # Gold (nectar)
        ]

        for food in self.food_sources:
            screen_x = food[0] - camera_x + screen_width / 2
            screen_y = food[1] - camera_y + screen_height / 2

            # Skip if off-screen
            if not (0 <= screen_x < screen_width and 0 <= screen_y < screen_height):
                continue

            # PHASE 14.0-REVISED: Meadow Cluster (small filled circle, random color)
            color = meadow_colors[np.random.randint(0, len(meadow_colors))]
            pygame.draw.circle(
                screen,
                color,
                (int(screen_x), int(screen_y)),
                8,  # 8px radius
                0   # Filled
            )

    def render_collision_mask_debug(self, screen, camera_x, camera_y, screen_width, screen_height):
        """
        Debug: Render collision mask as overlay.

        Args:
            screen: Pygame surface
            camera_x, camera_y: Camera position
            screen_width, screen_height: Screen dimensions
        """
        # Downsample collision mask for performance
        step = 20  # pixels per sample

        for world_y in range(0, WORLD_HEIGHT, step):
            for world_x in range(0, WORLD_WIDTH, step):
                alpha = self.get_collision_alpha(world_x, world_y)

                # Skip fully transparent
                if alpha > 0.95:
                    continue

                screen_x = world_x - camera_x + screen_width / 2
                screen_y = world_y - camera_y + screen_height / 2

                # Skip if off-screen
                if not (0 <= screen_x < screen_width and 0 <= screen_y < screen_height):
                    continue

                # Red = blocked, transparent = passable
                color = (255, 0, 0, int((1.0 - alpha) * 100))
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 3)


# ============================================================================
# SPATIAL QUERY HELPERS
# ============================================================================

def get_neighbors_in_radius(position, all_positions, radius):
    """
    Get all positions within radius (brute force, for validation).

    Args:
        position: (2,) array
        all_positions: (N, 2) array
        radius: Float

    Returns:
        List of indices within radius
    """
    dists = np.linalg.norm(all_positions - position, axis=1)
    return np.where(dists < radius)[0]


def check_collision_circle(pos_a, radius_a, pos_b, radius_b):
    """
    Check circle-circle collision.

    Args:
        pos_a: (2,) array
        radius_a: Float
        pos_b: (2,) array
        radius_b: Float

    Returns:
        Boolean (True if colliding)
    """
    dist = np.linalg.norm(pos_a - pos_b)
    return dist < (radius_a + radius_b)


def world_to_grid_cell(position, grid_cells=GRID_CELLS):
    """
    Convert world position to grid cell indices.

    Args:
        position: (2,) array [x, y]
        grid_cells: Number of grid cells per axis

    Returns:
        (cell_x, cell_y) tuple
    """
    cell_size = WORLD_WIDTH / grid_cells

    cell_x = int(position[0] / cell_size)
    cell_y = int(position[1] / cell_size)

    cell_x = np.clip(cell_x, 0, grid_cells - 1)
    cell_y = np.clip(cell_y, 0, grid_cells - 1)

    return cell_x, cell_y


def grid_cell_to_world(cell_x, cell_y, grid_cells=GRID_CELLS):
    """
    Convert grid cell indices to world position (center of cell).

    Args:
        cell_x, cell_y: Grid cell indices
        grid_cells: Number of grid cells per axis

    Returns:
        (x, y) tuple (world coordinates)
    """
    cell_size = WORLD_WIDTH / grid_cells

    x = (cell_x + 0.5) * cell_size
    y = (cell_y + 0.5) * cell_size

    return x, y


# ============================================================================
# TEMPERATURE FIELD (Optional enhancement)
# ============================================================================

class TemperatureField:
    """
    Optional: Dynamic temperature field for warmth seeking.
    Hive radiates heat, edges are cold.
    """

    def __init__(self, resolution=64):
        """
        Initialize temperature field.

        Args:
            resolution: Field resolution (64×64)
        """
        self.resolution = resolution
        self.field = np.zeros((resolution, resolution), dtype=np.float32)
        self._initialize_field()

    def _initialize_field(self):
        """Initialize temperature gradient (hot at hive, cold at edges)."""
        y, x = np.ogrid[:self.resolution, :self.resolution]

        # Hive position in field space
        hive_x = HIVE_CENTER_X / WORLD_WIDTH * self.resolution
        hive_y = HIVE_CENTER_Y / WORLD_HEIGHT * self.resolution

        # Distance from hive
        dist = np.sqrt((x - hive_x)**2 + (y - hive_y)**2)

        # Temperature falls off with distance (sigmoid for smooth gradient)
        max_dist = self.resolution * 0.7
        self.field = 1.0 / (1.0 + (dist / max_dist)**2)

    def get_temperature(self, x, y):
        """
        Sample temperature at world position.

        Args:
            x, y: World coordinates

        Returns:
            Temperature [0, 1]
        """
        field_x = int(x / WORLD_WIDTH * self.resolution)
        field_y = int(y / WORLD_HEIGHT * self.resolution)

        field_x = np.clip(field_x, 0, self.resolution - 1)
        field_y = np.clip(field_y, 0, self.resolution - 1)

        return self.field[field_y, field_x]

    def update(self, dt):
        """
        Optional: Update temperature field (e.g., cooling over time).

        Args:
            dt: Delta time in seconds
        """
        # Could add dynamic cooling, but for now static field is fine
        pass


# ============================================================================
# ZONE SYSTEM (Optional)
# ============================================================================

class Zone:
    """
    Spatial zone with properties (e.g., Zone 3 = choke point near hive).
    """

    def __init__(self, center, radius, zone_type='neutral'):
        """
        Initialize zone.

        Args:
            center: (2,) array [x, y]
            radius: Float
            zone_type: String ('neutral', 'choke', 'food', etc.)
        """
        self.center = center
        self.radius = radius
        self.zone_type = zone_type

    def contains(self, position):
        """
        Check if position is inside zone.

        Args:
            position: (2,) array [x, y]

        Returns:
            Boolean
        """
        dist = np.linalg.norm(position - self.center)
        return dist < self.radius

    def get_distance(self, position):
        """
        Get distance from zone center.

        Args:
            position: (2,) array [x, y]

        Returns:
            Float (distance)
        """
        return np.linalg.norm(position - self.center)


# Zone 3 (choke point) example
ZONE_CHOKE = Zone(
    center=np.array([HIVE_CENTER_X, HIVE_CENTER_Y], dtype=np.float32),
    radius=HIVE_ENTRANCE_RADIUS * 1.5,
    zone_type='choke'
)
