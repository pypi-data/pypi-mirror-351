# unifyops_core/logging/logger_config.py

import logging.config
from typing import Dict, Any
import logging
import os

from app.config import settings
from unifyops_core.logging.formatter import LevelColorFormatter, SignozJSONFormatter

"""
Centralized logging configuration for the UnifyOps application with Signoz optimization.

This module configures the Python logging system with enhanced support for Signoz ingestion:
- OpenTelemetry-compliant structured logging
- Signoz-optimized JSON formatting
- Enhanced trace context propagation
- Proper resource attributes for service identification

Environment variables that control behavior:
- ENVIRONMENT: The deployment environment (local, test, staging, prod)
- LOG_LEVEL: The minimum log level to record (DEBUG, INFO, WARNING, etc.)
- LOG_STYLE: Force a specific logging style (auto, console, json)
- SERVICE_NAME: The name of the service for Signoz identification
- SERVICE_VERSION: The version of the service
- DEPLOYMENT_ENVIRONMENT: The deployment environment for Signoz
"""

# Centralized settings with Signoz-specific enhancements
ENVIRONMENT: str = settings.ENVIRONMENT.lower()
IS_LOCAL: bool = ENVIRONMENT in ("local", "test")
LOG_LEVEL: str = settings.LOG_LEVEL.upper() if hasattr(settings.LOG_LEVEL, 'upper') else settings.LOG_LEVEL
LOG_STYLE: str = settings.LOG_STYLE
SERVICE_NAME = getattr(settings, 'SERVICE_NAME', 'unifyops-api')
SERVICE_VERSION = getattr(settings, 'VERSION', '1.0.0')
SERVICE_NAMESPACE = getattr(settings, 'SERVICE_NAMESPACE', 'unifyops')
DEPLOYMENT_ENVIRONMENT = getattr(settings, 'DEPLOYMENT_ENVIRONMENT', ENVIRONMENT)
LOG_RETENTION_DAYS = getattr(settings, 'LOG_RETENTION_DAYS', 30)

# OpenTelemetry resource attributes for Signoz
OTEL_RESOURCE_ATTRIBUTES = {
    "service.name": SERVICE_NAME,
    "service.version": SERVICE_VERSION,
    "service.namespace": SERVICE_NAMESPACE,
    "deployment.environment": DEPLOYMENT_ENVIRONMENT,
    "telemetry.sdk.language": "python",
    "telemetry.sdk.name": "opentelemetry",
}

# Export resource attributes as environment variable for OTel SDK
if not os.getenv("OTEL_RESOURCE_ATTRIBUTES"):
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = ",".join(
        [f"{k}={v}" for k, v in OTEL_RESOURCE_ATTRIBUTES.items()]
    )

# Decide console vs JSON
if LOG_STYLE == "auto":
    use_console = IS_LOCAL
elif LOG_STYLE == "console":
    use_console = True
else:
    use_console = False

# Base handler (app logs) with Signoz optimization
handlers: Dict[str, Dict[str, Any]] = {
    "stdout": {
        "class":     "logging.StreamHandler",
        "formatter": "console" if use_console else "signoz_json",
        "level":     LOG_LEVEL,
        "stream":    "ext://sys.stdout",
    }
}

# Null handler for suppressing unwanted logs
handlers["null"] = {
    "class": "logging.NullHandler",
}

# Configure third-party loggers to reduce noise
third_party_loggers = {
    # Uvicorn loggers
    "uvicorn":        {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "uvicorn.access": {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "uvicorn.error":  {"level": "ERROR", "handlers": ["stdout"], "propagate": False},
    
    # HTTP client libraries
    "httpx":          {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "httpcore":       {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "urllib3":        {"level": "WARNING", "handlers": ["null"], "propagate": False},
    
    # Database libraries
    "sqlalchemy":     {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "sqlalchemy.engine": {"level": "WARNING", "handlers": ["null"], "propagate": False},
    
    # Other common libraries
    "asyncio":        {"level": "WARNING", "handlers": ["null"], "propagate": False},
    "watchfiles":     {"level": "WARNING", "handlers": ["null"], "propagate": False},
}

# Full logging configuration dictionary with Signoz enhancements
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {
            "()": LevelColorFormatter,
            "format": "%(asctime)s [%(colored_levelname)s] %(message)s (%(shortpath)s:%(lineno)d)",
            "datefmt": "%H:%M:%S",
        },
        "signoz_json": {
            "()": SignozJSONFormatter,
            "format": "%(message)s",
            # Signoz-specific configuration
            "service_name": SERVICE_NAME,
            "service_version": SERVICE_VERSION,
            "deployment_environment": DEPLOYMENT_ENVIRONMENT,
        },
    },

    "handlers": handlers,

    "root": {
        "handlers": ["stdout"],
        "level":    LOG_LEVEL,
    },

    "loggers": {
        **third_party_loggers,
        # Application-specific loggers
        "unifyops": {
            "level": LOG_LEVEL,
            "handlers": ["stdout"],
            "propagate": False,
        },
    },
}

# Apply configuration
def configure_logging() -> None:
    """
    Configure the Python logging system with Signoz-optimized settings.
    
    This function applies the LOGGING_CONFIG to Python's logging system with
    enhancements for Signoz ingestion including proper resource attributes
    and OpenTelemetry compliance.
    
    Raises:
        ValueError: If an invalid log level is specified
    """
    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        
        # Log initial configuration info
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configured for Signoz ingestion",
            extra={
                "service.name": SERVICE_NAME,
                "service.version": SERVICE_VERSION,
                "deployment.environment": DEPLOYMENT_ENVIRONMENT,
                "log.level": LOG_LEVEL,
            }
        )
    except ValueError as e:
        # Provide a more helpful error message for log level issues
        if "Unknown level" in str(e):
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            print(f"ERROR: Invalid log level '{settings.LOG_LEVEL}'. Valid levels are: {', '.join(valid_levels)}")
        raise

# Apply configuration when this module is imported
configure_logging()
