#
# config.py
#
"""
Configuration Models for Pyvider Telemetry (structlog-based).

This module defines the configuration objects used to set up and customize
the telemetry system, primarily focusing on logging behavior. It utilizes
the `attrs` library for creating structured and immutable configuration classes.

The configuration system supports:
- Environment variable-driven configuration
- Programmatic configuration with type safety
- Module-specific log level overrides
- Multiple output formats (JSON, key-value)
- Emoji customization options
- Service identification for multi-service environments
"""

import os
import sys
import logging as stdlib_logging
from typing import TYPE_CHECKING, Literal, Any, TextIO # Basic typing

from attrs import define, field # attrs needed early for @define

if TYPE_CHECKING:
    # Using string literal for self-reference to avoid circular import issues at runtime if not already.
    # Also, for types that might be forward-declared or complex.
    pass

# Define fundamental type aliases FIRST to break circular dependencies
LogLevelStr = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]
_VALID_LOG_LEVEL_TUPLE: tuple[LogLevelStr, ...] = (
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"
)
ConsoleFormatterStr = Literal["key_value", "json"]
_VALID_FORMATTER_TUPLE: tuple[ConsoleFormatterStr, ...] = ("key_value", "json")

# NOW import from custom_processors, structlog, and other libraries needed for constants/processor logic
import structlog
import json # For JSONRenderer for _config_create_json_formatter_processors
from pyvider.telemetry.logger.custom_processors import (
    StructlogProcessor,
    add_log_level_custom,
    filter_by_level_custom,
    add_logger_name_emoji_prefix,
    add_das_emoji_prefix,
    TRACE_LEVEL_NUM # For _LEVEL_TO_NUMERIC
)

# THEN define constants that depend on the above imports (like _LEVEL_TO_NUMERIC uses TRACE_LEVEL_NUM)
_LEVEL_TO_NUMERIC: dict[LogLevelStr, int] = {
    "CRITICAL": stdlib_logging.CRITICAL,
    "ERROR": stdlib_logging.ERROR,
    "WARNING": stdlib_logging.WARNING,
    "INFO": stdlib_logging.INFO,
    "DEBUG": stdlib_logging.DEBUG,
    "TRACE": TRACE_LEVEL_NUM, # This now uses the imported TRACE_LEVEL_NUM
    "NOTSET": stdlib_logging.NOTSET,
}

# Initialize the dedicated logger for configuration warnings.
# Handler is NOT added here; it will be added just-in-time.
config_warnings_logger = stdlib_logging.getLogger("pyvider.telemetry.config_warnings")

_config_warning_formatter = stdlib_logging.Formatter(
    "[Pyvider Config Warning] %(levelname)s (%(name)s): %(message)s"
)

def _ensure_config_logger_handler(logger: stdlib_logging.Logger) -> None:
    """
    Ensures the given logger has a StreamHandler pointing to the current sys.stderr.
    This is called "just-in-time" before a warning is emitted to ensure
    it uses the sys.stderr that capsys (or other test utilities) might have patched.
    """
    # Check if there's already a handler pointing to the *current* sys.stderr.
    # This avoids adding duplicate handlers if this function is called multiple times
    # and sys.stderr hasn't changed.
    has_current_stderr_handler = any(
        isinstance(h, stdlib_logging.StreamHandler) and h.stream == sys.stderr
        for h in logger.handlers
    )

    if not has_current_stderr_handler:
        # If there are other handlers (e.g., to an old sys.stderr), remove them.
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            try:
                # Only close if it's not the global sys.stdout or sys.stderr
                if handler.stream not in (sys.stdout, sys.stderr):
                    handler.close()
            except Exception: # nosemgrep: generic-exception-handling
                pass # Ignore errors on close

        # Add the new handler using the current sys.stderr
        stderr_handler = stdlib_logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(_config_warning_formatter)
        logger.addHandler(stderr_handler)
        logger.setLevel(stdlib_logging.WARNING) # Ensure level is set
        logger.propagate = False # Prevent double logging if root logger is also configured

