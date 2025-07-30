#
# config.py
#

import os
import sys
import logging as stdlib_logging
from typing import TYPE_CHECKING, Literal, Any, TextIO

from attrs import define, field

if TYPE_CHECKING:
    pass

# Define fundamental type aliases
LogLevelStr = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"]
_VALID_LOG_LEVEL_TUPLE: tuple[LogLevelStr, ...] = (
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "NOTSET"
)
ConsoleFormatterStr = Literal["key_value", "json"]
_VALID_FORMATTER_TUPLE: tuple[ConsoleFormatterStr, ...] = ("key_value", "json")

# Import dependencies after type definitions
import structlog
import json
from pyvider.telemetry.logger.custom_processors import (
    StructlogProcessor,
    add_log_level_custom,
    filter_by_level_custom,
    add_logger_name_emoji_prefix,
    add_das_emoji_prefix,
    TRACE_LEVEL_NUM,
)

# Level mapping
_LEVEL_TO_NUMERIC: dict[LogLevelStr, int] = {
    "CRITICAL": stdlib_logging.CRITICAL,
    "ERROR": stdlib_logging.ERROR,
    "WARNING": stdlib_logging.WARNING,
    "INFO": stdlib_logging.INFO,
    "DEBUG": stdlib_logging.DEBUG,
    "TRACE": TRACE_LEVEL_NUM,
    "NOTSET": stdlib_logging.NOTSET,
}

# Default environment configuration for zero-config usage (emoji settings handled conditionally)
DEFAULT_ENV_CONFIG: dict[str, str] = {
    "PYVIDER_LOG_LEVEL": "DEBUG",
    "PYVIDER_LOG_CONSOLE_FORMATTER": "key_value",
    "PYVIDER_LOG_OMIT_TIMESTAMP": "false",
    "PYVIDER_TELEMETRY_DISABLED": "false",
    "PYVIDER_LOG_MODULE_LEVELS": "",
    # Note: Emoji settings are set conditionally in _apply_default_env_config()
}

# Configuration warnings logger
config_warnings_logger = stdlib_logging.getLogger("pyvider.telemetry.config_warnings")
_config_warning_formatter = stdlib_logging.Formatter(
    "[Pyvider Config Warning] %(levelname)s (%(name)s): %(message)s"
)


def _ensure_config_logger_handler(logger: stdlib_logging.Logger) -> None:
    """
    Ensures the config warnings logger has a StreamHandler pointing to stderr.

    Args:
        logger: The logger to configure.
    """
    has_current_stderr_handler = any(
        isinstance(h, stdlib_logging.StreamHandler) and h.stream == sys.stderr
        for h in logger.handlers
    )

    if not has_current_stderr_handler:
        # Remove old handlers
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            try:
                if handler.stream not in (sys.stdout, sys.stderr):
                    handler.close()
            except Exception:
                pass

        # Add new stderr handler
        stderr_handler = stdlib_logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(_config_warning_formatter)
        logger.addHandler(stderr_handler)
        logger.setLevel(stdlib_logging.WARNING)
        logger.propagate = False


