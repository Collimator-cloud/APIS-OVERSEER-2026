"""
APIS-OVERSEER GPU Pre-Check Utility
Step 0 verification before ModernGL installation

This script uses only standard library (ctypes) to detect OpenGL driver support
without requiring any external dependencies.

Per Architect Spec [ARCH-SDL-PHASE6-002]:
- Detect opengl32.dll presence (Windows)
- Query OpenGL version if possible
- Report READY/NOT READY status for ModernGL installation
"""

import sys
import ctypes
import ctypes.util
from ctypes import wintypes

def check_opengl_driver():
    """
    Check if OpenGL drivers are available on Windows.

    Returns:
        tuple: (success: bool, version_string: str, message: str)
    """
    try:
        # Attempt to load opengl32.dll
        opengl_lib = ctypes.util.find_library('opengl32')

        if not opengl_lib:
            return False, "N/A", "opengl32.dll not found in system PATH"

        # Try to load the library
        try:
            gl = ctypes.WinDLL('opengl32')
        except OSError as e:
            return False, "N/A", f"Failed to load opengl32.dll: {e}"

        # Basic presence check passed
        # Note: Full version detection requires a GL context, which we can't create
        # without pygame/GLFW/etc. So we only verify the DLL exists.

        return True, "Unknown (no context)", "opengl32.dll present and loadable"

    except Exception as e:
        return False, "N/A", f"Unexpected error during GL detection: {e}"


def check_pygame_gl_context():
    """
    Attempt to create a minimal pygame OpenGL context to query version.
    Only runs if pygame is already installed.

    Returns:
        tuple: (success: bool, version_string: str)
    """
    try:
        import pygame
        from pygame.locals import OPENGL, DOUBLEBUF

        # Initialize pygame with hidden window
        pygame.init()
        pygame.display.set_mode((1, 1), OPENGL | DOUBLEBUF)

        # Try to import OpenGL (if pyopengl is installed)
        try:
            from OpenGL.GL import glGetString, GL_VERSION
            version = glGetString(GL_VERSION)
            if version:
                version_str = version.decode('utf-8')
                pygame.quit()
                return True, version_str
        except ImportError:
            # PyOpenGL not installed, but pygame GL context works
            pygame.quit()
            return True, "Context created (PyOpenGL not available for version query)"

        pygame.quit()
        return True, "Context created but version query failed"

    except ImportError:
        return False, "pygame not installed"
    except Exception as e:
        try:
            pygame.quit()
        except:
            pass
        return False, f"Context creation failed: {e}"


def main():
    """
    Main pre-check execution.
    Reports hardware readiness for ModernGL installation.
    """
    print("=" * 80)
    print("APIS-OVERSEER Phase 6 GPU Pre-Check (Step 0)")
    print("=" * 80)
    print()

    # Step 1: Check basic OpenGL driver presence
    print("[1/2] Checking OpenGL driver availability...")
    driver_ok, driver_version, driver_msg = check_opengl_driver()

    if driver_ok:
        print(f"[OK] OpenGL Driver: {driver_msg}")
        print(f"     Version: {driver_version}")
    else:
        print(f"[FAIL] OpenGL Driver: {driver_msg}")
        print()
        print("=" * 80)
        print("RESULT: Hardware NOT READY for ModernGL")
        print("=" * 80)
        print()
        print("RECOMMENDATION:")
        print("  - Update your graphics drivers from manufacturer website")
        print("  - Intel: https://www.intel.com/content/www/us/en/download-center/home.html")
        print("  - NVIDIA: https://www.nvidia.com/Download/index.aspx")
        print("  - AMD: https://www.amd.com/en/support")
        print()
        return 1

    print()

    # Step 2: Attempt to create GL context (optional, requires pygame)
    print("[2/2] Attempting OpenGL context creation (optional)...")
    context_ok, context_version = check_pygame_gl_context()

    if context_ok:
        print(f"[OK] OpenGL Context: {context_version}")

        # Parse version if possible
        try:
            if "." in context_version:
                major, minor = context_version.split(".")[:2]
                major_ver = int(major)
                minor_ver = int(minor.split()[0])  # Handle "3.3 Mesa" etc

                if major_ver >= 3 and minor_ver >= 3:
                    print(f"[OK] Version Check: OpenGL {major_ver}.{minor_ver} >= 3.3 (ModernGL compatible)")
                elif major_ver >= 3:
                    print(f"[WARN] Version Check: OpenGL {major_ver}.{minor_ver} (ModernGL requires 3.3+)")
                    print("       ModernGL may work with reduced feature set")
                else:
                    print(f"[FAIL] Version Check: OpenGL {major_ver}.{minor_ver} < 3.3 (ModernGL incompatible)")
                    print()
                    print("=" * 80)
                    print("RESULT: Hardware NOT READY for ModernGL")
                    print("=" * 80)
                    print()
                    print("Your GPU supports OpenGL but the version is too old.")
                    print("ModernGL requires OpenGL 3.3 or higher.")
                    print()
                    return 1
        except (ValueError, IndexError):
            print("[WARN] Version parsing failed, assuming compatibility")
    else:
        print(f"[WARN] OpenGL Context: {context_version}")
        print("       (This is OK - context creation will be tested after ModernGL install)")

    print()
    print("=" * 80)
    print("RESULT: Hardware READY for ModernGL")
    print("=" * 80)
    print()
    print("NEXT STEP:")
    print("  Run the following command to install ModernGL:")
    print()
    print("  pip install moderngl")
    print()
    print("  After installation, the simulation will automatically detect GPU capabilities.")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