# LoggingConfig and TelemetryConfig class definitions remain here
# They use LogLevelStr and ConsoleFormatterStr which are defined above.

@define(frozen=True, slots=True)
class LoggingConfig:
    """
    Configuration for the Pyvider logging subsystem (structlog-based).

    This class defines all logging-specific configuration options, including
    log levels, output formatting, emoji features, and timestamp handling.

    Attributes:
        default_level: The default logging level for all loggers.
                      Can be overridden per module using module_levels.
        module_levels: A dictionary mapping module names to specific log levels.
                      Enables fine-grained control over logging verbosity.
        console_formatter: The formatter to use for console output.
                          "key_value" provides human-readable output,
                          "json" provides machine-parseable structured output.
        logger_name_emoji_prefix_enabled: If True, prepends context-aware emojis
                                        based on logger name patterns.
        das_emoji_prefix_enabled: If True, prepends Domain-Action-Status emojis
                                 based on semantic log fields.
        omit_timestamp: If True, timestamps will be omitted from log entries.
                       Useful for development or when external timestamping is used.

    Example:
        >>> config = LoggingConfig(
        ...     default_level="INFO",
        ...     module_levels={"auth": "DEBUG", "database": "ERROR"},
        ...     console_formatter="json",
        ... )
    """
    default_level: LogLevelStr = field(default="DEBUG")
    module_levels: dict[str, LogLevelStr] = field(factory=dict)
    console_formatter: ConsoleFormatterStr = field(default="key_value")
    logger_name_emoji_prefix_enabled: bool = field(default=True)
    das_emoji_prefix_enabled: bool = field(default=True)
    omit_timestamp: bool = field(default=False)


