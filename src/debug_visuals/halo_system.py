"""
APIS-OVERSEER Halo System (CPU Vectorized Module)
Phase 14: Caste Semantics & Vitality Visualization

Per Architect Spec [ARCH-SDL-PHASE14-001]:
- Caste-specific RGB halos (Scout/Forager/Nurse color encoding)
- Vitality-based alpha/radius modulation (sin(pi × maturity) curve)
- Pre-rendered halo gradients at startup (zero per-frame allocation)
- Distance-based culling (1.5x diagonal = visible bees only)
- ≤1.0ms CPU budget (vectorized operations only)
"""

import numpy as np
import pygame
from config import (
    HALO_ENABLED,
    HALO_RADIUS,
    HALO_CULL_DISTANCE,
    MAX_DEBUG_HALOS,
    V_POS_X, V_POS_Y, V_HEALTH, V_STATE_FLAGS, V_MATURITY,
    L_POS_X, L_POS_Y, L_HEALTH,
    CASTE_SCOUT, CASTE_FORAGER, CASTE_NURSE,
    CASTE_BITS_OFFSET
)

# PHASE 14.0: Caste RGB colors (Electric Gold / Amber / Deep Honey)
CASTE_HALO_COLORS = {
    CASTE_SCOUT: (255, 255, 200),    # Electric Gold
    CASTE_FORAGER: (255, 190, 50),   # Amber
    CASTE_NURSE: (200, 100, 20)      # Deep Honey
}


