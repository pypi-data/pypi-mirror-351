#
# test_lazy_setup_flag.py
#
"""
Test to verify the lazy setup done flag is set correctly.
"""
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

def test_lazy_setup_done_flag():
    """Test that the lazy setup done flag is set correctly."""
    print("=== Testing Lazy Setup Done Flag ===")

    # Reset state
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()

    # Check initial state
    from pyvider.telemetry.logger.base import _LAZY_SETUP_DONE, _LAZY_SETUP_ERROR, _LAZY_SETUP_IN_PROGRESS
    print(f"Initial state:")
    print(f"  _LAZY_SETUP_DONE: {_LAZY_SETUP_DONE}")
    print(f"  _LAZY_SETUP_ERROR: {_LAZY_SETUP_ERROR}")
    print(f"  _LAZY_SETUP_IN_PROGRESS: {_LAZY_SETUP_IN_PROGRESS}")

    # Trigger lazy setup
    from pyvider.telemetry import logger
    print(f"\nLogging message to trigger lazy setup...")
    logger.info("Test message to trigger lazy setup")

    # Check state after logging
    from pyvider.telemetry.logger.base import _LAZY_SETUP_DONE, _LAZY_SETUP_ERROR, _LAZY_SETUP_IN_PROGRESS
    print(f"After logging:")
    print(f"  _LAZY_SETUP_DONE: {_LAZY_SETUP_DONE}")
    print(f"  _LAZY_SETUP_ERROR: {_LAZY_SETUP_ERROR}")
    print(f"  _LAZY_SETUP_IN_PROGRESS: {_LAZY_SETUP_IN_PROGRESS}")

    # Verify expected state
    if _LAZY_SETUP_DONE and _LAZY_SETUP_ERROR is None and not _LAZY_SETUP_IN_PROGRESS:
        print("✅ Lazy setup flags are correct!")
        return True
    else:
        print("❌ Lazy setup flags are incorrect!")
        return False

def test_recursive_logging_protection():
    """Test that recursive logging doesn't cause infinite loops."""
    print("\n=== Testing Recursive Logging Protection ===")

    # Reset state
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()

    # Create a custom setup function that logs during setup
    def recursive_setup(self):
        print("In recursive setup - this should trigger emergency fallback")
        from pyvider.telemetry import logger as global_logger
        global_logger.debug("Logging during setup - should use emergency fallback")
        # Don't call the original setup to avoid actual recursion
        return

    # Patch the setup method
    from unittest.mock import patch
    from pyvider.telemetry.logger.base import PyviderLogger

    with patch.object(PyviderLogger, '_perform_lazy_setup', recursive_setup):
        from pyvider.telemetry import logger
        print("Triggering recursive logging scenario...")

        try:
            logger.info("This should trigger recursive setup scenario")
            print("✅ Recursive logging handled without infinite loop!")
            return True
        except Exception as e:
            print(f"❌ Recursive logging failed: {e}")
            return False

if __name__ == "__main__":
    success1 = test_lazy_setup_done_flag()
    success2 = test_recursive_logging_protection()

    if success1 and success2:
        print("\n🎉 All lazy setup tests PASSED!")
    else:
        print("\n💥 Some lazy setup tests FAILED!")

# 🧪🔄
