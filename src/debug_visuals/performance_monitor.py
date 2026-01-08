"""
APIS-OVERSEER Performance Monitor & GPU Detection
Phase 6: Debug Visuals System

Per Architect Spec [ARCH-SDL-PHASE6-002]:
- Robust GPU detection with ModernGL context creation
- Auto-throttle protection (14ms breach → disable debug)
- Frame time tracking (5-frame moving window)
- RAM monitoring (2Hz sampling, TRIAGE-004)
"""

import time
from collections import deque
from config import (
    THROTTLE_THRESHOLD_MS,
    GPU_MIN_OPENGL_VERSION,
    GPU_MIN_TEXTURE_SIZE,
    GPU_SHADER_BUDGET_MS
)

# TRIAGE-004: psutil for RAM monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None


class PerformanceMonitor:
    """
    The Brain: Auto-throttle guardian and GPU capability detector.

    Responsibilities:
    - Detect ModernGL GPU capabilities at startup
    - Track frame times (5-frame window)
    - Auto-disable debug visuals if >14ms for 5 consecutive frames
    - Report GPU status to debug overlay
    """

    def __init__(self):
        """Initialize performance monitor with GPU detection."""
        # GPU capabilities
        self.gpu_enabled = False
        self.gpu_version = "N/A"
        self.gpu_renderer = "N/A"
        self.gpu_error = None

        # Frame time tracking (5-frame moving window)
        self.frame_times = deque(maxlen=5)
        self.breach_count = 0  # Consecutive frames >14ms

        # Debug visual enable state
        self.debug_enabled = True

        # GPU timing
        self.last_gpu_time_ms = 0.0

        # TRIAGE-004: RAM monitoring (2Hz sampling)
        self.ram_usage_mb = 0.0
        self.last_ram_sample_time = 0.0
        self.ram_sample_interval = 0.5  # 2Hz

        # Attempt GPU initialization
        self._detect_gpu()

    def _detect_gpu(self):
        """
        Robust GPU detection with ModernGL context creation.

        Per Architect Spec:
        - Create standalone context (no pygame coupling)
        - Query version, renderer, max texture size
        - Silent fallback on failure
        """
        try:
            import moderngl

            # Create standalone context (no window required)
            ctx = moderngl.create_context(standalone=True, require=330)

            if ctx is None:
                self.gpu_error = "Context creation returned None"
                return

            # Query GPU info
            info = ctx.info
            self.gpu_version = info.get('GL_VERSION', 'Unknown')
            self.gpu_renderer = info.get('GL_RENDERER', 'Unknown')

            # Check version compatibility
            version_str = self.gpu_version.split()[0] if self.gpu_version != 'Unknown' else "0.0"
            try:
                major, minor = map(int, version_str.split('.')[:2])
                if (major, minor) < GPU_MIN_OPENGL_VERSION:
                    self.gpu_error = f"OpenGL {major}.{minor} < required 3.3"
                    ctx.release()
                    return
            except (ValueError, IndexError):
                # Version parsing failed, but context created - assume compatible
                pass

            # Check max texture size
            max_texture = ctx.info.get('GL_MAX_TEXTURE_SIZE', 0)
            if max_texture < GPU_MIN_TEXTURE_SIZE:
                self.gpu_error = f"Max texture {max_texture} < required {GPU_MIN_TEXTURE_SIZE}"
                ctx.release()
                return

            # Success
            self.gpu_enabled = True
            self.gpu_error = None

            # Clean up test context (actual context created in distortion_system)
            ctx.release()

            print(f"[GPU] ModernGL initialized: {self.gpu_renderer}")
            print(f"[GPU] OpenGL version: {self.gpu_version}")

        except ImportError:
            self.gpu_error = "ModernGL not installed"
        except Exception as e:
            self.gpu_error = f"GPU init failed: {str(e)}"

    def record_frame(self, frame_time_ms):
        """
        Record frame time and check for auto-throttle breach.
        TRIAGE-004: Sample RAM usage at 2Hz (every 0.5s).

        Args:
            frame_time_ms: Total frame time in milliseconds

        Returns:
            bool: True if debug visuals should remain enabled
        """
        self.frame_times.append(frame_time_ms)

        # TRIAGE-004: Sample RAM at 2Hz
        current_time = time.time()
        if current_time - self.last_ram_sample_time >= self.ram_sample_interval:
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                self.ram_usage_mb = process.memory_info().rss / (1024 * 1024)  # Convert to MB
            self.last_ram_sample_time = current_time

        # Check breach condition (>14ms)
        if frame_time_ms > THROTTLE_THRESHOLD_MS:
            self.breach_count += 1
        else:
            self.breach_count = 0  # Reset on good frame

        # Auto-throttle: 5 consecutive breaches
        if self.breach_count >= 5 and self.debug_enabled:
            self.debug_enabled = False
            print(f"[PERF] Auto-throttle engaged: {self.breach_count} frames >{THROTTLE_THRESHOLD_MS}ms")
            print(f"[PERF] Debug visuals disabled to protect performance budget")

        return self.debug_enabled

    def get_avg_frame_time(self):
        """Get average frame time from recent window."""
        if not self.frame_times:
            return 0.0
        return sum(self.frame_times) / len(self.frame_times)

    def get_gpu_status_text(self):
        """
        Get GPU status for debug overlay.
        TRIAGE-004: Include GPU time, RAM usage, and texture memory.

        Returns:
            str: Status line for overlay (e.g., "GPU: ENABLED | Time: 0.2ms | RAM: 125MB")
        """
        if self.gpu_enabled:
            gpu_str = f"GPU: ENABLED | Time: {self.last_gpu_time_ms:.1f}ms"
        else:
            gpu_str = f"GPU: FALLBACK ({self.gpu_error or 'unavailable'})"

        # Add RAM usage if available
        if PSUTIL_AVAILABLE and self.ram_usage_mb > 0:
            gpu_str += f" | RAM: {self.ram_usage_mb:.0f}MB"

        return gpu_str

    def record_gpu_time(self, gpu_time_ms):
        """Record GPU shader execution time."""
        self.last_gpu_time_ms = gpu_time_ms

        # Warn if GPU exceeds budget
        if gpu_time_ms > GPU_SHADER_BUDGET_MS:
            print(f"[WARN] GPU shader {gpu_time_ms:.2f}ms exceeds {GPU_SHADER_BUDGET_MS}ms budget")

    def reset_throttle(self):
        """Manually re-enable debug visuals (e.g., user override)."""
        self.debug_enabled = True
        self.breach_count = 0
        print("[PERF] Debug visuals manually re-enabled")
