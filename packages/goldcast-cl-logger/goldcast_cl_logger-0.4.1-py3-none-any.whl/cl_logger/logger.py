"""
Core logging functionality for CL Logger
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union
import re

from .trace_context import get_trace_id, get_trace_metadata


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging with trace support"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace ID if available
        trace_id = get_trace_id()
        if trace_id:
            log_data["trace_id"] = trace_id

        # Add trace metadata if available
        trace_metadata = get_trace_metadata()
        if trace_metadata:
            log_data["trace_metadata"] = trace_metadata

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class CLLogger:
    """
    A flexible logger that can switch between normal and JSON logging.
    Supports both f-string and structured logging formats.

    Example:
        logger = CLLogger("my_app")
        logger.info("Application started")

        # With f-string (supported)
        logger.info(f"User {user_id} logged in from {ip_address}")

        # With extra context (structured logging)
        logger.info("User action", extra={"user_id": 123, "action": "login"})

        # Switch to normal logging
        logger.set_json_logging(False)
    """

    def __init__(
        self,
        name: str,
        level: Union[str, int] = logging.INFO,
        json_logging: Optional[bool] = None,
        log_to_file: Optional[str] = None,
    ):
        """
        Initialize the logger.

        Args:
            name: Logger name (typically __name__)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            json_logging: Enable JSON logging (if None, checks CL_JSON_LOGGING env var, defaults to True)
            log_to_file: Optional file path for logging to file
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear any existing handlers

        # Check environment variable if json_logging not explicitly set
        # Default to True (JSON logging) if not specified
        if json_logging is None:
            json_logging = os.getenv("CL_JSON_LOGGING", "true").lower() != "false"

        self.json_logging = json_logging
        self._setup_handlers(log_to_file)

    def _setup_handlers(self, log_to_file: Optional[str] = None):
        """Set up logging handlers based on configuration"""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        if self.json_logging:
            console_handler.setFormatter(JsonFormatter())
        else:
            # Standard format for human-readable logs (includes trace ID)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s"
            )
            console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        # File handler if specified
        if log_to_file:
            file_handler = logging.FileHandler(log_to_file)
            if self.json_logging:
                file_handler.setFormatter(JsonFormatter())
            else:
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - [%(trace_id)s] - %(message)s"
                )
                file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def set_json_logging(self, enabled: bool):
        """Toggle between JSON and normal logging"""
        self.json_logging = enabled
        # Recreate handlers with new format
        handlers = self.logger.handlers.copy()
        log_to_file = None
        for handler in handlers:
            if isinstance(handler, logging.FileHandler):
                log_to_file = handler.baseFilename
        self.logger.handlers = []
        self._setup_handlers(log_to_file)

    def set_level(self, level: Union[str, int]):
        """Change the logging level"""
        self.logger.setLevel(level)

    def _log_with_extra(
        self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Internal method to log with extra fields and trace context"""
        # Add trace_id to the record for normal formatter
        if not self.json_logging:
            kwargs.setdefault("extra", {})
            kwargs["extra"]["trace_id"] = get_trace_id() or "no-trace"

        if extra and self.json_logging:
            # Store extra fields in the record for JSON formatter
            kwargs["extra"] = {"extra_fields": extra}
        elif extra:
            # For normal logging, append extra fields to message
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            msg = f"{msg} | {extra_str}"

        # Handle %-formatting by extracting args into extra fields
        if isinstance(msg, str) and "%" in msg and "args" in kwargs:
            try:
                # Get the format args
                args = kwargs.pop("args", ())
                if not isinstance(args, tuple):
                    args = (args,)

                # Create a mapping of format specifiers to their values
                extra_fields = {}
                format_specs = re.findall(r'%([a-zA-Z])', msg)
                
                # Map format specifiers to their values
                for i, (spec, value) in enumerate(zip(format_specs, args)):
                    if i < len(args):  # Make sure we have a value for this spec
                        # Use meaningful field names based on position
                        field_name = f"arg_{i+1}"
                        extra_fields[field_name] = value

                if extra_fields:
                    # Update extra with the extracted fields
                    if extra is None:
                        extra = {}
                    extra.update(extra_fields)

                    # Format the message with the values
                    msg = msg % args
            except Exception:
                # If anything goes wrong in parsing, just log the message as is
                pass

        # Handle f-string messages by extracting variables into extra fields
        elif isinstance(msg, str) and "{" in msg and "}" in msg:
            try:
                # If it's a simple f-string with variables, extract them
                import re
                import ast
                
                # Find all f-string expressions
                f_string_exprs = re.findall(r'\{([^{}]+)\}', msg)
                
                # Create a mapping of variable names to their values
                extra_fields = {}
                for expr in f_string_exprs:
                    # Skip complex expressions and just handle simple variable names
                    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr):
                        # Get the value from the local scope
                        try:
                            value = eval(expr, kwargs.get('extra', {}))
                            extra_fields[expr] = value
                        except (NameError, SyntaxError):
                            # If we can't evaluate, just keep the f-string as is
                            continue
                
                if extra_fields:
                    # Update extra with the extracted fields
                    if extra is None:
                        extra = {}
                    extra.update(extra_fields)
                    
                    # Replace the f-string expressions with their values
                    for expr, value in extra_fields.items():
                        msg = msg.replace(f"{{{expr}}}", str(value))
            except Exception:
                # If anything goes wrong in parsing, just log the message as is
                pass

        self.logger.log(level, msg, **kwargs)

    def debug(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message"""
        kwargs["args"] = args
        self._log_with_extra(logging.DEBUG, msg, extra, **kwargs)

    def info(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message"""
        kwargs["args"] = args
        self._log_with_extra(logging.INFO, msg, extra, **kwargs)

    def warning(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message"""
        kwargs["args"] = args
        self._log_with_extra(logging.WARNING, msg, extra, **kwargs)

    def warn(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message (deprecated alias for warning)"""
        self.warning(msg, *args, extra=extra, **kwargs)

    def error(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message with stack trace by default"""
        kwargs.setdefault(
            "exc_info", True
        )  # Set exc_info=True by default for error logs
        kwargs["args"] = args
        self._log_with_extra(logging.ERROR, msg, extra, **kwargs)

    def critical(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log critical message with stack trace by default"""
        kwargs.setdefault(
            "exc_info", True
        )  # Set exc_info=True by default for critical logs
        kwargs["args"] = args
        self._log_with_extra(logging.CRITICAL, msg, extra, **kwargs)

    def exception(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log exception with traceback (alias for error with exc_info=True)"""
        # This is now an alias for error() since error() includes exc_info by default
        self.error(msg, *args, extra=extra, **kwargs)


# Singleton pattern for easy access
_loggers: Dict[str, CLLogger] = {}


def get_logger(name: str, **kwargs) -> CLLogger:
    """
    Get or create a logger instance.

    This function maintains a singleton pattern, returning the same logger
    instance for a given name.

    Args:
        name: Logger name (typically __name__)
        **kwargs: Additional arguments passed to CLLogger constructor

    Returns:
        CLLogger instance
    """
    if name not in _loggers:
        _loggers[name] = CLLogger(name, **kwargs)
    return _loggers[name]