@define(frozen=True, slots=True)
class TelemetryConfig:
    """
    Main configuration object for Pyvider Telemetry (structlog-based).

    This is the top-level configuration class that encompasses all telemetry
    settings, including logging configuration and global system settings.

    Attributes:
        service_name: An optional service name to include in log entries.
                     Useful for identifying logs in multi-service environments.
                     Can also be set via OTEL_SERVICE_NAME or PYVIDER_SERVICE_NAME.
        logging: An instance of `LoggingConfig` for logging-specific settings.
                Provides fine-grained control over logging behavior.
        globally_disabled: If True, all telemetry (including logging) is disabled.
                          Useful for testing or environments where logging is not desired.

    Example:
        >>> config = TelemetryConfig(
        ...     service_name="my-service",
        ...     logging=LoggingConfig(default_level="INFO"),
        ...     globally_disabled=False,
        ... )
    """
    service_name: str | None = field(default=None)
    logging: LoggingConfig = field(factory=LoggingConfig)
    globally_disabled: bool = field(default=False)

    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        """
        Creates a TelemetryConfig instance from environment variables.

        This method provides a convenient way to configure telemetry using
        environment variables, which is common in containerized and cloud
        environments.

        Environment Variables Used:
            Service Configuration:
                - OTEL_SERVICE_NAME or PYVIDER_SERVICE_NAME: For `service_name`.
                  OTEL_SERVICE_NAME takes precedence for OpenTelemetry compatibility.

            Logging Configuration:
                - PYVIDER_LOG_LEVEL: For `logging.default_level`.
                  Valid values: CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE, NOTSET
                - PYVIDER_LOG_CONSOLE_FORMATTER: For `logging.console_formatter`.
                  Valid values: key_value, json
                - PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED: For emoji prefix feature.
                  Valid values: true, false (case insensitive)
                - PYVIDER_LOG_DAS_EMOJI_ENABLED: For DAS emoji feature.
                  Valid values: true, false (case insensitive)
                - PYVIDER_LOG_OMIT_TIMESTAMP: For timestamp handling.
                  Valid values: true, false (case insensitive)
                - PYVIDER_LOG_MODULE_LEVELS: For per-module log levels.
                  Format: "module1:LEVEL1,module2:LEVEL2"
                  Example: "auth:DEBUG,database:ERROR,cache:WARNING"

            Global Configuration:
                - PYVIDER_TELEMETRY_DISABLED: For `globally_disabled`.
                  Valid values: true, false (case insensitive)

        Returns:
            A new TelemetryConfig instance configured from environment variables.

        Note:
            Invalid environment variable values fall back to defaults with
            warnings printed to stderr. This ensures the system remains
            functional even with misconfiguration.

        Example:
            >>> import os
            >>> os.environ["PYVIDER_SERVICE_NAME"] = "my-service"
            >>> os.environ["PYVIDER_LOG_LEVEL"] = "INFO"
            >>> config = TelemetryConfig.from_env()
            >>> assert config.service_name == "my-service"
            >>> assert config.logging.default_level == "INFO"
        """
        # Load service name with OpenTelemetry compatibility
        service_name_env: str | None = os.getenv(
            "OTEL_SERVICE_NAME", os.getenv("PYVIDER_SERVICE_NAME")
        )

        # Load and validate log level
        raw_default_log_level: str = os.getenv("PYVIDER_LOG_LEVEL", "DEBUG").upper()
        default_log_level: LogLevelStr

        match raw_default_log_level:
            case level if level in _VALID_LOG_LEVEL_TUPLE:
                default_log_level = level  # type: ignore[assignment]
            case _:
                _ensure_config_logger_handler(config_warnings_logger)
                config_warnings_logger.warning(
                    f"⚙️➡️⚠️ Invalid PYVIDER_LOG_LEVEL '{raw_default_log_level}'. Defaulting to DEBUG."
                )
                default_log_level = "DEBUG"

        # Load and validate console formatter
        raw_console_formatter: str = os.getenv(
            "PYVIDER_LOG_CONSOLE_FORMATTER", "key_value"
        ).lower()
        console_formatter: ConsoleFormatterStr

        match raw_console_formatter:
            case formatter if formatter in _VALID_FORMATTER_TUPLE:
                console_formatter = formatter  # type: ignore[assignment]
            case _:
                _ensure_config_logger_handler(config_warnings_logger)
                config_warnings_logger.warning(
                    f"⚙️➡️⚠️ Invalid PYVIDER_LOG_CONSOLE_FORMATTER '{raw_console_formatter}'. Defaulting to 'key_value'."
                )
                console_formatter = "key_value"

        # Load boolean configuration options
        logger_name_emoji_enabled_str: str = os.getenv(
            "PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED", "true"
        ).lower()
        logger_name_emoji_prefix_enabled: bool = logger_name_emoji_enabled_str == "true"

        das_emoji_enabled_str: str = os.getenv(
            "PYVIDER_LOG_DAS_EMOJI_ENABLED", "true"
        ).lower()
        das_emoji_prefix_enabled: bool = das_emoji_enabled_str == "true"

        omit_timestamp_str: str = os.getenv("PYVIDER_LOG_OMIT_TIMESTAMP", "false").lower()
        omit_timestamp_bool: bool = omit_timestamp_str == "true"

        globally_disabled_str: str = os.getenv("PYVIDER_TELEMETRY_DISABLED", "false").lower()
        globally_disabled: bool = globally_disabled_str == "true"

        # Parse module-specific log levels
        module_levels = cls._parse_module_levels(
            os.getenv("PYVIDER_LOG_MODULE_LEVELS", "")
        )

        # Create logging configuration
        log_cfg = LoggingConfig(
            default_level=default_log_level,
            module_levels=module_levels,
            console_formatter=console_formatter,
            logger_name_emoji_prefix_enabled=logger_name_emoji_prefix_enabled,
            das_emoji_prefix_enabled=das_emoji_prefix_enabled,
            omit_timestamp=omit_timestamp_bool,
        )

        # Create and return main configuration
        return cls(
            service_name=service_name_env,
            logging=log_cfg,
            globally_disabled=globally_disabled
        )

    @staticmethod
    def _parse_module_levels(levels_str: str) -> dict[str, LogLevelStr]:
        """
        Parses a comma-separated string of module log level overrides.

        This method handles the parsing of the PYVIDER_LOG_MODULE_LEVELS
        environment variable, which allows setting different log levels
        for different modules or logger names.

        Args:
            levels_str: String in the format "module1:LEVEL1,module2:LEVEL2".
                       Whitespace around module names and levels is ignored.
                       Invalid entries are skipped with warnings.

        Returns:
            A dictionary mapping module names to LogLevelStr values.
            Only valid entries are included in the result.

        Example:
            >>> levels = TelemetryConfig._parse_module_levels("auth:DEBUG,db:ERROR")
            >>> assert levels == {"auth": "DEBUG", "db": "ERROR"}

            >>> # Invalid entries are skipped
            >>> levels = TelemetryConfig._parse_module_levels("auth:DEBUG,bad:INVALID")
            >>> assert levels == {"auth": "DEBUG"}
        """
        levels: dict[str, LogLevelStr] = {}

        if not levels_str.strip():
            return levels

        for item in levels_str.split(","):
            item = item.strip()
            if not item:
                continue

            parts: list[str] = item.split(":", 1)
            match len(parts):
                case 2:
                    module_name: str = parts[0].strip()
                    level_name_raw: str = parts[1].strip().upper()

                    # Validate module name
                    if not module_name:
                        _ensure_config_logger_handler(config_warnings_logger)
                        config_warnings_logger.warning(
                            f"⚙️➡️⚠️ Empty module name in PYVIDER_LOG_MODULE_LEVELS item '{item}'. Skipping."
                        )
                        continue

                    # Validate and assign log level
                    match level_name_raw:
                        case level if level in _VALID_LOG_LEVEL_TUPLE:
                            levels[module_name] = level  # type: ignore[assignment]
                        case _:
                            _ensure_config_logger_handler(config_warnings_logger)
                            config_warnings_logger.warning(
                                f"⚙️➡️⚠️ Invalid log level '{level_name_raw}' for module '{module_name}' "
                                f"in PYVIDER_LOG_MODULE_LEVELS. Skipping."
                            )

                case _:
                    _ensure_config_logger_handler(config_warnings_logger)
                    config_warnings_logger.warning(
                        f"⚙️➡️⚠️ Invalid item '{item}' in PYVIDER_LOG_MODULE_LEVELS. "
                        f"Expected 'module:LEVEL' format. Skipping."
                    )

        return levels

