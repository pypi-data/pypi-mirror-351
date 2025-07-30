#
# core.py
#

import logging as stdlib_logging
import os
import sys
import threading
from typing import Any, TextIO

import structlog

from pyvider.telemetry.config import (
    TelemetryConfig,
    _build_core_processors_list,
    _build_formatter_processors_list,
)
from pyvider.telemetry.logger import base as logger_base_module

# Enhanced global state management
_PYVIDER_SETUP_LOCK = threading.Lock()
_PYVIDER_LOG_STREAM: TextIO = sys.stderr  # Always default to stderr
_CORE_SETUP_LOGGER_NAME = "pyvider.telemetry.core_setup"
_EXPLICIT_SETUP_DONE = False


def _get_safe_stderr() -> TextIO:
    """
    Returns a safe stderr stream, with fallback if stderr is not available.

    Returns:
        A TextIO stream that can be used for error output.
    """
    if hasattr(sys, 'stderr') and sys.stderr is not None:
        return sys.stderr
    else:
        # Fallback: create a no-op stream if stderr is not available
        import io
        return io.StringIO()


def _set_log_stream_for_testing(stream: TextIO | None) -> None:
    """
    Sets the global log stream, primarily for testing purposes.

    Args:
        stream: The stream to use for logging output, or None to reset to stderr.
    """
    global _PYVIDER_LOG_STREAM
    _PYVIDER_LOG_STREAM = stream if stream is not None else sys.stderr


def _ensure_stderr_default() -> None:
    """
    Ensures the default log stream is always stderr, never stdout.

    This function corrects any accidental assignment of stdout as the log stream.
    """
    global _PYVIDER_LOG_STREAM
    if _PYVIDER_LOG_STREAM is sys.stdout:
        _PYVIDER_LOG_STREAM = sys.stderr


def _create_failsafe_handler() -> stdlib_logging.Handler:
    """
    Creates a failsafe handler that always outputs to stderr.

    Used as a last resort if other configuration fails.

    Returns:
        A configured StreamHandler pointing to stderr.
    """
    handler = stdlib_logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        stdlib_logging.Formatter("[Pyvider Failsafe] %(levelname)s: %(message)s")
    )
    return handler


def _create_core_setup_logger(globally_disabled: bool = False) -> stdlib_logging.Logger:
    """
    Creates and configures a standard library logger for core setup messages.

    Args:
        globally_disabled: If True, uses NullHandler to suppress all output.

    Returns:
        Configured stdlib logger for setup diagnostics.
    """
    logger = stdlib_logging.getLogger(_CORE_SETUP_LOGGER_NAME)

    # Ensure handlers are (re)configured to use the current stderr
    for h in list(logger.handlers):
        logger.removeHandler(h)
        try:
            if h.stream not in (sys.stdout, sys.stderr, _PYVIDER_LOG_STREAM):
                h.close()
        except Exception:
            pass

    # Configure new handler
    handler: stdlib_logging.Handler
    if globally_disabled:
        handler = stdlib_logging.NullHandler()
    else:
        # Always use stderr for this stdlib logger
        handler = stdlib_logging.StreamHandler(sys.stderr)
        formatter = stdlib_logging.Formatter(
            "[Pyvider Setup] %(levelname)s (%(name)s): %(message)s"
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Set log level from environment with fallback
    level_str = os.getenv("PYVIDER_CORE_SETUP_LOG_LEVEL", "INFO").upper()
    level = getattr(stdlib_logging, level_str, stdlib_logging.INFO)
    logger.setLevel(level)
    logger.propagate = False

    return logger


# Global setup logger
_core_setup_logger = _create_core_setup_logger()


def _build_complete_processor_chain(config: TelemetryConfig) -> list[Any]:
    """
    Builds the complete processor chain including formatters.

    Args:
        config: Complete telemetry configuration.

    Returns:
        Complete ordered list of processors including formatters.
    """
    # Get core processors from config.py
    core_processors = _build_core_processors_list(config)

    output_stream = _PYVIDER_LOG_STREAM

    # Get formatter processors from config.py
    formatter_processors = _build_formatter_processors_list(config.logging, output_stream)

    # Log the choice of formatter
    if config.logging.console_formatter == "json":
        _core_setup_logger.info("📝➡️🎨 Configured JSON renderer.")
    elif config.logging.console_formatter == "key_value":
        _core_setup_logger.info("📝➡️🎨 Configured Key-Value (ConsoleRenderer).")
    else:
        _core_setup_logger.warning(
            f"Unknown formatter '{config.logging.console_formatter}' was processed. "
            "Defaulted to key-value. This indicates a potential issue in config validation."
        )

    # Combine core and formatter processors
    return core_processors + formatter_processors


def _apply_structlog_configuration(processors: list[Any]) -> None:
    """
    Applies the processor chain to structlog configuration.

    Args:
        processors: Complete list of processors to configure.
    """
    output_stream = _PYVIDER_LOG_STREAM

    # Configure structlog with our processor chain
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(file=output_stream),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )

    stream_name = 'sys.stderr' if output_stream == sys.stderr else 'custom stream (testing)'
    _core_setup_logger.info(
        f"📝➡️✅ structlog configured. Wrapper: BoundLogger. Output: {stream_name}."
    )