@define(frozen=True, slots=True)
class LoggingConfig:
    """
    Configuration for the Pyvider logging subsystem (structlog-based).

    Attributes:
        default_level: The default logging level for all loggers.
        module_levels: Module-specific log level overrides.
        console_formatter: Output formatter ("key_value" or "json").
        logger_name_emoji_prefix_enabled: Enable logger name emoji prefixes.
        das_emoji_prefix_enabled: Enable Domain-Action-Status emoji prefixes.
        omit_timestamp: Omit timestamps from log entries.
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

    Attributes:
        service_name: Optional service name for log entries.
        logging: Logging configuration instance.
        globally_disabled: If True, all telemetry is disabled.
    """
    service_name: str | None = field(default=None)
    logging: LoggingConfig = field(factory=LoggingConfig)
    globally_disabled: bool = field(default=False)

    @classmethod
    def from_env(cls) -> "TelemetryConfig":
        """
        Creates a TelemetryConfig instance from environment variables with enhanced defaults.

        This method now provides sensible defaults even when environment variables
        are not set, enabling zero-configuration usage.

        Returns:
            A new TelemetryConfig instance.
        """
        # Apply default environment configuration for missing variables
        _apply_default_env_config()

        # Load service name with OpenTelemetry compatibility
        service_name_env: str | None = os.getenv(
            "OTEL_SERVICE_NAME", os.getenv("PYVIDER_SERVICE_NAME")
        )

        # FIXED: Load and validate log level with consistent fallback
        raw_default_log_level: str = os.getenv("PYVIDER_LOG_LEVEL", "DEBUG").upper()
        default_log_level: LogLevelStr

        if raw_default_log_level in _VALID_LOG_LEVEL_TUPLE:
            default_log_level = raw_default_log_level  # type: ignore[assignment]
        else:
            _ensure_config_logger_handler(config_warnings_logger)
            config_warnings_logger.warning(
                f"⚙️➡️⚠️ Invalid PYVIDER_LOG_LEVEL '{raw_default_log_level}'. Defaulting to DEBUG."
            )
            default_log_level = "DEBUG"  # FIXED: Match LoggingConfig default

        # Load and validate console formatter
        raw_console_formatter: str = os.getenv(
            "PYVIDER_LOG_CONSOLE_FORMATTER", "key_value"
        ).lower()
        console_formatter: ConsoleFormatterStr

        if raw_console_formatter in _VALID_FORMATTER_TUPLE:
            console_formatter = raw_console_formatter  # type: ignore[assignment]
        else:
            _ensure_config_logger_handler(config_warnings_logger)
            config_warnings_logger.warning(
                f"⚙️➡️⚠️ Invalid PYVIDER_LOG_CONSOLE_FORMATTER '{raw_console_formatter}'. Defaulting to 'key_value'."
            )
            console_formatter = "key_value"

        # FIXED: Load boolean configuration options using the determined formatter
        # This ensures emoji defaults are based on the final formatter choice
        logger_name_emoji_enabled: bool = _parse_bool_env_with_formatter_default(
            "PYVIDER_LOG_LOGGER_NAME_EMOJI_ENABLED", console_formatter
        )
        das_emoji_enabled: bool = _parse_bool_env_with_formatter_default(
            "PYVIDER_LOG_DAS_EMOJI_ENABLED", console_formatter
        )
        omit_timestamp: bool = _parse_bool_env(
            "PYVIDER_LOG_OMIT_TIMESTAMP", False
        )
        globally_disabled: bool = _parse_bool_env(
            "PYVIDER_TELEMETRY_DISABLED", False
        )

        # Parse module-specific log levels
        module_levels = cls._parse_module_levels(
            os.getenv("PYVIDER_LOG_MODULE_LEVELS", "")
        )

        # Create logging configuration
        log_cfg = LoggingConfig(
            default_level=default_log_level,
            module_levels=module_levels,
            console_formatter=console_formatter,
            logger_name_emoji_prefix_enabled=logger_name_emoji_enabled,
            das_emoji_prefix_enabled=das_emoji_enabled,
            omit_timestamp=omit_timestamp,
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

        Args:
            levels_str: String in format "module1:LEVEL1,module2:LEVEL2".

        Returns:
            Dictionary mapping module names to LogLevelStr values.
        """
        levels: dict[str, LogLevelStr] = {}

        if not levels_str.strip():
            return levels

        for item in levels_str.split(","):
            item = item.strip()
            if not item:
                continue

            parts: list[str] = item.split(":", 1)
            if len(parts) == 2:
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
                if level_name_raw in _VALID_LOG_LEVEL_TUPLE:
                    levels[module_name] = level_name_raw  # type: ignore[assignment]
                else:
                    _ensure_config_logger_handler(config_warnings_logger)
                    config_warnings_logger.warning(
                        f"⚙️➡️⚠️ Invalid log level '{level_name_raw}' for module '{module_name}' "
                        f"in PYVIDER_LOG_MODULE_LEVELS. Skipping."
                    )
            else:
                _ensure_config_logger_handler(config_warnings_logger)
                config_warnings_logger.warning(
                    f"⚙️➡️⚠️ Invalid item '{item}' in PYVIDER_LOG_MODULE_LEVELS. "
                    f"Expected 'module:LEVEL' format. Skipping."
                )

        return levels


def _apply_default_env_config() -> None:
    """
    Applies default environment configuration for variables that aren't set.

    This enables zero-configuration usage by providing sensible defaults.
    Note: Emoji settings are handled conditionally based on formatter type.
    """
    for key, default_value in DEFAULT_ENV_CONFIG.items():
        if key not in os.environ:
            os.environ[key] = default_value

    # FIXED: Don't set emoji defaults here - they'll be handled in from_env()
    # This prevents premature setting of emoji defaults before formatter is determined


def _parse_bool_env(env_var: str, default: bool) -> bool:
    """
    Parses a boolean environment variable with a default fallback.

    Args:
        env_var: Environment variable name.
        default: Default value if variable is not set.

    Returns:
        Parsed boolean value.
    """
    value = os.getenv(env_var, str(default).lower()).lower()
    return value == "true"


def _parse_bool_env_with_formatter_default(env_var: str, formatter: ConsoleFormatterStr) -> bool:
    """
    Parses a boolean environment variable with formatter-specific defaults.

    Args:
        env_var: Environment variable name.
        formatter: The console formatter being used.

    Returns:
        Parsed boolean value.
    """
    if env_var in os.environ:
        # If explicitly set, use that value
        return _parse_bool_env(env_var, True)
    else:
        # If not set, use formatter-specific default
        # JSON format: emojis disabled by default
        # Key-value format: emojis enabled by default
        return formatter != "json"


# Processor chain building functions (existing code)
def _config_create_service_name_processor(service_name: str | None) -> StructlogProcessor:
    """Factory function for service name injection processor."""
    def processor(
        _logger: Any, _method_name: str, event_dict: structlog.types.EventDict
    ) -> structlog.types.EventDict:
        if service_name is not None:
            event_dict["service_name"] = service_name
        return event_dict
    return processor


def _config_create_timestamp_processors(omit_timestamp: bool) -> list[StructlogProcessor]:
    """Creates timestamp-related processors based on configuration."""
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


def _config_create_emoji_processors(logging_config: LoggingConfig) -> list[StructlogProcessor]:
    """Creates emoji-related processors based on configuration flags."""
    processors: list[StructlogProcessor] = []
    if logging_config.logger_name_emoji_prefix_enabled:
        processors.append(add_logger_name_emoji_prefix)
    if logging_config.das_emoji_prefix_enabled:
        processors.append(add_das_emoji_prefix)
    return processors


def _build_core_processors_list(config: TelemetryConfig) -> list[StructlogProcessor]:
    """Builds the core processor chain (excluding formatters) based on configuration."""
    log_cfg = config.logging
    processors: list[StructlogProcessor] = [
        structlog.contextvars.merge_contextvars,
        add_log_level_custom,
        filter_by_level_custom(
            default_level_str=log_cfg.default_level,
            module_levels=log_cfg.module_levels,
            level_to_numeric_map=_LEVEL_TO_NUMERIC
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]
    processors.extend(_config_create_timestamp_processors(log_cfg.omit_timestamp))
    if config.service_name is not None:
        processors.append(_config_create_service_name_processor(config.service_name))
    processors.extend(_config_create_emoji_processors(log_cfg))
    return processors


def _config_create_json_formatter_processors() -> list[Any]:
    """Creates JSON output formatter processors."""
    return [
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(serializer=json.dumps, sort_keys=False)
    ]


def _config_create_keyvalue_formatter_processors(output_stream: TextIO) -> list[Any]:
    """Creates key-value output formatter processors."""
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


def _build_formatter_processors_list(
    logging_config: LoggingConfig, output_stream: TextIO
) -> list[Any]:
    """Creates output formatter processors based on configuration."""
    match logging_config.console_formatter:
        case "json":
            return _config_create_json_formatter_processors()
        case "key_value":
            return _config_create_keyvalue_formatter_processors(output_stream)
        case unknown_formatter:
            _ensure_config_logger_handler(config_warnings_logger)
            config_warnings_logger.warning(
                f"⚙️➡️⚠️ Unknown PYVIDER_LOG_CONSOLE_FORMATTER '{unknown_formatter}' encountered "
                f"during processor list build. Defaulting to 'key_value' formatter."
            )
            return _config_create_keyvalue_formatter_processors(output_stream)

# 🐍⚙️
