"""
APIS-OVERSEER Debug Visuals System (Phase 6)

Per Architect Spec [ARCH-SDL-PHASE6-002]:
- ModernGL standalone context for GPU shaders
- CPU-side vectorized halos and vignettes
- Auto-throttle protection (14ms breach → disable)
- ≤1.0ms total debug budget

Modules:
- performance_monitor: GPU detection, frame time tracking, auto-throttle
- distortion_system: Fragment shader for pheromone stress shimmer
- halo_system: Vectorized bee stress halos (Surface.blits)
- vignette_system: Static radial gradient overlay
"""

from .performance_monitor import PerformanceMonitor
from .distortion_system import DistortionSystem
from .halo_system import HaloSystem
from .vignette_system import VignetteSystem

__version__ = "6.0.0"
__all__ = ["PerformanceMonitor", "DistortionSystem", "HaloSystem", "VignetteSystem"]
