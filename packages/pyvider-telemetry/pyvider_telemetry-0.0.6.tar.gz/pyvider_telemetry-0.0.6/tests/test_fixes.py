#
# test_fixes.py
#
"""
Test script to verify all lazy initialization fixes work correctly.
"""
import json
import os
import sys
import threading
import time
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))


def test_lazy_setup_flags():
    """Test that lazy setup flags are set correctly."""
    print("=== Test 1: Lazy Setup Flags ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()
    
    from pyvider.telemetry.logger.base import _LAZY_SETUP_DONE, _LAZY_SETUP_ERROR, _LAZY_SETUP_IN_PROGRESS
    print(f"Initial state - DONE: {_LAZY_SETUP_DONE}, ERROR: {_LAZY_SETUP_ERROR}, IN_PROGRESS: {_LAZY_SETUP_IN_PROGRESS}")
    
    from pyvider.telemetry import logger
    logger.info("Trigger lazy setup")
    
    from pyvider.telemetry.logger.base import _LAZY_SETUP_DONE, _LAZY_SETUP_ERROR, _LAZY_SETUP_IN_PROGRESS
    print(f"After logging - DONE: {_LAZY_SETUP_DONE}, ERROR: {_LAZY_SETUP_ERROR}, IN_PROGRESS: {_LAZY_SETUP_IN_PROGRESS}")
    
    if _LAZY_SETUP_DONE and _LAZY_SETUP_ERROR is None and not _LAZY_SETUP_IN_PROGRESS:
        print("✅ Lazy setup flags work correctly")
        return True
    else:
        print("❌ Lazy setup flags not set correctly")
        return False


def test_service_name_no_emoji():
    """Test service name injection without emoji prefix for JSON format."""
    print("\n=== Test 2: Service Name Without Emoji (JSON) ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing, _set_log_stream_for_testing
    reset_pyvider_setup_for_testing()
    
    # Set environment to disable emojis for JSON format
    os.environ["PYVIDER_SERVICE_NAME"] = "test-service"
    os.environ["PYVIDER_LOG_CONSOLE_FORMATTER"] = "json"
    os.environ["PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED"] = "false"
    os.environ["PYVIDER_LOG_DAS_EMOJI_ENABLED"] = "false"
    
    # Capture output
    import io
    captured_output = io.StringIO()
    _set_log_stream_for_testing(captured_output)
    
    try:
        from pyvider.telemetry import logger
        logger.info("Message with service name")
        
        output = captured_output.getvalue()
        lines = [line for line in output.strip().splitlines() if line.strip() and not line.startswith("[")]
        
        if lines:
            log_data = json.loads(lines[0])
            expected_event = "Message with service name"
            actual_event = log_data.get("event", "")
            
            print(f"Expected: {expected_event}")
            print(f"Actual: {actual_event}")
            
            if actual_event == expected_event and log_data.get("service_name") == "test-service":
                print("✅ Service name injection without emoji works")
                return True
            else:
                print("❌ Service name injection test failed")
                return False
        else:
            print("❌ No log output found")
            return False
    finally:
        _set_log_stream_for_testing(None)
        # Clean up environment
        for key in ["PYVIDER_SERVICE_NAME", "PYVIDER_LOG_CONSOLE_FORMATTER", 
                   "PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED", "PYVIDER_LOG_DAS_EMOJI_ENABLED"]:
            os.environ.pop(key, None)


def test_das_emoji_register_action():
    """Test that register action has proper emoji mapping."""
    print("\n=== Test 3: DAS Emoji Register Action ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing, _set_log_stream_for_testing
    reset_pyvider_setup_for_testing()
    
    # Enable DAS emojis
    os.environ["PYVIDER_LOG_DAS_EMOJI_ENABLED"] = "true"
    os.environ["PYVIDER_LOG_CONSOLE_FORMATTER"] = "key_value"
    
    import io
    captured_output = io.StringIO()
    _set_log_stream_for_testing(captured_output)
    
    try:
        from pyvider.telemetry import logger
        logger.info(
            "User registration processed",
            domain="user",
            action="register",
            status="success"
        )
        
        output = captured_output.getvalue()
        print(f"Output: {output}")
        
        # Should contain [👤][⚙️][✅] - user, register (⚙️), success
        if "[👤][⚙️][✅]" in output:
            print("✅ DAS emoji register action works")
            return True
        else:
            print("❌ DAS emoji register action failed")
            print(f"Expected [👤][⚙️][✅] in output")
            return False
    finally:
        _set_log_stream_for_testing(None)
        for key in ["PYVIDER_LOG_DAS_EMOJI_ENABLED", "PYVIDER_LOG_CONSOLE_FORMATTER"]:
            os.environ.pop(key, None)


def test_thread_safety():
    """Test thread safety of lazy initialization."""
    print("\n=== Test 4: Thread Safety ===")
    
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()
    
    results = []
    exceptions = []
    
    def worker_thread(worker_id):
        try:
            from pyvider.telemetry import logger
            logger.info(f"Thread {worker_id} message")
            results.append(True)
        except Exception as e:
            exceptions.append(e)
            results.append(False)
    
    # Create multiple threads
    threads = []
    thread_count = 10
    
    for i in range(thread_count):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join(timeout=5.0)
    
    if len(exceptions) == 0 and len(results) == thread_count and all(results):
        print("✅ Thread safety test passed")
        return True
    else:
        print(f"❌ Thread safety test failed - Exceptions: {len(exceptions)}, Results: {len(results)}/{thread_count}")
        return False


def test_get_safe_stderr():
    """Test that _get_safe_stderr function exists and works."""
    print("\n=== Test 5: Safe Stderr Function ===")
    
    try:
        from pyvider.telemetry.logger.base import _get_safe_stderr
        stderr = _get_safe_stderr()
        
        if hasattr(stderr, 'write'):
            print("✅ _get_safe_stderr function works")
            return True
        else:
            print("❌ _get_safe_stderr returned invalid stream")
            return False
    except ImportError:
        print("❌ _get_safe_stderr function not found")
        return False


def test_emoji_matrix_defaults():
    """Test emoji matrix has correct default mappings."""
    print("\n=== Test 6: Emoji Matrix Defaults ===")
    
    from pyvider.telemetry.logger.emoji_matrix import PRIMARY_EMOJI, SECONDARY_EMOJI, TERTIARY_EMOJI
    
    # Check that register action exists
    if "register" in SECONDARY_EMOJI:
        register_emoji = SECONDARY_EMOJI["register"]
        print(f"Register action emoji: {register_emoji}")
        
        # Check default emojis match test expectations
        expected_defaults = {
            "domain_default": PRIMARY_EMOJI.get("default", "❓"),
            "action_default": SECONDARY_EMOJI.get("default", "⚙️"), 
            "status_default": TERTIARY_EMOJI.get("default", "➡️")
        }
        
        print(f"Default emojis: {expected_defaults}")
        
        if (expected_defaults["domain_default"] == "❓" and 
            expected_defaults["action_default"] == "⚙️" and 
            expected_defaults["status_default"] == "➡️"):
            print("✅ Emoji matrix defaults are correct")
            return True
        else:
            print("❌ Emoji matrix defaults are incorrect")
            return False
    else:
        print("❌ Register action not found in emoji matrix")
        return False


def main():
    """Run all test fixes."""
    print("🧪 Testing Lazy Initialization Fixes")
    print("=" * 50)
    
    tests = [
        test_lazy_setup_flags,
        test_service_name_no_emoji,
        test_das_emoji_register_action,
        test_thread_safety,
        test_get_safe_stderr,
        test_emoji_matrix_defaults,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests PASSED! Fixes are working correctly.")
    else:
        print("💥 Some tests FAILED. Review the output above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# 🧪✅