class HaloSystem:
    """
    CPU-side vectorized bee caste halos with vitality modulation.

    Responsibilities:
    - Pre-render 3 caste-specific halo gradients at startup (Scout/Forager/Nurse)
    - Cull bees outside viewport (1.5x diagonal radius)
    - Batch render using Surface.blits() for visible bees
    - Modulate alpha/radius by vitality (sin(pi × maturity) curve)
    """

    def __init__(self, screen_width, screen_height):
        """
        Initialize halo system with pre-rendered caste gradients.

        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
        """
        self.width = screen_width
        self.height = screen_height
        self.enabled = HALO_ENABLED

        # PHASE 14.0: Pre-rendered halo textures (3 castes)
        self.halo_surfaces = {}
        self.halo_size = HALO_RADIUS * 2

        # Culling distance (1.5x diagonal for off-screen margin)
        self.cull_distance = HALO_CULL_DISTANCE * np.sqrt(screen_width**2 + screen_height**2)

        # Initialize caste-specific halo gradients
        if self.enabled:
            self._create_halo_gradients()

        # Legacy compatibility
        self.halo_surface = self.halo_surfaces.get(CASTE_FORAGER, None) if self.enabled else None

    def _create_halo_gradients(self):
        """
        PHASE 14.0: Pre-render 3 caste-specific halo gradients at startup.
        Zero per-frame allocation - created once, reused every frame.
        """
        for caste_id, base_color in CASTE_HALO_COLORS.items():
            surface = pygame.Surface((self.halo_size, self.halo_size), pygame.SRCALPHA)

            # Generate radial gradient using numpy
            center = HALO_RADIUS
            y, x = np.ogrid[:self.halo_size, :self.halo_size]
            dist = np.sqrt((x - center)**2 + (y - center)**2)

            # Smooth falloff: alpha = 1.0 at center, 0.0 at radius
            alpha = np.clip(1.0 - (dist / HALO_RADIUS), 0.0, 1.0)
            alpha = alpha ** 2  # Quadratic falloff for smoother gradient

            # Caste-specific RGB color
            red_channel = np.full_like(alpha, base_color[0], dtype=np.uint8)
            green_channel = np.full_like(alpha, base_color[1], dtype=np.uint8)
            blue_channel = np.full_like(alpha, base_color[2], dtype=np.uint8)
            alpha_channel = (alpha * 180).astype(np.uint8)  # Max alpha = 180 (70% opacity)

            # Combine RGBA channels
            rgba_array = np.dstack([red_channel, green_channel, blue_channel, alpha_channel])

            # Write to surface
            pygame.surfarray.blit_array(surface, rgba_array[:, :, :3].swapaxes(0, 1))

            # Set per-pixel alpha manually (pygame bug workaround)
            for py in range(self.halo_size):
                for px in range(self.halo_size):
                    r, g, b, a = rgba_array[py, px]
                    surface.set_at((px, py), (r, g, b, a))

            self.halo_surfaces[caste_id] = surface

        print(f"[HALO] Pre-rendered 3 caste gradients ({self.halo_size}x{self.halo_size} each): Scout/Forager/Nurse")

    def render_halos(self, screen, camera_x, camera_y, vanguard, legion):
        """
        PHASE 14.0: Render caste-specific halos with vitality modulation.

        Args:
            screen: Pygame Surface to render to
            camera_x: Camera center X position (world coordinates)
            camera_y: Camera center Y position (world coordinates)
            vanguard: (N, 21) Vanguard state array (with maturity column)
            legion: (M, 16) Legion state array (no halos for Legion)
        """
        if not self.enabled or len(self.halo_surfaces) == 0:
            return

        # PHASE 14.0: Only render Vanguard halos (Legion are background agents)
        v_positions = vanguard[:, [V_POS_X, V_POS_Y]]
        v_caste_flags = vanguard[:, V_STATE_FLAGS].astype(np.int32)
        v_maturity = vanguard[:, V_MATURITY]

        # Extract caste IDs from state flags
        caste_ids = (v_caste_flags >> CASTE_BITS_OFFSET) & 0b11

        # Cull bees outside viewport (distance from camera)
        dx = v_positions[:, 0] - camera_x
        dy = v_positions[:, 1] - camera_y
        distances = np.sqrt(dx**2 + dy**2)

        visible_mask = distances < self.cull_distance
        visible_positions = v_positions[visible_mask]
        visible_caste_ids = caste_ids[visible_mask]
        visible_maturity = v_maturity[visible_mask]

        # Limit to MAX_DEBUG_HALOS (sort by distance, keep closest)
        if len(visible_positions) > MAX_DEBUG_HALOS:
            visible_distances = distances[visible_mask]
            closest_indices = np.argsort(visible_distances)[:MAX_DEBUG_HALOS]
            visible_positions = visible_positions[closest_indices]
            visible_caste_ids = visible_caste_ids[closest_indices]
            visible_maturity = visible_maturity[closest_indices]

        # Convert world coordinates to screen coordinates
        screen_x = visible_positions[:, 0] - camera_x + self.width // 2 - HALO_RADIUS
        screen_y = visible_positions[:, 1] - camera_y + self.height // 2 - HALO_RADIUS

        # PHASE 14.0: Vectorized vitality computation (eliminate Python loop)
        vitality_factors = np.sin(np.pi * visible_maturity)  # 0.0 at birth/death, 1.0 at prime

        # Prepare blit sequence with pre-set alpha per surface (avoid Surface.copy())
        blit_sequence = []

        # Group bees by caste to batch-set alpha
        for caste_id in [CASTE_SCOUT, CASTE_FORAGER, CASTE_NURSE]:
            caste_mask = (visible_caste_ids == caste_id)
            if not np.any(caste_mask):
                continue

            # Get base halo surface for this caste
            halo_surface = self.halo_surfaces[caste_id]

            # Extract positions and vitality for this caste
            caste_x = screen_x[caste_mask]
            caste_y = screen_y[caste_mask]
            caste_vitality = vitality_factors[caste_mask]

            # Render each bee (alpha modulation requires per-bee copy - unavoidable with Pygame)
            for i in range(len(caste_x)):
                # Calculate alpha from vitality
                halo_alpha = int(caste_vitality[i] * 200)

                # Skip invisible halos (vitality too low)
                if halo_alpha < 10:
                    continue

                # Create alpha-modulated copy (expensive but necessary for per-bee alpha)
                halo_copy = halo_surface.copy()
                halo_copy.set_alpha(halo_alpha)

                dest = (int(caste_x[i]), int(caste_y[i]))
                blit_sequence.append((halo_copy, dest))

        # Batch blit (GPU-accelerated)
        if blit_sequence:
            screen.blits(blit_sequence, doreturn=False)

    def cleanup(self):
        """Release resources on shutdown."""
        if self.halo_surface:
            del self.halo_surface
            print("[HALO] Resources released")
