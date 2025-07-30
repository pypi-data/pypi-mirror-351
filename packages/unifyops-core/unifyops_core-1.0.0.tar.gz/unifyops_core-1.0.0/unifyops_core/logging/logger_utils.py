import os
import json
import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
import time

from unifyops_core.utils import parse_uuids
from unifyops_core.logging.context_vars import (
    correlation_id_var, 
    metadata_var, 
    trace_id_var, 
    span_id_var
)

# Metrics tracking
_log_counts = defaultdict(int)
_serialization_errors = 0
_rate_limit_counters = defaultdict(int)
_rate_limit_timestamps = defaultdict(float)

def get_logging_metrics():
    """
    Return metrics about the logging system performance.
    
    Returns:
        Dict containing log counts by level and error statistics
    """
    return {
        "log_counts_by_level": dict(_log_counts),
        "serialization_errors": _serialization_errors,
        "rate_limited_logs": dict(_rate_limit_counters)
    }

def is_rate_limited(key: str, max_count: int, time_window: float) -> bool:
    """
    Check if a log should be rate limited.
    
    Args:
        key: The rate limiting key (usually log message or category)
        max_count: Maximum allowed count in the time window
        time_window: Time window in seconds
        
    Returns:
        True if the log should be rate limited, False otherwise
    """
    now = time.time()
    
    # Reset counter if time window has passed
    if now - _rate_limit_timestamps.get(key, 0) > time_window:
        _rate_limit_counters[key] = 0
        _rate_limit_timestamps[key] = now
    
    # Increment counter
    _rate_limit_counters[key] += 1
    
    # Check if limit exceeded
    return _rate_limit_counters[key] > max_count

# ——— Metadata helpers ———
def add_logging_metadata(**kwargs) -> None:
    """
    Merge these key/value pairs into the current request's metadata.
    They'll end up as flat fields in the JSON log.
    """
    meta = metadata_var.get() or {}
    meta.update(kwargs)
    metadata_var.set(meta)


# ——— JSON builder ———
def format_log_as_json(record: logging.LogRecord, message: str) -> str:
    """
    Assemble structured log data in the format expected by DataDog.
    
    This function transforms a log record into a properly structured JSON
    format with metadata flattening and correlation ID tracking.
    
    Args:
        record: The LogRecord object
        message: The formatted log message
        
    Returns:
        JSON string representation of the log data
        
    Raises:
        ValueError: If the record contains data that cannot be serialized to JSON
    """
    # Track metrics by log level
    global _serialization_errors
    _log_counts[record.levelname] += 1
    
    try:
        # Process metadata with UUID handling
        flat_meta = _flatten_metadata(metadata_var.get() or {})
        
        # Get trace context if available
        trace_id = trace_id_var.get()
        span_id = span_id_var.get()
        
        # Build the base payload with standard fields
        payload = {
            # core log data
            "message":    message,
            "levelname":  record.levelname,
            "timestamp":  int(record.created * 1000),
            "logger.name":record.name,
            "threadName": record.threadName,
            "correlation_id": correlation_id_var.get(),
    
            # source info
            "pathname": getattr(record, "source_file", record.pathname),
            "lineno":   getattr(record, "source_line", record.lineno),
            "funcName": record.funcName,
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "ddsource": "python",
            "service": os.getenv("SERVICE_NAME", "unifyops-api"),
            "env": os.getenv("ENVIRONMENT", "development"),
            **flat_meta,
        }
        
        # Add OpenTelemetry trace context if available
        if trace_id:
            payload["trace_id"] = trace_id
        if span_id:
            payload["span_id"] = span_id
    
        # Add exception information if present
        if record.exc_info:
            err = logging.Formatter().formatException(record.exc_info)
            if err and "NoneType" not in err:
                payload["error.stack"] = err
    
        # Drop nulls and emit JSON
        clean = {k: v for k, v in payload.items() if v is not None}
        return json.dumps(clean)
    except TypeError as e:
        # Handle JSON serialization errors gracefully
        _serialization_errors += 1
        fallback = {
            "message": f"ERROR SERIALIZING LOG: {str(e)}",
            "original_message": message,
            "levelname": record.levelname,
            "timestamp": int(record.created * 1000),
            "logger.name": record.name,
            "correlation_id": correlation_id_var.get()
        }
        return json.dumps(fallback)
    except Exception as e:
        # Catch any other errors to prevent logging failures
        _serialization_errors += 1
        return json.dumps({
            "message": f"CRITICAL ERROR IN LOG FORMATTING: {str(e)}",
            "levelname": "ERROR",
            "timestamp": int(record.created * 1000)
        })


