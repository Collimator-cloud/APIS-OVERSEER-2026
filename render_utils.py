"""
APIS-OVERSEER Rendering Utilities
Batched Surface.blits(), texture atlas, GPU-ready instancing
Target: 60 FPS with 16.6 ms frame budget
"""

import numpy as np
import pygame
from config import *

# ============================================================================
# TEXTURE ATLAS
# ============================================================================

class TextureAtlas:
    """Single 256×256 texture atlas for all bee states/tiers."""

    def __init__(self):
        """Create texture atlas with bee sprites."""
        self.atlas = pygame.Surface((TEXTURE_ATLAS_SIZE, TEXTURE_ATLAS_SIZE), pygame.SRCALPHA)
        self.atlas.fill((0, 0, 0, 0))

        # Define sprite regions (x, y, w, h) in atlas
        self.sprites = {
            'vanguard_normal': (0, 0, BEE_SPRITE_SIZE, BEE_SPRITE_SIZE),
            'vanguard_low_health': (8, 0, BEE_SPRITE_SIZE, BEE_SPRITE_SIZE),
            'legion_normal': (16, 0, BEE_SPRITE_SIZE, BEE_SPRITE_SIZE),
            'legion_low_health': (24, 0, BEE_SPRITE_SIZE, BEE_SPRITE_SIZE),
            'nebula_particle': (32, 0, 4, 4),  # Smaller for distant particles
        }

        self._render_sprites()

    def _render_sprites(self):
        """Render bee sprites into atlas (simple colored circles for now)."""
        # Vanguard normal: bright yellow
        pygame.draw.circle(
            self.atlas,
            (255, 220, 0),
            (4, 4),
            3
        )

        # Vanguard low health: orange with red tint
        pygame.draw.circle(
            self.atlas,
            (255, 150, 50),
            (12, 4),
            3
        )

        # Legion normal: slightly dimmer yellow
        pygame.draw.circle(
            self.atlas,
            (220, 200, 0),
            (20, 4),
            3
        )

        # Legion low health: orange
        pygame.draw.circle(
            self.atlas,
            (220, 120, 30),
            (28, 4),
            3
        )

        # Nebula particle: very dim yellow
        pygame.draw.circle(
            self.atlas,
            (180, 180, 100),
            (34, 2),
            1
        )

    def get_sprite_rect(self, sprite_name):
        """Get texture coordinates for sprite."""
        return self.sprites.get(sprite_name, self.sprites['vanguard_normal'])


# ============================================================================
# BATCHED RENDERING
# ============================================================================

