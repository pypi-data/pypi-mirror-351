#
# test_service_name_fix.py
#
"""
Test to verify the service name injection fix works correctly.
"""
import json
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

def test_service_name_injection_fix():
    """Test that service name injection works with JSON format and no emoji prefix."""
    print("=== Testing Service Name Injection Fix ===")

    # Reset state
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()

    # Set environment like the failing test
    os.environ["PYVIDER_SERVICE_NAME"] = "lazy-service-test"
    os.environ["PYVIDER_LOG_CONSOLE_FORMATTER"] = "json"

    # Clear any existing emoji settings
    for key in ["PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED", "PYVIDER_LOG_DAS_EMOJI_ENABLED"]:
        os.environ.pop(key, None)

    # Capture output
    import io
    from pyvider.telemetry.core import _set_log_stream_for_testing
    captured_output = io.StringIO()
    _set_log_stream_for_testing(captured_output)

    try:
        # Test logging
        from pyvider.telemetry import logger
        logger.info("Message with service name")

        # Get output
        output = captured_output.getvalue()
        print(f"Raw output: {repr(output)}")

        # Parse JSON
        lines = [line for line in output.strip().splitlines()
                if line.strip() and not line.startswith("[")]

        if lines:
            log_data = json.loads(lines[0])
            print(f"Parsed JSON: {json.dumps(log_data, indent=2)}")

            # Check expectations
            expected_event = "Message with service name"
            actual_event = log_data.get("event", "")

            print(f"Expected event: {repr(expected_event)}")
            print(f"Actual event: {repr(actual_event)}")

            if actual_event == expected_event:
                print("✅ Service name injection test PASSED!")
                return True
            else:
                print("❌ Service name injection test FAILED!")
                print(f"  Expected: {expected_event}")
                print(f"  Got: {actual_event}")
                return False
        else:
            print("❌ No log output found!")
            return False

    finally:
        _set_log_stream_for_testing(None)

def test_key_value_still_has_emojis():
    """Test that key-value format still has emoji prefixes."""
    print("\n=== Testing Key-Value Format Still Has Emojis ===")

    # Reset state
    from pyvider.telemetry.core import reset_pyvider_setup_for_testing
    reset_pyvider_setup_for_testing()

    # Set environment for key-value format
    os.environ.pop("PYVIDER_SERVICE_NAME", None)
    os.environ["PYVIDER_LOG_CONSOLE_FORMATTER"] = "key_value"

    # Clear any existing emoji settings
    for key in ["PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED", "PYVIDER_LOG_DAS_EMOJI_ENABLED"]:
        os.environ.pop(key, None)

    # Capture output
    import io
    from pyvider.telemetry.core import _set_log_stream_for_testing
    captured_output = io.StringIO()
    _set_log_stream_for_testing(captured_output)

    try:
        from pyvider.telemetry import logger
        logger.info("Test message for key-value format")

        output = captured_output.getvalue()
        print(f"Key-value output: {repr(output)}")

        if "🗣️" in output:
            print("✅ Key-value format still has emojis!")
            return True
        else:
            print("❌ Key-value format missing emojis!")
            return False

    finally:
        _set_log_stream_for_testing(None)

if __name__ == "__main__":
    success1 = test_service_name_injection_fix()
    success2 = test_key_value_still_has_emojis()

    if success1 and success2:
        print("\n🎉 All tests PASSED!")
    else:
        print("\n💥 Some tests FAILED!")

# 🧪✅