def format_log_for_signoz(record: logging.LogRecord, message: str) -> str:
    """
    Assemble structured log data optimized for Signoz ingestion.
    
    This function transforms a log record into a Signoz-optimized JSON format
    following OpenTelemetry log data model specifications with proper field
    organization for efficient querying and correlation.
    
    Args:
        record: The LogRecord object
        message: The formatted log message
        
    Returns:
        JSON string representation of the log data optimized for Signoz
    """
    # Track metrics by log level
    global _serialization_errors
    _log_counts[record.levelname] += 1
    
    try:
        # Get context variables
        correlation_id = correlation_id_var.get()
        trace_id = trace_id_var.get()
        span_id = span_id_var.get()
        metadata = metadata_var.get() or {}
        
        # Build the log payload following OpenTelemetry log data model
        payload = {
            # Timestamp in nanoseconds for OpenTelemetry compliance
            "timestamp": int(record.created * 1_000_000_000),
            
            # ISO timestamp for human readability
            "time": getattr(record, "iso_timestamp", 
                          datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()),
            
            # OpenTelemetry severity fields
            "severity_text": record.levelname,
            "severity_number": getattr(record, "severity_number", 0),
            
            # Log body
            "body": message,
            
            # Resource attributes (service identification)
            "resource": {
                "service.name": getattr(record, "service_name", "unifyops-api"),
                "service.version": getattr(record, "service_version", "1.0.0"),
                "deployment.environment": getattr(record, "deployment_environment", "production"),
                "host.name": os.getenv("HOSTNAME", "unknown"),
            },
            
            # Log attributes (contextual information)
            "attributes": {
                "logger.name": record.name,
                "code.filepath": _normalize_filepath(getattr(record, "source_file", record.pathname)),
                "code.lineno": getattr(record, "source_line", record.lineno),
                "code.function": record.funcName,
                "thread.name": record.threadName,
                "process.pid": os.getpid(),
            },
            
            # Instrumentation scope
            "scope": {
                "name": record.name,
                "version": getattr(record, "logger_version", "1.0.0"),
            },
        }
        
        # Add correlation ID if present
        if correlation_id:
            payload["attributes"]["correlation_id"] = correlation_id
        
        # Add trace context for correlation with traces
        if trace_id:
            payload["trace_id"] = trace_id
            payload["attributes"]["trace_id"] = trace_id
        if span_id:
            payload["span_id"] = span_id
            payload["attributes"]["span_id"] = span_id
            
        # Add trace flags if available
        trace_flags = getattr(record, "trace_flags", None)
        if trace_flags is not None:
            payload["attributes"]["trace_flags"] = trace_flags
        
        # Process and add custom metadata
        if metadata:
            # Parse UUIDs and flatten nested structures
            processed_metadata = parse_uuids(metadata)
            flattened_metadata = _flatten_metadata_for_signoz(processed_metadata)
            
            # Add to attributes with proper namespacing
            for key, value in flattened_metadata.items():
                # Namespace custom attributes to avoid conflicts
                namespaced_key = f"custom.{key}" if not key.startswith("custom.") else key
                payload["attributes"][namespaced_key] = value
        
        # Add exception information if present
        if record.exc_info:
            exception_info = _format_exception_for_signoz(record.exc_info)
            if exception_info:
                payload["attributes"]["exception.type"] = exception_info["type"]
                payload["attributes"]["exception.message"] = exception_info["message"]
                payload["attributes"]["exception.stacktrace"] = exception_info["stacktrace"]
                # Set severity to ERROR for exceptions
                payload["severity_text"] = "ERROR"
                payload["severity_number"] = 17
        
        # Add any extra fields from the record
        extra_fields = _extract_extra_fields(record)
        if extra_fields:
            payload["attributes"].update(extra_fields)
        
        # Ensure all values are JSON serializable
        clean_payload = _ensure_json_serializable(payload)
        
        # Return formatted JSON
        return json.dumps(clean_payload, separators=(',', ':'))
        
    except Exception as e:
        # Handle any errors gracefully
        _serialization_errors += 1
        fallback = {
            "timestamp": int(time.time() * 1_000_000_000),
            "severity_text": "ERROR",
            "severity_number": 17,
            "body": f"Log serialization error: {str(e)} - Original message: {message}",
            "resource": {
                "service.name": getattr(record, "service_name", "unifyops-api"),
            },
            "attributes": {
                "error.type": "LogSerializationError",
                "logger.name": record.name,
            }
        }
        return json.dumps(fallback, separators=(',', ':'))