def _configure_structlog_output(config: TelemetryConfig) -> None:
    """
    Configures structlog with the complete processor chain and output settings.

    Args:
        config: Complete telemetry configuration.
    """
    processors = _build_complete_processor_chain(config)
    _apply_structlog_configuration(processors)


def _handle_globally_disabled_setup() -> None:
    """
    Handles the setup process when telemetry is globally disabled.
    """
    # Create temporary logger for disabled message
    temp_logger_name = f"{_CORE_SETUP_LOGGER_NAME}_temp_disabled_msg"
    temp_logger = stdlib_logging.getLogger(temp_logger_name)

    # Check if we need to configure this temporary logger
    needs_configuration = (
        not temp_logger.handlers or
        not any(
            isinstance(h, stdlib_logging.StreamHandler) and h.stream == sys.stderr
            for h in temp_logger.handlers
        )
    )

    if needs_configuration:
        # Clear and reconfigure
        for h in list(temp_logger.handlers):
            temp_logger.removeHandler(h)

        temp_handler = stdlib_logging.StreamHandler(sys.stderr)
        temp_formatter = stdlib_logging.Formatter(
            "[Pyvider Setup] %(levelname)s (%(name)s): %(message)s"
        )
        temp_handler.setFormatter(temp_formatter)
        temp_logger.addHandler(temp_handler)
        temp_logger.setLevel(stdlib_logging.INFO)
        temp_logger.propagate = False

    temp_logger.info("⚙️➡️🚫 Pyvider telemetry globally disabled.")

    # Configure minimal structlog setup to avoid errors
    structlog.configure(
        processors=[],
        logger_factory=structlog.ReturnLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def reset_pyvider_setup_for_testing() -> None:
    """
    Resets structlog defaults and Pyvider logger state for isolated testing.
    """
    global _PYVIDER_LOG_STREAM, _core_setup_logger, _EXPLICIT_SETUP_DONE

    with _PYVIDER_SETUP_LOCK:
        # Reset structlog
        structlog.reset_defaults()

        # Reset logger state
        logger_base_module.logger._is_configured_by_setup = False
        logger_base_module.logger._active_config = None

        # Reset lazy setup state - FIXED: Reset all flags including in-progress
        logger_base_module._LAZY_SETUP_DONE = False
        logger_base_module._LAZY_SETUP_ERROR = None
        if hasattr(logger_base_module, '_LAZY_SETUP_IN_PROGRESS'):
            logger_base_module._LAZY_SETUP_IN_PROGRESS = False  # ADDED: Reset in-progress flag if it exists

        # Reset stream and setup flags
        _PYVIDER_LOG_STREAM = sys.stderr
        _EXPLICIT_SETUP_DONE = False
        _core_setup_logger = _create_core_setup_logger()


def setup_telemetry(config: TelemetryConfig | None = None) -> None:
    """
    Enhanced setup_telemetry that works with lazy initialization.

    This function now coordinates with the lazy initialization system to ensure
    proper setup regardless of call order.

    Args:
        config: Optional TelemetryConfig instance.
    """
    global _PYVIDER_LOG_STREAM, _core_setup_logger, _EXPLICIT_SETUP_DONE

    with _PYVIDER_SETUP_LOCK:
        # Ensure stderr default
        _ensure_stderr_default()

        # Reset state for clean initialization
        structlog.reset_defaults()
        logger_base_module.logger._is_configured_by_setup = False
        logger_base_module.logger._active_config = None

        # Reset lazy setup state since we're doing explicit setup - FIXED: Reset all flags
        logger_base_module._LAZY_SETUP_DONE = False
        logger_base_module._LAZY_SETUP_ERROR = None
        if hasattr(logger_base_module, '_LAZY_SETUP_IN_PROGRESS'):
            logger_base_module._LAZY_SETUP_IN_PROGRESS = False  # ADDED: Reset in-progress flag if it exists

        # Load configuration
        current_config = config if config is not None else TelemetryConfig.from_env()

        # Create core setup logger
        _core_setup_logger = _create_core_setup_logger(
            globally_disabled=current_config.globally_disabled
        )

        # Log setup start (unless globally disabled)
        if not current_config.globally_disabled:
            _core_setup_logger.info("⚙️➡️🚀 Starting Pyvider (structlog) explicit setup...")

        # Configure based on disabled state
        if current_config.globally_disabled:
            _handle_globally_disabled_setup()
        else:
            _configure_structlog_output(current_config)

        # Mark as properly configured - FIXED: Set both explicit and lazy flags
        logger_base_module.logger._is_configured_by_setup = True
        logger_base_module.logger._active_config = current_config
        _EXPLICIT_SETUP_DONE = True

        # Also mark lazy setup as done to prevent future lazy initialization
        logger_base_module._LAZY_SETUP_DONE = True

        if not current_config.globally_disabled:
            _core_setup_logger.info("⚙️➡️✅ Pyvider (structlog) explicit setup completed.")


async def shutdown_pyvider_telemetry(timeout_millis: int = 5000) -> None:
    """
    Performs shutdown procedures for Pyvider telemetry.

    Args:
        timeout_millis: Timeout in milliseconds for shutdown operations.
    """
    _core_setup_logger.info("🔌➡️🏁 Pyvider telemetry shutdown called.")

# 🐍🛠️
