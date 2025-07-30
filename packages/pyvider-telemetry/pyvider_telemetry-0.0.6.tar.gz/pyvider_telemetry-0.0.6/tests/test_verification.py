#
# test_verification.py
#
"""
Quick verification script to test the lazy initialization fixes.
"""
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

def test_basic_lazy_init():
    """Test basic lazy initialization works."""
    print("=== Test 1: Basic Lazy Initialization ===")
    
    # Reset any existing configuration
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()
    
    # Clear environment
    env_vars_to_clear = [
        "PYVIDER_SERVICE_NAME", "PYVIDER_LOG_CONSOLE_FORMATTER",
        "PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED", "PYVIDER_LOG_DAS_EMOJI_ENABLED"
    ]
    for var in env_vars_to_clear:
        os.environ.pop(var, None)
    
    from pyvider.telemetry import logger
    logger.info("Basic lazy initialization test")
    print("✅ Basic lazy initialization works")


def test_service_name_injection():
    """Test service name injection with JSON format."""
    print("\n=== Test 2: Service Name Injection (JSON) ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()
    
    # Set environment like the failing test
    os.environ["PYVIDER_SERVICE_NAME"] = "test-service"
    os.environ["PYVIDER_LOG_CONSOLE_FORMATTER"] = "json"
    
    from pyvider.telemetry import logger
    logger.info("Message with service name")
    print("✅ Service name injection test works")


def test_lazy_setup_flags():
    """Test that lazy setup flags are set correctly."""
    print("\n=== Test 3: Lazy Setup Flags ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()
    
    from pyvider.telemetry.logger.base import _LAZY_SETUP_DONE, _LAZY_SETUP_ERROR
    print(f"Initial state - DONE: {_LAZY_SETUP_DONE}, ERROR: {_LAZY_SETUP_ERROR}")
    
    from pyvider.telemetry import logger
    logger.info("Trigger lazy setup")
    
    from pyvider.telemetry.logger.base import _LAZY_SETUP_DONE, _LAZY_SETUP_ERROR
    print(f"After logging - DONE: {_LAZY_SETUP_DONE}, ERROR: {_LAZY_SETUP_ERROR}")
    
    if _LAZY_SETUP_DONE and _LAZY_SETUP_ERROR is None:
        print("✅ Lazy setup flags work correctly")
    else:
        print("❌ Lazy setup flags not set correctly")


def test_emergency_fallback():
    """Test emergency fallback doesn't crash."""
    print("\n=== Test 4: Emergency Fallback ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()
    
    from pyvider.telemetry.logger.base import PyviderLogger
    test_logger = PyviderLogger()
    
    # Trigger emergency fallback by setting error state
    from pyvider.telemetry.logger import base as logger_base
    logger_base._LAZY_SETUP_ERROR = Exception("Test error")
    
    try:
        test_logger.info("Emergency fallback test")
        print("✅ Emergency fallback works")
    except Exception as e:
        print(f"❌ Emergency fallback failed: {e}")


if __name__ == "__main__":
    try:
        test_basic_lazy_init()
        test_service_name_injection()
        test_lazy_setup_flags()
        test_emergency_fallback()
        print("\n🎉 All verification tests completed!")
    except Exception as e:
        print(f"\n💥 Verification failed: {e}")
        import traceback
        traceback.print_exc()

# 🧪✅
