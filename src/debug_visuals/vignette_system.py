"""
APIS-OVERSEER Vignette System (Static Gradient Overlay)
Phase 6: Debug Visuals System

Per Architect Spec [ARCH-SDL-PHASE6-002]:
- Static radial gradient overlay (screen-space)
- Pre-rendered at startup (zero per-frame allocation)
- Global stress intensity from mean bee health
- ≤0.1ms CPU budget (single Surface.blit per frame)
- Subtle red vignette (inner radius 0.6, outer radius 1.0)
"""

import numpy as np
import pygame
from config import (
    VIGNETTE_ENABLED,
    VIGNETTE_INNER_RADIUS,
    VIGNETTE_OUTER_RADIUS,
    V_HEALTH,
    L_HEALTH
)


class VignetteSystem:
    """
    Static screen-space stress vignette overlay.

    Responsibilities:
    - Pre-render radial vignette gradient at startup
    - Modulate alpha by global bee health (mean across population)
    - Single blit per frame (GPU-accelerated)
    - Subtle red tint to indicate colony stress
    """

    def __init__(self, screen_width, screen_height):
        """
        Initialize vignette system with pre-rendered gradient.

        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
        """
        self.width = screen_width
        self.height = screen_height
        self.enabled = VIGNETTE_ENABLED

        # Pre-rendered vignette surface
        self.vignette_surface = None

        # Initialize gradient
        if self.enabled:
            self._create_vignette_gradient()

    def _create_vignette_gradient(self):
        """
        Pre-render radial vignette gradient at startup.
        Zero per-frame allocation - created once, alpha modulated each frame.
        """
        # Create RGBA surface with per-pixel alpha
        self.vignette_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Generate radial gradient from screen center
        center_x = self.width / 2
        center_y = self.height / 2
        max_dist = np.sqrt(center_x**2 + center_y**2)  # Diagonal distance

        y, x = np.ogrid[:self.height, :self.width]
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)

        # Normalize distance (0.0 = center, 1.0 = corner)
        dist_normalized = dist / max_dist

        # Vignette gradient: inner radius (transparent) → outer radius (opaque)
        # Alpha = 0 inside inner_radius, ramps to max at outer_radius
        vignette_alpha = np.clip(
            (dist_normalized - VIGNETTE_INNER_RADIUS) / (VIGNETTE_OUTER_RADIUS - VIGNETTE_INNER_RADIUS),
            0.0,
            1.0
        )

        # Smooth falloff using smoothstep
        vignette_alpha = vignette_alpha * vignette_alpha * (3.0 - 2.0 * vignette_alpha)

        # Red stress color (R=180, G=0, B=0 for subtle tint)
        red_channel = np.full_like(vignette_alpha, 180, dtype=np.uint8)
        green_channel = np.zeros_like(vignette_alpha, dtype=np.uint8)
        blue_channel = np.zeros_like(vignette_alpha, dtype=np.uint8)
        alpha_channel = (vignette_alpha * 120).astype(np.uint8)  # Max alpha = 120 (~47% opacity)

        # Combine RGBA channels
        rgba_array = np.dstack([red_channel, green_channel, blue_channel, alpha_channel])

        # Write to surface using surfarray (much faster than set_at for large images)
        # Note: pygame surfarray expects (width, height, channels), so transpose
        pygame.surfarray.pixels_alpha(self.vignette_surface)[:] = alpha_channel.T
        pygame.surfarray.pixels_red(self.vignette_surface)[:] = red_channel.T
        pygame.surfarray.pixels_green(self.vignette_surface)[:] = green_channel.T
        pygame.surfarray.pixels_blue(self.vignette_surface)[:] = blue_channel.T

        print(f"[VIGNETTE] Pre-rendered gradient overlay ({self.width}x{self.height})")

    def render_vignette(self, screen, vanguard, legion):
        """
        Render stress vignette with global health modulation.

        Args:
            screen: Pygame Surface to render to
            vanguard: (N, 17) Vanguard state array
            legion: (M, 12) Legion state array
        """
        if not self.enabled or self.vignette_surface is None:
            return

        # Calculate global stress (mean health across all bees)
        v_health = vanguard[:, V_HEALTH]
        l_health = legion[:, L_HEALTH]
        mean_health = np.mean(np.concatenate([v_health, l_health]))

        # Stress factor: 0.0 = healthy (no vignette), 1.0 = critical (full intensity)
        stress_factor = 1.0 - mean_health

        # Only render if stress is significant (health < 0.8)
        if stress_factor > 0.2:
            # Modulate vignette alpha by stress
            vignette_copy = self.vignette_surface.copy()
            vignette_copy.set_alpha(int(stress_factor * 255))

            # Single blit to screen (GPU-accelerated)
            screen.blit(vignette_copy, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def cleanup(self):
        """Release resources on shutdown."""
        if self.vignette_surface:
            del self.vignette_surface
            print("[VIGNETTE] Resources released")
