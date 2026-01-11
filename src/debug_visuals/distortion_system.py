"""
APIS-OVERSEER Distortion System (GPU Shader Module)
Phase 6: Debug Visuals System

Per Architect Spec [ARCH-SDL-PHASE6-002]:
- ModernGL fragment shader for pheromone stress shimmer
- Render-to-texture pipeline: Pygame Surface → GL Texture → Shader → Blit back
- Zero per-frame allocations (compile shader + allocate textures at startup)
- ≤0.3ms GPU shader budget
- Ghost Layer only (no position writes, purely visual effect)
"""

import numpy as np
import pygame
from config import (
    DISTORTION_ENABLED,
    DISTORTION_AMPLITUDE,
    DISTORTION_FREQUENCY,
    PHEROMONE_GRID_SIZE
)

# TRIAGE-004: Move ModernGL import to global scope (dependency hardening)
try:
    import moderngl
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False
    moderngl = None

# ============================================================================
# TASK 8.2: SURGICAL TIMELINE INSTRUMENTATION (Phase 8 Latency Trap Test)
# ============================================================================
# Module-level buffer for 10-frame GPU timing capture
# Buffered output prevents console I/O from contaminating millisecond measurements
_surgical_timeline_buffer = []
_grace_frames_remaining = 10  # Grace window: suppress throttle for first 10 frames


# TRIAGE-005 EMERGENCY: Simplified shader (35ms → 0.3ms)
# Replace expensive per-pixel Perlin with pre-computed noise texture
DISTORTION_FRAGMENT_SHADER = """
#version 330

uniform sampler2D tex;
uniform sampler2D noise_tex;
uniform sampler2D pheromone_tex;
uniform float intensity;

in vec2 v_texcoord;
out vec4 f_color;

void main() {
    // Sample pheromone stress (single texture lookup)
    vec4 pheromone = texture(pheromone_tex, v_texcoord);
    float stress = (pheromone.r + pheromone.g + pheromone.b) * 0.333;

    // Sample pre-computed noise (tiled 64x64 texture)
    vec2 noise_uv = v_texcoord * 10.0;  // Tile noise
    vec2 noise = texture(noise_tex, noise_uv).rg;

    // Convert from [0,1] to [-1,1] and scale
    vec2 displacement = (noise - 0.5) * 0.02 * intensity * stress;

    // Apply distortion (single texture lookup)
    f_color = texture(tex, v_texcoord + displacement);
}
"""