# ---- Processor Chain Building Logic Moved from core.py ----

# Helper: Create service name processor (moved from core.py)
def _config_create_service_name_processor(service_name: str | None) -> StructlogProcessor:
    """
    Factory function that creates a structlog processor for service name injection.
    (Moved from core.py)
    """
    def processor(
        _logger: Any, _method_name: str, event_dict: structlog.types.EventDict
    ) -> structlog.types.EventDict:
        if service_name is not None:
            event_dict["service_name"] = service_name
        return event_dict
    return processor

# Helper: Create timestamp processors (moved from core.py)
def _config_create_timestamp_processors(omit_timestamp: bool) -> list[StructlogProcessor]:
    """
    Creates timestamp-related processors based on configuration.
    (Moved from core.py)
    """
    processors: list[StructlogProcessor] = [
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False)
    ]
    if omit_timestamp:
        def pop_timestamp_processor(
            _logger: Any, _method_name: str, event_dict: structlog.types.EventDict
        ) -> structlog.types.EventDict:
            event_dict.pop("timestamp", None)
            return event_dict
        processors.append(pop_timestamp_processor)
    return processors

# Helper: Create emoji processors (moved from core.py)
def _config_create_emoji_processors(logging_config: "LoggingConfig") -> list[StructlogProcessor]:
    """
    Creates emoji-related processors based on configuration flags.
    (Moved from core.py)
    """
    processors: list[StructlogProcessor] = []
    if logging_config.logger_name_emoji_prefix_enabled:
        processors.append(add_logger_name_emoji_prefix)
    if logging_config.das_emoji_prefix_enabled:
        processors.append(add_das_emoji_prefix)
    return processors

