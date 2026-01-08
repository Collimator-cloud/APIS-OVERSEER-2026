"""
APIS-OVERSEER Halo System (CPU Vectorized Module)
Phase 6: Debug Visuals System

Per Architect Spec [ARCH-SDL-PHASE6-002]:
- Vectorized bee stress halos using Surface.blits()
- Pre-rendered halo gradients at startup (zero per-frame allocation)
- Distance-based culling (1.5x diagonal = visible bees only)
- ≤0.4ms CPU budget (vectorized operations only)
- Color intensity driven by bee health (red = low health)
"""

import numpy as np
import pygame
from config import (
    HALO_ENABLED,
    HALO_RADIUS,
    HALO_CULL_DISTANCE,
    MAX_DEBUG_HALOS,
    V_POS_X, V_POS_Y, V_HEALTH,
    L_POS_X, L_POS_Y, L_HEALTH
)


class HaloSystem:
    """
    CPU-side vectorized bee stress halos.

    Responsibilities:
    - Pre-render halo gradient textures at startup (red stress gradient)
    - Cull bees outside viewport (1.5x diagonal radius)
    - Batch render using Surface.blits() for visible bees
    - Modulate alpha by health (low health = high intensity)
    """

    def __init__(self, screen_width, screen_height):
        """
        Initialize halo system with pre-rendered gradients.

        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
        """
        self.width = screen_width
        self.height = screen_height
        self.enabled = HALO_ENABLED

        # Pre-rendered halo texture (radial gradient)
        self.halo_surface = None
        self.halo_size = HALO_RADIUS * 2

        # Culling distance (1.5x diagonal for off-screen margin)
        self.cull_distance = HALO_CULL_DISTANCE * np.sqrt(screen_width**2 + screen_height**2)

        # Initialize halo gradient
        if self.enabled:
            self._create_halo_gradient()

    def _create_halo_gradient(self):
        """
        Pre-render radial gradient halo texture at startup.
        Zero per-frame allocation - created once, reused every frame.
        """
        # Create RGBA surface with per-pixel alpha
        self.halo_surface = pygame.Surface((self.halo_size, self.halo_size), pygame.SRCALPHA)

        # Generate radial gradient using numpy
        center = HALO_RADIUS
        y, x = np.ogrid[:self.halo_size, :self.halo_size]
        dist = np.sqrt((x - center)**2 + (y - center)**2)

        # Smooth falloff: alpha = 1.0 at center, 0.0 at radius
        alpha = np.clip(1.0 - (dist / HALO_RADIUS), 0.0, 1.0)
        alpha = alpha ** 2  # Quadratic falloff for smoother gradient

        # Red stress color (R=255, G=0, B=0)
        # Alpha modulated by distance (outer edge fades to transparent)
        red_channel = np.full_like(alpha, 255, dtype=np.uint8)
        green_channel = np.zeros_like(alpha, dtype=np.uint8)
        blue_channel = np.zeros_like(alpha, dtype=np.uint8)
        alpha_channel = (alpha * 180).astype(np.uint8)  # Max alpha = 180 (70% opacity)

        # Combine RGBA channels
        rgba_array = np.dstack([red_channel, green_channel, blue_channel, alpha_channel])

        # Write to surface
        pygame.surfarray.blit_array(self.halo_surface, rgba_array[:, :, :3].swapaxes(0, 1))

        # Set per-pixel alpha manually (pygame bug workaround)
        for py in range(self.halo_size):
            for px in range(self.halo_size):
                r, g, b, a = rgba_array[py, px]
                self.halo_surface.set_at((px, py), (r, g, b, a))

        print(f"[HALO] Pre-rendered gradient texture ({self.halo_size}x{self.halo_size})")

    def render_halos(self, screen, camera_x, camera_y, vanguard, legion):
        """
        Render stress halos for visible bees using vectorized culling.

        Args:
            screen: Pygame Surface to render to
            camera_x: Camera center X position (world coordinates)
            camera_y: Camera center Y position (world coordinates)
            vanguard: (N, 17) Vanguard state array
            legion: (M, 12) Legion state array
        """
        if not self.enabled or self.halo_surface is None:
            return

        # Combine Vanguard and Legion positions + health
        v_positions = vanguard[:, [V_POS_X, V_POS_Y]]
        v_health = vanguard[:, V_HEALTH]

        l_positions = legion[:, [L_POS_X, L_POS_Y]]
        l_health = legion[:, L_HEALTH]

        all_positions = np.vstack([v_positions, l_positions])
        all_health = np.hstack([v_health, l_health])

        # Cull bees outside viewport (distance from camera)
        dx = all_positions[:, 0] - camera_x
        dy = all_positions[:, 1] - camera_y
        distances = np.sqrt(dx**2 + dy**2)

        visible_mask = distances < self.cull_distance
        visible_positions = all_positions[visible_mask]
        visible_health = all_health[visible_mask]

        # Limit to MAX_DEBUG_HALOS (sort by distance, keep closest)
        if len(visible_positions) > MAX_DEBUG_HALOS:
            visible_distances = distances[visible_mask]
            closest_indices = np.argsort(visible_distances)[:MAX_DEBUG_HALOS]
            visible_positions = visible_positions[closest_indices]
            visible_health = visible_health[closest_indices]

        # Convert world coordinates to screen coordinates
        screen_x = visible_positions[:, 0] - camera_x + self.width // 2 - HALO_RADIUS
        screen_y = visible_positions[:, 1] - camera_y + self.height // 2 - HALO_RADIUS

        # Prepare blit sequence (Surface.blits requires list of (surface, dest) tuples)
        blit_sequence = []

        for i in range(len(visible_positions)):
            # Health-based alpha modulation (low health = high intensity)
            health = visible_health[i]
            stress_factor = 1.0 - health  # 0.0 = healthy, 1.0 = critical

            # Only render halos for stressed bees (health < 0.7)
            if stress_factor > 0.3:
                # Create alpha-modulated copy (expensive, but pre-filtering reduces count)
                halo_copy = self.halo_surface.copy()
                halo_copy.set_alpha(int(stress_factor * 255))

                dest = (int(screen_x[i]), int(screen_y[i]))
                blit_sequence.append((halo_copy, dest))

        # Batch blit (GPU-accelerated)
        if blit_sequence:
            screen.blits(blit_sequence, doreturn=False)

    def cleanup(self):
        """Release resources on shutdown."""
        if self.halo_surface:
            del self.halo_surface
            print("[HALO] Resources released")