def _flatten_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens nested metadata dictionaries for consistent log field structure.
    
    Args:
        metadata: The metadata dictionary to flatten
        
    Returns:
        Flattened dictionary with nested keys joined by underscores
    """
    flat_meta = {}
    for k, v in parse_uuids(metadata).items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                flat_meta[f"{k}_{subk}"] = subv
        else:
            flat_meta[k] = v
    return flat_meta


def _flatten_metadata_for_signoz(metadata: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Flattens nested metadata dictionaries using dot notation for Signoz.
    
    This follows OpenTelemetry attribute naming conventions using dots
    for nested structures rather than underscores.
    
    Args:
        metadata: The metadata dictionary to flatten
        prefix: Prefix for nested keys
        
    Returns:
        Flattened dictionary with nested keys joined by dots
    """
    flat_meta = {}
    
    for key, value in metadata.items():
        # Construct the full key
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            nested_flat = _flatten_metadata_for_signoz(value, full_key)
            flat_meta.update(nested_flat)
        elif isinstance(value, (list, tuple)):
            # Convert lists/tuples to JSON strings for Signoz
            flat_meta[full_key] = json.dumps(value)
        else:
            # Add the value directly
            flat_meta[full_key] = value
    
    return flat_meta


def _normalize_filepath(filepath: Optional[str]) -> str:
    """
    Normalize file path for consistent representation in Signoz.
    
    Args:
        filepath: The file path to normalize
        
    Returns:
        Normalized file path
    """
    if not filepath:
        return "<unknown>"
    
    # Make path relative to APP_ROOT if possible
    app_root = os.getenv("APP_ROOT", os.getcwd())
    if filepath.startswith(app_root):
        return os.path.relpath(filepath, app_root)
    
    return filepath


def _format_exception_for_signoz(exc_info) -> Optional[Dict[str, str]]:
    """
    Format exception information for Signoz following OpenTelemetry conventions.
    
    Args:
        exc_info: The exception info tuple
        
    Returns:
        Dictionary with exception details or None
    """
    if not exc_info:
        return None
    
    try:
        exc_type, exc_value, exc_tb = exc_info
        
        # Format the full stacktrace
        stacktrace = logging.Formatter().formatException(exc_info)
        
        return {
            "type": exc_type.__name__ if exc_type else "Unknown",
            "message": str(exc_value) if exc_value else "",
            "stacktrace": stacktrace
        }
    except Exception:
        return None


def _extract_extra_fields(record: logging.LogRecord) -> Dict[str, Any]:
    """
    Extract additional fields from the log record that aren't standard.
    
    Args:
        record: The LogRecord object
        
    Returns:
        Dictionary of extra fields
    """
    # Standard LogRecord attributes to exclude
    standard_attrs = {
        'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
        'levelno', 'lineno', 'module', 'msecs', 'pathname', 'process',
        'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
        'exc_text', 'stack_info', 'getMessage', 'custom_metadata', 'correlation_id',
        'iso_timestamp', 'severity_number', 'service_name', 'service_version',
        'deployment_environment', 'source_file', 'source_line', 'trace_id',
        'span_id', 'trace_flags', 'colored_levelname', 'shortpath'
    }
    
    extra = {}
    for key, value in record.__dict__.items():
        if key not in standard_attrs and not key.startswith('_'):
            # Ensure the key follows OpenTelemetry attribute naming
            clean_key = key.replace('_', '.').lower()
            extra[f"log.record.{clean_key}"] = value
    
    return extra


def _ensure_json_serializable(obj: Any) -> Any:
    """
    Recursively ensure all values in the object are JSON serializable.
    
    Args:
        obj: The object to process
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {k: _ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_ensure_json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # Convert non-serializable objects to strings
        return str(obj)


# Import datetime at the top if not already imported
from datetime import datetime, timezone