# Main function to build the core list of processors (excluding formatters)
def _build_core_processors_list(config: "TelemetryConfig") -> list[StructlogProcessor]:
    """
    Builds the core processor chain (excluding formatters) based on configuration.
    (Logic moved from _build_core_processor_chain in core.py)
    """
    log_cfg = config.logging
    processors: list[StructlogProcessor] = [
        structlog.contextvars.merge_contextvars,
        add_log_level_custom,
        filter_by_level_custom(
            default_level_str=log_cfg.default_level,
            module_levels=log_cfg.module_levels,
            level_to_numeric_map=_LEVEL_TO_NUMERIC # Use _LEVEL_TO_NUMERIC from this module
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]
    processors.extend(_config_create_timestamp_processors(log_cfg.omit_timestamp))
    if config.service_name is not None:
        processors.append(_config_create_service_name_processor(config.service_name))
    processors.extend(_config_create_emoji_processors(log_cfg))
    return processors

# Helper: Create JSON formatter processors (moved from core.py)
def _config_create_json_formatter_processors() -> list[Any]:
    """
    Creates JSON output formatter processors.
    (Moved from core.py)
    """
    return [
        structlog.processors.format_exc_info, # Should be before renderer
        structlog.processors.JSONRenderer(serializer=json.dumps, sort_keys=False)
    ]

# Helper: Create key-value formatter processors (moved from core.py)
def _config_create_keyvalue_formatter_processors(output_stream: TextIO) -> list[Any]:
    """
    Creates key-value output formatter processors.
    (Moved from core.py)
    """
    processors: list[Any] = []
    def pop_logger_name_processor(
        _logger: Any, _method_name: str, event_dict: structlog.types.EventDict
    ) -> structlog.types.EventDict:
        event_dict.pop("logger_name", None)
        return event_dict
    processors.append(pop_logger_name_processor)
    is_tty = hasattr(output_stream, 'isatty') and output_stream.isatty()
    processors.append(
        structlog.dev.ConsoleRenderer(
            colors=is_tty,
            exception_formatter=structlog.dev.plain_traceback,
        )
    )
    return processors

# Main function to build the list of formatter processors
def _build_formatter_processors_list(
    logging_config: "LoggingConfig", output_stream: TextIO
) -> list[Any]:
    """
    Creates output formatter processors based on configuration.
    (Logic moved from _create_formatter_processors in core.py, logging removed)
    """
    match logging_config.console_formatter:
        case "json":
            # Logging about chosen formatter will be done in core.py
            return _config_create_json_formatter_processors()
        case "key_value":
            # Logging about chosen formatter will be done in core.py
            return _config_create_keyvalue_formatter_processors(output_stream)
        case unknown_formatter:
            # This case should ideally be prevented by earlier config validation.
            # If it occurs, default to key_value. Logging for this fallback can also be in core.py.
            # Consider if a warning is still needed here, perhaps using config_warnings_logger.
            # For now, adhering to "no logging side effects from config determination".
            _ensure_config_logger_handler(config_warnings_logger)
            config_warnings_logger.warning(
                f"⚙️➡️⚠️ Unknown PYVIDER_LOG_CONSOLE_FORMATTER '{unknown_formatter}' encountered "
                f"during processor list build. Defaulting to 'key_value' formatter."
            )
            return _config_create_keyvalue_formatter_processors(output_stream)

# 🐍⚙️
