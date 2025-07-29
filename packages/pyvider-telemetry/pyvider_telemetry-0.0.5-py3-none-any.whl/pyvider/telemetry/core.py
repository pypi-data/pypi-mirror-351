#
# core.py
#
"""
Pyvider Telemetry Core Setup (structlog-based).

This module contains the core logic for initializing and configuring the
`structlog` based logging system for Pyvider. It handles processor chains,
log level filtering, formatter selection, and global state management for telemetry.

This module is the heart of the telemetry system, responsible for:
- Setting up and configuring structlog with appropriate processors
- Managing thread-safe initialization and shutdown
- Building processor chains based on configuration
- Handling formatter selection (JSON vs key-value)
- Managing global state and configuration lifecycle
"""
import logging as stdlib_logging # Renamed from json to logging
import os # Kept os
import sys # Kept sys
import threading # Kept threading
from typing import ( # Kept typing imports
    TYPE_CHECKING,
    Any,
    # Protocol, # Protocol might not be needed if FormatterProcessor is not used here anymore
    TextIO,
)

import structlog # Kept structlog

# Import new processor list builder functions from config
from pyvider.telemetry.config import (
    TelemetryConfig,
    _build_core_processors_list, # New import
    _build_formatter_processors_list, # New import
    # LoggingConfig, LogLevelStr are likely used by TelemetryConfig, so keep if needed implicitly
    # or if TelemetryConfig methods here still need them directly.
    # For now, assuming TelemetryConfig encapsulates them enough for core.py's direct needs.
)
from pyvider.telemetry.logger import base as logger_base_module
# Custom processors might still be needed if any are used directly here, beyond what config.py handles.
# For now, assuming they are fully handled by config.py's builder functions.
# from pyvider.telemetry.logger.custom_processors import (
#     TRACE_LEVEL_NUM, # This was for _LEVEL_TO_NUMERIC, now in config.py
#     StructlogProcessor, # This was for type hints of processor functions, now in config.py
#     add_das_emoji_prefix,
#     add_log_level_custom,
#     add_logger_name_emoji_prefix,
#     filter_by_level_custom,
# )

if TYPE_CHECKING:
    pass

# Module-level constants for logging infrastructure
_CORE_SETUP_LOGGER_NAME = "pyvider.telemetry.core_setup"
_PYVIDER_LOG_STREAM: TextIO = sys.stderr

def _set_log_stream_for_testing(stream: TextIO | None) -> None:  # pragma: no cover
    """
    Sets the global log stream, primarily for testing purposes.

    This function allows tests to redirect log output to capture and verify
    logging behavior without affecting stderr.

    Args:
        stream: The stream to use for logging output, or None to reset to stderr.

    Note:
        This is intended for testing only and should not be used in production code.
    """
    global _PYVIDER_LOG_STREAM
    _PYVIDER_LOG_STREAM = stream if stream is not None else sys.stderr

def _create_core_setup_logger(globally_disabled: bool = False) -> stdlib_logging.Logger:
    """
    Creates and configures a standard library logger for core setup messages.

    This logger is used specifically for telemetry system setup and teardown
    messages, separate from the main structlog-based logging system.

    Args:
        globally_disabled: If True, uses NullHandler to suppress all output.

    Returns:
        Configured stdlib logger for setup diagnostics.

    Note:
        This logger uses the standard library logging module to avoid
        circular dependencies during system initialization.
    """
    logger = stdlib_logging.getLogger(_CORE_SETUP_LOGGER_NAME)

    # Ensure handlers are (re)configured to use the current _PYVIDER_LOG_STREAM (sys.stderr by default)
    # This is important for capsys in tests.
    for h in list(logger.handlers): # Remove any existing handlers
        logger.removeHandler(h)
        try:
            if h.stream not in (sys.stdout, sys.stderr, _PYVIDER_LOG_STREAM): # Avoid closing std streams
                 h.close()
        except Exception: # nosemgrep: generic-exception-handling
            pass

    # Configure new handler
    handler: stdlib_logging.Handler
    if globally_disabled:
        handler = stdlib_logging.NullHandler()
    else:
        # Always use the current sys.stderr for this stdlib logger for capsys compatibility
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

# Global state management for setup process
_core_setup_logger = _create_core_setup_logger()
_PYVIDER_SETUP_LOCK = threading.Lock()

# _LEVEL_TO_NUMERIC and FormatterProcessor Protocol are removed as they are now in config.py
# All _create_* processor helper functions are removed as they are now in config.py
# _build_core_processor_chain is removed as it's now _build_core_processors_list in config.py
# _create_formatter_processors is removed as it's now _build_formatter_processors_list in config.py


def _build_complete_processor_chain(config: TelemetryConfig) -> list[Any]:
    """
    Builds the complete processor chain including formatters.
    This function now delegates to helper functions imported from `config.py`.
    It also handles logging the choice of formatter.

    Args:
        config: Complete telemetry configuration.

    Returns:
        Complete ordered list of processors including formatters.
    """
    # Get core processors from config.py
    core_processors = _build_core_processors_list(config)

    output_stream = _PYVIDER_LOG_STREAM # _PYVIDER_LOG_STREAM is still managed in core.py

    # Get formatter processors from config.py
    # Note: config.logging is passed as LoggingConfig is expected by _build_formatter_processors_list
    formatter_processors = _build_formatter_processors_list(config.logging, output_stream)

    # Log the choice of formatter (this logging was previously inside _create_formatter_processors)
    if config.logging.console_formatter == "json":
        _core_setup_logger.info("📝➡️🎨 Configured JSON renderer.")
    elif config.logging.console_formatter == "key_value":
        _core_setup_logger.info("📝➡️🎨 Configured Key-Value (ConsoleRenderer).")
    else:
        # This case should ideally be handled by config validation, but as a fallback:
        _core_setup_logger.warning(
            f"Unknown formatter '{config.logging.console_formatter}' was processed."
            " Defaulted to key-value. This indicates a potential issue in config validation or propagation."
        )


    # Combine core and formatter processors
    return core_processors + formatter_processors