DISTORTION_VERTEX_SHADER = """
#version 330

in vec2 in_position;
in vec2 in_texcoord;

out vec2 v_texcoord;

void main() {
    v_texcoord = in_texcoord;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""


class DistortionSystem:
    """
    GPU shader module for pheromone-driven stress shimmer.

    Responsibilities:
    - Compile fragment shader at startup
    - Convert Pygame Surface → OpenGL texture
    - Apply Perlin noise displacement based on pheromone density
    - Render back to Pygame Surface
    - Track GPU shader time for budget compliance
    """

    def __init__(self, screen_width, screen_height, performance_monitor):
        """
        Initialize distortion system with ModernGL context.

        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
            performance_monitor: PerformanceMonitor instance for GPU status
        """
        self.width = screen_width
        self.height = screen_height
        self.perf_monitor = performance_monitor

        # GPU context and shader
        self.ctx = None
        self.program = None
        self.vao = None
        self.texture = None
        self.pheromone_texture = None
        self.fbo = None

        # Enable/disable state
        self.enabled = DISTORTION_ENABLED and self.perf_monitor.gpu_enabled

        # Initialize GPU resources if available
        if self.enabled:
            self._init_gpu_resources()

    def _init_gpu_resources(self):
        """
        Initialize ModernGL context, compile shaders, allocate textures.
        Zero per-frame allocation - all resources created at startup.
        """
        # TRIAGE-004: Use global ModernGL import
        if not MODERNGL_AVAILABLE:
            print("[DISTORTION] ModernGL not available, disabling")
            self.enabled = False
            return

        try:
            # Create standalone context (reuse detection from performance_monitor)
            self.ctx = moderngl.create_context(standalone=True, require=330)

            if self.ctx is None:
                print("[DISTORTION] Failed to create ModernGL context")
                self.enabled = False
                return

            # Compile shader program
            self.program = self.ctx.program(
                vertex_shader=DISTORTION_VERTEX_SHADER,
                fragment_shader=DISTORTION_FRAGMENT_SHADER
            )

            # Create fullscreen quad (normalized device coordinates)
            vertices = np.array([
                # Position (x, y)    Texcoord (u, v)
                -1.0, -1.0,          0.0, 1.0,  # Bottom-left
                 1.0, -1.0,          1.0, 1.0,  # Bottom-right
                -1.0,  1.0,          0.0, 0.0,  # Top-left
                 1.0,  1.0,          1.0, 0.0,  # Top-right
            ], dtype='f4')

            vbo = self.ctx.buffer(vertices.tobytes())
            self.vao = self.ctx.simple_vertex_array(
                self.program,
                vbo,
                'in_position', 'in_texcoord'
            )

            # Allocate screen texture (RGBA8)
            self.texture = self.ctx.texture((self.width, self.height), 4)
            self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

            # TRIAGE-005: Pre-compute noise texture (64x64, RG channels for 2D noise)
            noise_data = np.random.randn(64, 64, 2).astype(np.float32)
            # Normalize to [0, 1] range
            noise_data = (noise_data - noise_data.min()) / (noise_data.max() - noise_data.min())
            noise_bytes = (noise_data * 255).astype(np.uint8).tobytes()

            self.noise_texture = self.ctx.texture((64, 64), 2)
            self.noise_texture.write(noise_bytes)
            self.noise_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

            # Allocate pheromone texture (RGB8, lower resolution)
            self.pheromone_texture = self.ctx.texture((PHEROMONE_GRID_SIZE, PHEROMONE_GRID_SIZE), 3)
            self.pheromone_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

            # Create framebuffer for render-to-texture
            self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])

            print(f"[DISTORTION] GPU shader initialized ({self.width}x{self.height})")

        except Exception as e:
            print(f"[DISTORTION] GPU init failed: {e}")
            self.enabled = False

    def apply_distortion(self, screen_surface, pheromone_field, frame_count=0):
        """
        Apply pheromone-driven distortion to the screen.

        Args:
            screen_surface: Pygame Surface to distort
            pheromone_field: (128, 128, 3) numpy array of pheromone RGB intensities
            frame_count: Current frame number (for Task 8.2 timeline correlation)

        Returns:
            pygame.Surface: Distorted surface (or original if GPU unavailable)
        """
        global _surgical_timeline_buffer, _grace_frames_remaining

        if not self.enabled or self.ctx is None:
            return screen_surface

        import time

        # TASK 8.2: Initialize timeline entry
        timeline_entry = {'frame': frame_count}

        try:
            # ================================================================
            # STAGE 1: UPLOAD (CPU → GPU)
            # ================================================================
            t0 = time.perf_counter()

            # Convert Pygame Surface to bytes (RGBA)
            surface_bytes = pygame.image.tostring(screen_surface, 'RGBA', True)
            self.texture.write(surface_bytes)

            # Upload pheromone field to GPU (normalize to 0-1 range)
            pheromone_rgb = (pheromone_field * 255).astype(np.uint8)
            self.pheromone_texture.write(pheromone_rgb.tobytes())

            timeline_entry['upload_ms'] = (time.perf_counter() - t0) * 1000.0

            # ================================================================
            # STAGE 2: DISPATCH (Shader Execution)
            # ================================================================
            t1 = time.perf_counter()

            # Bind textures (TRIAGE-005: Now includes noise texture)
            self.texture.use(location=0)
            self.noise_texture.use(location=1)
            self.pheromone_texture.use(location=2)

            # Set shader uniforms (TRIAGE-005: Simplified)
            self.program['tex'] = 0
            self.program['noise_tex'] = 1
            self.program['pheromone_tex'] = 2
            self.program['intensity'] = DISTORTION_AMPLITUDE / 100.0  # Normalize intensity

            # Render to framebuffer
            self.fbo.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            timeline_entry['dispatch_ms'] = (time.perf_counter() - t1) * 1000.0

            # ================================================================
            # STAGE 3: DOWNLOAD (GPU → CPU)
            # ================================================================
            t2 = time.perf_counter()

            # Read back to Pygame Surface
            distorted_bytes = self.fbo.read(components=4)
            distorted_surface = pygame.image.fromstring(
                distorted_bytes,
                (self.width, self.height),
                'RGBA',
                True  # Flip vertically (OpenGL vs Pygame coordinate system)
            )

            timeline_entry['download_ms'] = (time.perf_counter() - t2) * 1000.0

            # ================================================================
            # STAGE 4: SYNC (Driver overhead - implicit in total)
            # ================================================================
            # ModernGL operations are synchronous, so sync is embedded in stages above
            # Calculate sync as residual from total minus explicit stages
            total_measured = timeline_entry['upload_ms'] + timeline_entry['dispatch_ms'] + timeline_entry['download_ms']
            t3 = time.perf_counter()
            # Explicit sync point (finish any pending operations)
            self.ctx.finish()
            timeline_entry['sync_ms'] = (time.perf_counter() - t3) * 1000.0

            # Total GPU time
            gpu_time_ms = total_measured + timeline_entry['sync_ms']
            timeline_entry['total_ms'] = gpu_time_ms

            # Buffer timeline (no console output yet)
            _surgical_timeline_buffer.append(timeline_entry)

            # Record to performance monitor
            self.perf_monitor.record_gpu_time(gpu_time_ms)

            # ================================================================
            # TASK 8.2: GRACE WINDOW (Suppress 1.0ms throttle for 10 frames)
            # ================================================================
            if gpu_time_ms > 1.0:
                if _grace_frames_remaining > 0:
                    _grace_frames_remaining -= 1
                    print(f"[TASK 8.2] Grace frame {10 - _grace_frames_remaining}/10: GPU {gpu_time_ms:.2f}ms (throttle suppressed)")
                else:
                    print(f"[DISTORTION] EMERGENCY DISABLE: GPU time {gpu_time_ms:.1f}ms > 1.0ms (grace expired)")
                    self.enabled = False
                    return screen_surface

            return distorted_surface

        except Exception as e:
            print(f"[DISTORTION] Shader error: {e}")
            self.enabled = False  # Fallback to CPU rendering
            return screen_surface

    def cleanup(self):
        """Release GPU resources on shutdown."""
        if self.ctx:
            if self.texture:
                self.texture.release()
            if self.pheromone_texture:
                self.pheromone_texture.release()
            if self.fbo:
                self.fbo.release()
            if self.vao:
                self.vao.release()
            if self.program:
                self.program.release()
            self.ctx.release()
            print("[DISTORTION] GPU resources released")
