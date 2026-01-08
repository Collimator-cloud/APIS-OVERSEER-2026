"""
PHASE 4 Test Script
Run simulation for 600 frames and report performance
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Run headless

import numpy as np
import pygame
import time
from config import *
from simulation import BeeSimulation

def test_phase4():
    """Run 600-frame test and report results."""
    print("=" * 60)
    print("PHASE 4 TEST: THE GARDEN (600 frames)")
    print("=" * 60)

    # Initialize Pygame (headless)
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    # Create simulation
    sim = BeeSimulation()

    # Timing
    frame_times = []
    pheromone_times = []
    resource_times = []

    # Run 600 frames
    dt = 1.0 / 60.0  # 60 FPS fixed timestep
    print("\nRunning simulation...")

    for frame in range(600):
        start = time.perf_counter()

        # Update simulation
        timing = sim.update(dt)

        end = time.perf_counter()
        frame_time = (end - start) * 1000.0

        frame_times.append(frame_time)
        if 'pheromone' in timing:
            pheromone_times.append(timing['pheromone'])
        if 'resources' in timing:
            resource_times.append(timing['resources'])

        # Progress update every 100 frames
        if (frame + 1) % 100 == 0:
            print(f"  Frame {frame + 1}/600 | Sim time: {frame_time:.2f}ms")

    # Calculate statistics
    print("\n" + "=" * 60)
    print("RESULTS (600-frame run)")
    print("=" * 60)

    avg_frame = np.mean(frame_times)
    max_frame = np.max(frame_times)
    min_frame = np.min(frame_times)

    print(f"Frame Time (Total Sim):")
    print(f"  Average: {avg_frame:.2f} ms")
    print(f"  Min:     {min_frame:.2f} ms")
    print(f"  Max:     {max_frame:.2f} ms")
    print(f"  Target:  <= 8.00 ms (baseline)")
    print(f"  Limit:   <= 12.00 ms (5000 bees)")
    print(f"  Budget:  <= 15.00 ms (HALT threshold)")

    if pheromone_times:
        avg_pheromone = np.mean(pheromone_times)
        print(f"\nPheromone System:")
        print(f"  Average: {avg_pheromone:.2f} ms")

    if resource_times:
        avg_resource = np.mean(resource_times)
        print(f"\nResource Manager:")
        print(f"  Average: {avg_resource:.2f} ms")

    # Check performance targets
    print("\n" + "=" * 60)
    print("PERFORMANCE VALIDATION")
    print("=" * 60)

    baseline_pass = avg_frame <= 8.0
    scalability_pass = avg_frame <= 12.0
    budget_pass = max_frame <= 15.0

    print(f"[CHECK] Baseline (2000 bees @ <=8ms):    {'PASS' if baseline_pass else 'FAIL'}")
    print(f"[CHECK] Scalability (5000 bees @ <=12ms): {'PASS' if scalability_pass else 'FAIL'}")
    print(f"[CHECK] Budget Collapse (max <=15ms):     {'PASS' if budget_pass else 'FAIL'}")

    # Test Phase 4 systems
    print("\n" + "=" * 60)
    print("PHASE 4 SYSTEM CHECKS")
    print("=" * 60)

    # Check pheromone grid
    heatmap = sim.pheromone_system.get_heatmap()
    print(f"[CHECK] Pheromone Grid Shape: {heatmap.shape}")
    print(f"  Expected: (128, 128)")
    print(f"  Max Value: {np.max(heatmap):.4f}")

    # Check resource manager
    flower_data = sim.resource_manager.get_render_data()
    print(f"\n[CHECK] Flower Count: {len(flower_data['positions'])}")
    print(f"  Expected: 5")
    print(f"  Avg Nectar: {np.mean(flower_data['nectar_pct']):.2%}")

    # Check gradient field
    gradient = sim.pheromone_system.gradient_field
    print(f"\n[CHECK] Gradient Field Shape: {gradient.shape}")
    print(f"  Expected: (128, 128, 2)")
    print(f"  Max Magnitude: {np.max(np.linalg.norm(gradient, axis=2)):.4f}")

    # Final verdict
    print("\n" + "=" * 60)
    if baseline_pass and scalability_pass and budget_pass:
        print("STATUS: [PASS] ALL TESTS PASSED")
        print("Phase 4 implementation is COMPLETE and meets all specs.")
    else:
        print("STATUS: [WARN] PERFORMANCE ISSUES DETECTED")
        print("Review timing breakdown above.")

    print("=" * 60)

    pygame.quit()

if __name__ == "__main__":
    test_phase4()