def _apply_structlog_configuration(processors: list[Any]) -> None:
    """
    Applies the processor chain to structlog configuration.

    This function performs the final structlog configuration with the
    provided processor chain.

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

    This function orchestrates the structlog configuration by:
    1. Building the complete processor chain
    2. Applying the configuration to structlog

    Args:
        config: Complete telemetry configuration.

    Raises:
        Exception: If structlog configuration fails.

    Note:
        This function has global side effects and should only be called
        during system initialization with proper locking.
    """
    processors = _build_complete_processor_chain(config)
    _apply_structlog_configuration(processors)

def _handle_globally_disabled_setup() -> None:
    """
    Handles the setup process when telemetry is globally disabled.

    When telemetry is disabled, we still need to:
    1. Log a notification about the disabled state
    2. Configure structlog with minimal processors to avoid errors

    This ensures that logging calls don't fail even when disabled,
    they just produce no output.
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
        logger_factory=structlog.ReturnLoggerFactory()
    )

def reset_pyvider_setup_for_testing() -> None:
    """
    Resets structlog defaults and Pyvider logger state for isolated testing.

    This function ensures that tests do not interfere with each other by:
    1. Resetting structlog to default configuration
    2. Clearing Pyvider logger state
    3. Restoring default log stream
    4. Recreating setup logger

    Note:
        This is crucial for test isolation and should be called before
        each test that configures telemetry.
    """
    global _core_setup_logger, _PYVIDER_LOG_STREAM

    with _PYVIDER_SETUP_LOCK:
        structlog.reset_defaults()
        logger_base_module.logger._is_configured_by_setup = False
        logger_base_module.logger._active_config = None
        _PYVIDER_LOG_STREAM = sys.stderr
        _core_setup_logger = _create_core_setup_logger()

def setup_telemetry(config: TelemetryConfig | None = None) -> None:
    """
    Initializes and configures the Pyvider telemetry system (structlog).

    This is the main entry point for setting up logging. It configures structlog
    processors, formatters, and log levels based on the provided configuration
    or environment variables if no configuration is given.

    The setup process includes:
    1. Thread-safe initialization with locking
    2. Configuration loading (programmatic or environment-based)
    3. Processor chain building and configuration
    4. Logger state management

    Args:
        config: An optional TelemetryConfig instance. If None, configuration
                is loaded from environment variables via TelemetryConfig.from_env().

    Thread Safety:
        This function is thread-safe and uses internal locking to prevent
        concurrent setup operations. Multiple calls are safe but only the
        first call will perform actual configuration.

    Example:
        >>> # Simple setup with defaults
        >>> setup_telemetry()

        >>> # Setup with custom configuration
        >>> config = TelemetryConfig(service_name="my-service")
        >>> setup_telemetry(config)
    """
    global _PYVIDER_LOG_STREAM, _core_setup_logger

    with _PYVIDER_SETUP_LOCK:
        # Reset state to ensure clean initialization
        structlog.reset_defaults()
        logger_base_module.logger._is_configured_by_setup = False
        logger_base_module.logger._active_config = None

        # Load configuration from parameter or environment
        current_config = config if config is not None else TelemetryConfig.from_env()
        _core_setup_logger = _create_core_setup_logger(
            globally_disabled=current_config.globally_disabled
        )

        # Log setup start (unless globally disabled)
        if not current_config.globally_disabled:
            _core_setup_logger.info("⚙️➡️🚀 Starting Pyvider (structlog) setup...")

        # Handle the two main setup paths
        match current_config.globally_disabled:
            case True:
                _handle_globally_disabled_setup()
            case False:
                _configure_structlog_output(current_config)

        # Mark as configured and store active configuration
        logger_base_module.logger._is_configured_by_setup = True
        logger_base_module.logger._active_config = current_config

        if not current_config.globally_disabled:
            _core_setup_logger.info("⚙️➡️✅ Pyvider (structlog) setup process completed.")

async def shutdown_pyvider_telemetry(timeout_millis: int = 5000) -> None:  # pragma: no cover
    """
    Performs shutdown procedures for Pyvider telemetry.

    Currently, this primarily logs a shutdown message and performs cleanup.
    In the future, it might be used to flush telemetry buffers or release resources.

    Args:
        timeout_millis: A timeout in milliseconds for shutdown operations.
                        Currently unused but reserved for future buffer flushing.

    Thread Safety:
        This function is async-safe and does not modify global state.
        It can be safely called from async contexts.

    Note:
        This function is async to support future enhancements like
        buffer flushing or network resource cleanup.

    Example:
        >>> # In async context
        >>> await shutdown_pyvider_telemetry()

        >>> # In sync context
        >>> import asyncio
        >>> asyncio.run(shutdown_pyvider_telemetry())
    """
    _core_setup_logger.info("🔌➡️🏁 Pyvider telemetry shutdown called.")

# 🐍🛠️