class BeeRenderer:
    """
    Batched renderer for all three tiers.
    Uses Surface.blits() for maximum performance.
    """

    def __init__(self, screen_width, screen_height):
        """Initialize renderer with screen dimensions."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.atlas = TextureAtlas()

        # Cache subsurfaces for each sprite type
        self.sprite_cache = {}
        for name, rect in self.atlas.sprites.items():
            self.sprite_cache[name] = self.atlas.atlas.subsurface(rect)

    def render_frame(self, screen, render_data, camera_x, camera_y, show_pheromone=False, pheromone_opacity=0.2):
        """
        Render complete frame with all tiers.
        PHASE 4: Added pheromone heatmap and flower rendering.

        Args:
            screen: Pygame surface
            render_data: Dict from simulation.get_render_data()
            camera_x, camera_y: Camera position for viewport transform
            show_pheromone: Toggle pheromone heatmap overlay
            pheromone_opacity: Opacity for pheromone heatmap (0.0-0.4)
        """
        # PHASE 12.0: Render dual-channel ghost-field (if enabled)
        if show_pheromone:
            if 'resource_grid' in render_data and 'exploration_grid' in render_data:
                self._render_ghost_field(screen, render_data['resource_grid'],
                                        render_data['exploration_grid'],
                                        camera_x, camera_y, pheromone_opacity)
            elif 'pheromone_heatmap' in render_data:
                # PHASE 4: Legacy single-channel fallback
                self._render_pheromone_heatmap(screen, render_data['pheromone_heatmap'],
                                              camera_x, camera_y, pheromone_opacity)

        # PHASE 4: Render flowers
        if 'flowers' in render_data:
            self._render_flowers(screen, render_data['flowers'], camera_x, camera_y)

        # Render in layer order: Ghost Bees -> Nebula -> Legion -> Vanguard
        # PHASE 13.0: Render ghost bees if present
        if 'ghost_bees' in render_data:
            self._render_ghost_bees(screen, render_data['ghost_bees'], camera_x, camera_y)

        self._render_nebula(screen, render_data['nebula'], camera_x, camera_y)
        self._render_legion(screen, render_data['legion'], camera_x, camera_y)
        self._render_vanguard(screen, render_data['vanguard'], camera_x, camera_y)

    def _render_vanguard(self, screen, vanguard, camera_x, camera_y):
        """
        Render Vanguard tier with batched blits.

        Args:
            screen: Pygame surface
            vanguard: (300, 15) array
            camera_x, camera_y: Camera position
        """
        # Build blit sequence: [(surface, (x, y)), ...]
        blit_sequence = []

        # Int32 view of flags for efficient bitwise checks (Phase 2B Step 2)
        flags = vanguard[:, V_STATE_FLAGS].view(np.int32)

        for i in range(len(vanguard)):
            # Skip dead bees
            if flags[i] & FLAG_DEAD:
                continue

            # World to screen transform
            world_x = vanguard[i, V_POS_X]
            world_y = vanguard[i, V_POS_Y]
            screen_x = world_x - camera_x + self.screen_width / 2
            screen_y = world_y - camera_y + self.screen_height / 2

            # Frustum culling
            if not (0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height):
                continue

            # Select sprite based on health
            health = vanguard[i, V_HEALTH]
            if health < 0.3:
                sprite = self.sprite_cache['vanguard_low_health']
            else:
                sprite = self.sprite_cache['vanguard_normal']

            # Apply vibration based on cohesion (illusion: low cohesion = erratic movement)
            cohesion = vanguard[i, V_COHESION]
            vibration = VIBRATION_BASE * (1.0 - cohesion)
            trail_phase = vanguard[i, V_TRAIL_PHASE]

            offset_x = np.sin(trail_phase) * vibration
            offset_y = np.cos(trail_phase * 1.3) * vibration

            final_x = int(screen_x + offset_x)
            final_y = int(screen_y + offset_y)

            blit_sequence.append((sprite, (final_x, final_y)))

        # Batch blit all vanguard bees
        if blit_sequence:
            screen.blits(blit_sequence, doreturn=False)

    def _render_legion(self, screen, legion, camera_x, camera_y):
        """
        Render Legion tier with batched blits (simplified).

        Args:
            screen: Pygame surface
            legion: (2000, 10) array - PHASE 2: expanded with state flags
            camera_x, camera_y: Camera position
        """
        blit_sequence = []

        # PHASE 2 FIX: Check FLAG_DEAD instead of health <= 0
        flags = legion[:, L_STATE_FLAGS].view(np.int32)

        for i in range(len(legion)):
            # Skip dead bees (PHASE 2: use state flags like Vanguard)
            if flags[i] & FLAG_DEAD:
                continue

            health = legion[i, L_HEALTH]

            world_x = legion[i, L_POS_X]
            world_y = legion[i, L_POS_Y]
            screen_x = world_x - camera_x + self.screen_width / 2
            screen_y = world_y - camera_y + self.screen_height / 2

            # Frustum culling
            if not (0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height):
                continue

            # Select sprite
            if health < 0.3:
                sprite = self.sprite_cache['legion_low_health']
            else:
                sprite = self.sprite_cache['legion_normal']

            blit_sequence.append((sprite, (int(screen_x), int(screen_y))))

        # Batch blit
        if blit_sequence:
            screen.blits(blit_sequence, doreturn=False)

    def _render_ghost_bees(self, screen, ghost_bees, camera_x, camera_y):
        """
        PHASE 14.0: Render Ghost Bees with distance-based color shading.

        Ghost bees provide visual mass (6K total agents) without computational cost.
        Rendering: Single-pixel dots with 3-step color lookup based on distance from hive.

        OPTIMIZATION: Use numpy indexing to batch-set pixels via PixelArray.

        Args:
            screen: Pygame surface
            ghost_bees: (4800, 4) array [x, y, vx, vy]
            camera_x, camera_y: Camera position
        """
        # Transform world to screen coordinates
        screen_x = ghost_bees[:, G_POS_X] - camera_x + self.screen_width / 2
        screen_y = ghost_bees[:, G_POS_Y] - camera_y + self.screen_height / 2

        # Frustum culling (only render visible ghosts)
        visible = (
            (screen_x >= 1) & (screen_x < self.screen_width - 1) &
            (screen_y >= 1) & (screen_y < self.screen_height - 1)
        )

        # Filter to visible ghosts
        visible_positions = ghost_bees[visible]
        screen_x_int = screen_x[visible].astype(int)
        screen_y_int = screen_y[visible].astype(int)

        # PHASE 14.0: Distance-based color shading (3-step lookup)
        # Calculate distance from hive center
        dx = visible_positions[:, G_POS_X] - HIVE_CENTER_X
        dy = visible_positions[:, G_POS_Y] - HIVE_CENTER_Y
        distances = np.sqrt(dx**2 + dy**2)

        # 3-step color classification (branchless via np.where)
        is_near = distances < GHOST_DISTANCE_THRESHOLD_1
        is_mid = (distances >= GHOST_DISTANCE_THRESHOLD_1) & (distances < GHOST_DISTANCE_THRESHOLD_2)
        is_far = distances >= GHOST_DISTANCE_THRESHOLD_2

        # Assign colors per ghost
        colors = np.zeros((len(visible_positions), 3), dtype=np.uint8)
        colors[is_near] = GHOST_COLOR_NEAR
        colors[is_mid] = GHOST_COLOR_MID
        colors[is_far] = GHOST_COLOR_FAR

        # Batch pixel drawing using PixelArray (lock surface once, write all pixels)
        try:
            pxarray = pygame.PixelArray(screen)

            # Set pixels in batch (per-color group for PixelArray compatibility)
            for color_rgb in [GHOST_COLOR_NEAR, GHOST_COLOR_MID, GHOST_COLOR_FAR]:
                mask = np.all(colors == color_rgb, axis=1)
                if np.any(mask):
                    x_coords = screen_x_int[mask]
                    y_coords = screen_y_int[mask]
                    mapped_color = screen.map_rgb(color_rgb)
                    pxarray[x_coords, y_coords] = mapped_color

            del pxarray  # Unlock surface
        except:
            # Fallback: skip ghost rendering if PixelArray fails
            pass

    def _render_nebula(self, screen, nebula_particles, camera_x, camera_y):
        """
        Render Nebula ephemeral particles with alpha masking.

        Args:
            screen: Pygame surface
            nebula_particles: (N, 5) array [x, y, vx, vy, alpha]
            camera_x, camera_y: Camera position
        """
        if len(nebula_particles) == 0:
            return

        blit_sequence = []
        sprite = self.sprite_cache['nebula_particle']

        for particle in nebula_particles:
            world_x = particle[0]
            world_y = particle[1]
            alpha = particle[4]

            screen_x = world_x - camera_x + self.screen_width / 2
            screen_y = world_y - camera_y + self.screen_height / 2

            # Frustum culling
            if not (0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height):
                continue

            # Apply alpha (create temp surface for each particle - not ideal but works)
            # In production, would use sprite sheets with pre-rendered alphas
            if alpha > 0.05:  # Skip nearly invisible particles
                particle_sprite = sprite.copy()
                particle_sprite.set_alpha(int(alpha * 255))
                blit_sequence.append((particle_sprite, (int(screen_x), int(screen_y))))

        # Batch blit nebula particles
        if blit_sequence:
            screen.blits(blit_sequence, doreturn=False)

    def _render_flowers(self, screen, flower_data, camera_x, camera_y):
        """
        PHASE 4: Render flowers with LOD scaling based on nectar level.

        Per architect specs:
        - Scale sprite size based on nectar percentage
        - Desaturate color when depleted

        Args:
            screen: Pygame surface
            flower_data: Dict with 'positions', 'nectar_pct', 'active'
            camera_x, camera_y: Camera position
        """
        positions = flower_data['positions']
        nectar_pct = flower_data['nectar_pct']
        active = flower_data['active']

        for i in range(len(positions)):
            if not active[i]:
                continue

            world_x = positions[i, 0]
            world_y = positions[i, 1]

            # World to screen transform
            screen_x = world_x - camera_x + self.screen_width / 2
            screen_y = world_y - camera_y + self.screen_height / 2

            # Frustum culling
            if not (0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height):
                continue

            # LOD: Scale size based on nectar (0.5 to 1.0 scale)
            nectar = nectar_pct[i]
            scale = 0.5 + 0.5 * nectar
            base_radius = 15
            radius = int(base_radius * scale)

            # Desaturate when depleted (full color at 100%, gray at 0%)
            full_color = (255, 100, 200)  # Pink/magenta for flowers
            gray = (150, 150, 150)

            # Lerp between gray and full color based on nectar
            color = tuple(int(gray[j] + (full_color[j] - gray[j]) * nectar) for j in range(3))

            # Draw flower as circle with petals
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)

            # Draw center (yellow)
            center_color = (255, 220, 0) if nectar > 0.2 else (150, 150, 100)
            pygame.draw.circle(screen, center_color, (int(screen_x), int(screen_y)), max(3, radius // 3))

    def _render_pheromone_heatmap(self, screen, pheromone_grid, camera_x, camera_y, opacity=0.2):
        """
        PHASE 4: Render pheromone heatmap overlay (debug mode).

        Per architect specs:
        - Amber heatmap with 0-40% opacity
        - Toggled with 'P' key
        - Adjustable with '[' and ']' keys

        Args:
            screen: Pygame surface
            pheromone_grid: (128, 128) float32 array
            camera_x, camera_y: Camera position
            opacity: Overlay opacity (0.0 - 0.4)
        """
        # Clamp opacity to architect's red line (0-40%)
        opacity = np.clip(opacity, 0.0, 0.4)

        chunk_size = WORLD_WIDTH / PHEROMONE_GRID_SIZE

        # Normalize pheromone values for visualization
        max_pheromone = np.max(pheromone_grid)
        if max_pheromone < 0.01:
            return  # Nothing to render

        for cy in range(PHEROMONE_GRID_SIZE):
            for cx in range(PHEROMONE_GRID_SIZE):
                pheromone = pheromone_grid[cy, cx]
                if pheromone < 0.01:
                    continue

                # World coordinates
                world_x = cx * chunk_size
                world_y = cy * chunk_size

                # Screen coordinates
                screen_x = world_x - camera_x + self.screen_width / 2
                screen_y = world_y - camera_y + self.screen_height / 2

                # Skip if off-screen
                if not (-chunk_size <= screen_x < self.screen_width + chunk_size and
                        -chunk_size <= screen_y < self.screen_height + chunk_size):
                    continue

                # Amber color (architect spec: amber heatmap)
                intensity = min(pheromone / max_pheromone, 1.0)
                alpha = int(intensity * opacity * 255)

                # Amber color (orange/yellow blend)
                color = (255, 180, 0, alpha)  # RGBA

                # Draw as filled rect with alpha
                surface = pygame.Surface((int(chunk_size), int(chunk_size)), pygame.SRCALPHA)
                surface.fill(color)
                screen.blit(surface, (int(screen_x), int(screen_y)))

    def _render_ghost_field(self, screen, resource_grid, exploration_grid, camera_x, camera_y, opacity=0.2):
        """
        PHASE 12.0: Render dual-channel ghost-field overlay.

        Cyan trails = Resource grid (Forager food paths)
        Violet markers = Exploration grid (Scout territory)

        Args:
            screen: Pygame surface
            resource_grid: (128, 128) float32 array - stable food trails
            exploration_grid: (128, 128) float32 array - volatile markers
            camera_x, camera_y: Camera position
            opacity: Overlay opacity (0.0 - 0.4)
        """
        opacity = np.clip(opacity, 0.0, 0.4)
        chunk_size = WORLD_WIDTH / PHEROMONE_GRID_SIZE

        # Normalize both grids for visualization
        max_resource = np.max(resource_grid)
        max_exploration = np.max(exploration_grid)

        for cy in range(PHEROMONE_GRID_SIZE):
            for cx in range(PHEROMONE_GRID_SIZE):
                resource_val = resource_grid[cy, cx]
                exploration_val = exploration_grid[cy, cx]

                # Skip empty cells
                if resource_val < 0.01 and exploration_val < 0.01:
                    continue

                # World coordinates
                world_x = cx * chunk_size
                world_y = cy * chunk_size

                # Screen coordinates
                screen_x = world_x - camera_x + self.screen_width / 2
                screen_y = world_y - camera_y + self.screen_height / 2

                # Skip if off-screen
                if not (-chunk_size <= screen_x < self.screen_width + chunk_size and
                        -chunk_size <= screen_y < self.screen_height + chunk_size):
                    continue

                # Blend colors: Cyan (resource) + Violet (exploration)
                r, g, b = 0, 0, 0
                total_alpha = 0

                if resource_val > 0.01 and max_resource > 0.01:
                    # Cyan (0, 255, 255) for resource trails
                    intensity = min(resource_val / max_resource, 1.0)
                    alpha = intensity * opacity
                    r += 0 * alpha
                    g += 255 * alpha
                    b += 255 * alpha
                    total_alpha += alpha

                if exploration_val > 0.01 and max_exploration > 0.01:
                    # Violet (180, 0, 255) for exploration markers
                    intensity = min(exploration_val / max_exploration, 1.0)
                    alpha = intensity * opacity
                    r += 180 * alpha
                    g += 0 * alpha
                    b += 255 * alpha
                    total_alpha += alpha

                if total_alpha > 0:
                    # Normalize and convert to integer color
                    final_alpha = min(int(total_alpha * 255), 255)
                    color = (int(r), int(g), int(b), final_alpha)

                    # Draw as filled rect with alpha
                    surface = pygame.Surface((int(chunk_size), int(chunk_size)), pygame.SRCALPHA)
                    surface.fill(color)
                    screen.blit(surface, (int(screen_x), int(screen_y)))

    def render_debug_overlay(self, screen, render_data, fps, sim_time_ms):
        """
        Render debug overlay with stats.

        Args:
            screen: Pygame surface
            render_data: Dict from simulation
            fps: Current FPS
            sim_time_ms: Last sim update time in ms
        """
        font = pygame.font.SysFont('monospace', 12)

        # Count active entities (cast flags to int for bitwise ops - Phase 2B Step 2)
        vanguard_flags = render_data['vanguard'][:, V_STATE_FLAGS].view(np.int32)
        vanguard_count = np.sum(~(vanguard_flags & FLAG_DEAD).astype(bool))

        # PHASE 2 FIX: Legion now uses FLAG_DEAD like Vanguard
        legion_flags = render_data['legion'][:, L_STATE_FLAGS].view(np.int32)
        legion_count = np.sum(~(legion_flags & FLAG_DEAD).astype(bool))
        nebula_count = len(render_data['nebula'])
        total_count = vanguard_count + legion_count + nebula_count

        # V6.0: RAM monitoring (exclude surface allocations)
        import psutil
        process = psutil.Process()
        ram_mb = process.memory_info().rss / (1024 * 1024)

        # V6.0: Coherence index
        coherence = render_data.get('coherence_index', 0.0)

        stats = [
            f"FPS: {fps:.1f} (target: {FPS_TARGET})",
            f"Sim: {sim_time_ms:.2f} ms (budget: {FRAME_BUDGET_MS - SAFETY_MARGIN_MS:.1f} ms)",
            f"RAM: {ram_mb:.1f} MB",
            f"Coherence: {coherence:.2f} (0=random, 1=aligned)",
            f"Vanguard: {vanguard_count}/{MAX_VANGUARD}",
            f"Legion: {legion_count}/{MAX_LEGION}",
            f"Nebula: {nebula_count}",
            f"Total illusion: ~{total_count:,} bees",
        ]

        y = 10
        for stat in stats:
            text = font.render(stat, True, (0, 255, 0))
            screen.blit(text, (10, y))
            y += 15

    def render_density_field(self, screen, density_field, camera_x, camera_y):
        """
        Debug: Render density field as heatmap.

        Args:
            screen: Pygame surface
            density_field: (128, 128, 4) array
            camera_x, camera_y: Camera position
        """
        chunk_size = WORLD_WIDTH / FIELD_RES

        for cy in range(FIELD_RES):
            for cx in range(FIELD_RES):
                density = density_field[cy, cx, D_DENSITY]
                if density < 0.01:
                    continue

                # World coordinates
                world_x = cx * chunk_size
                world_y = cy * chunk_size

                # Screen coordinates
                screen_x = world_x - camera_x + self.screen_width / 2
                screen_y = world_y - camera_y + self.screen_height / 2

                # Skip if off-screen
                if not (-chunk_size <= screen_x < self.screen_width + chunk_size and
                        -chunk_size <= screen_y < self.screen_height + chunk_size):
                    continue

                # Color based on density (red = high, blue = low)
                intensity = min(density / 5.0, 1.0)
                color = (int(intensity * 255), 0, int((1.0 - intensity) * 100))

                pygame.draw.rect(
                    screen,
                    color,
                    (int(screen_x), int(screen_y), int(chunk_size), int(chunk_size)),
                    1  # Outline only
                )


# ============================================================================
# CAMERA CONTROLLER
# ============================================================================

class Camera:
    """Simple camera with smooth following."""

    def __init__(self, x, y):
        """Initialize camera at position."""
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.lerp_speed = 0.1

    def set_target(self, x, y):
        """Set camera target position."""
        self.target_x = x
        self.target_y = y

    def update(self, dt):
        """Smooth lerp to target."""
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed

    def move(self, dx, dy):
        """Move camera by offset (for user control)."""
        self.x += dx
        self.y += dy
        self.target_x = self.x
        self.target_y = self.y


# ============================================================================
# PERFORMANCE PROFILER
# ============================================================================

class PerformanceProfiler:
    """Simple frame timing profiler."""

    def __init__(self):
        """Initialize profiler."""
        self.frame_times = []
        self.sim_times = []
        self.render_times = []

    def record_frame(self, total_ms, sim_ms, render_ms):
        """Record frame timings."""
        self.frame_times.append(total_ms)
        self.sim_times.append(sim_ms)
        self.render_times.append(render_ms)

        # Keep only last 60 frames
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
            self.sim_times.pop(0)
            self.render_times.pop(0)

    def get_stats(self):
        """Get performance statistics."""
        if not self.frame_times:
            return {
                'avg_fps': 0,
                'avg_frame_ms': 0,
                'avg_sim_ms': 0,
                'avg_render_ms': 0,
            }

        avg_frame = np.mean(self.frame_times)
        avg_fps = 1000.0 / avg_frame if avg_frame > 0 else 0

        return {
            'avg_fps': avg_fps,
            'avg_frame_ms': avg_frame,
            'avg_sim_ms': np.mean(self.sim_times),
            'avg_render_ms': np.mean(self.render_times),
        }
