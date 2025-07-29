"""Telemetry module for anonymous usage tracking with PostHog."""

import hashlib
import json
import os
import platform
import uuid
from pathlib import Path
from typing import Any

import posthog
from rich.console import Console

from golf import __version__

console = Console()

# PostHog configuration
# This is a client-side API key, safe to be public
# Users can override with GOLF_POSTHOG_API_KEY environment variable
DEFAULT_POSTHOG_API_KEY = "phc_7ccsDDxoC5tK5hodlrs2moGC74cThRzcN63flRYPWGl"
POSTHOG_API_KEY = os.environ.get("GOLF_POSTHOG_API_KEY", DEFAULT_POSTHOG_API_KEY)
POSTHOG_HOST = "https://us.i.posthog.com"

# Telemetry state
_telemetry_enabled: bool | None = None
_anonymous_id: str | None = None
_user_identified: bool = False  # Track if we've already identified the user


def _is_test_mode() -> bool:
    """Check if we're in test mode."""
    return os.environ.get("GOLF_TEST_MODE", "").lower() in ("1", "true", "yes", "on")


def _ensure_posthog_disabled_in_test_mode() -> None:
    """Ensure PostHog is disabled when in test mode."""
    if _is_test_mode() and not posthog.disabled:
        posthog.disabled = True


def get_telemetry_config_path() -> Path:
    """Get the path to the telemetry configuration file."""
    return Path.home() / ".golf" / "telemetry.json"


def save_telemetry_preference(enabled: bool) -> None:
    """Save telemetry preference to persistent storage."""
    config_path = get_telemetry_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config = {"enabled": enabled, "version": 1}

    try:
        with open(config_path, "w") as f:
            json.dump(config, f)
    except Exception:
        # Don't fail if we can't save the preference
        pass


def load_telemetry_preference() -> bool | None:
    """Load telemetry preference from persistent storage."""
    config_path = get_telemetry_config_path()

    if not config_path.exists():
        return None

    try:
        with open(config_path) as f:
            config = json.load(f)
            return config.get("enabled")
    except Exception:
        return None


def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled.

    Checks in order:
    1. Cached value
    2. GOLF_TEST_MODE environment variable (always disabled in test mode)
    3. GOLF_TELEMETRY environment variable
    4. Persistent preference file
    5. Default to True (opt-out model)
    """
    global _telemetry_enabled

    if _telemetry_enabled is not None:
        return _telemetry_enabled

    # Check if we're in test mode (highest priority after cache)
    if _is_test_mode():
        _telemetry_enabled = False
        return False

    # Check environment variables (second highest priority)
    env_telemetry = os.environ.get("GOLF_TELEMETRY", "").lower()
    if env_telemetry in ("0", "false", "no", "off"):
        _telemetry_enabled = False
        return False
    elif env_telemetry in ("1", "true", "yes", "on"):
        _telemetry_enabled = True
        return True

    # Check persistent preference
    saved_preference = load_telemetry_preference()
    if saved_preference is not None:
        _telemetry_enabled = saved_preference
        return saved_preference

    # Default to enabled (opt-out model)
    _telemetry_enabled = True
    return True


def set_telemetry_enabled(enabled: bool, persist: bool = True) -> None:
    """Set telemetry enabled state.

    Args:
        enabled: Whether telemetry should be enabled
        persist: Whether to save this preference persistently
    """
    global _telemetry_enabled
    _telemetry_enabled = enabled

    if persist:
        save_telemetry_preference(enabled)


def get_anonymous_id() -> str:
    """Get or create a persistent anonymous ID for this machine.

    The ID is stored in the user's home directory and is unique per installation.
    """
    global _anonymous_id

    if _anonymous_id:
        return _anonymous_id

    # Try to load existing ID
    id_file = Path.home() / ".golf" / "telemetry_id"

    if id_file.exists():
        try:
            _anonymous_id = id_file.read_text().strip()
            # Check if ID is in the old format (no hyphen between hash and random component)
            # Old format: golf-[8 chars hash][8 chars random]
            # New format: golf-[8 chars hash]-[8 chars random]
            if (
                _anonymous_id
                and _anonymous_id.startswith("golf-")
                and len(_anonymous_id) == 21
            ):
                # This is likely the old format, regenerate
                _anonymous_id = None
            elif _anonymous_id:
                return _anonymous_id
        except Exception:
            pass

    # Generate new ID with more unique data
    # Use only non-identifying system information

    # Combine non-identifying factors for uniqueness
    machine_data = (
        f"{platform.machine()}-{platform.system()}-{platform.python_version()}"
    )
    machine_hash = hashlib.sha256(machine_data.encode()).hexdigest()[:8]

    # Add a random component to ensure uniqueness
    random_component = str(uuid.uuid4()).split("-")[0]  # First 8 chars of UUID

    # Use hyphen separator for clarity and ensure PostHog treats these as different IDs
    _anonymous_id = f"golf-{machine_hash}-{random_component}"

    # Try to save for next time
    try:
        id_file.parent.mkdir(parents=True, exist_ok=True)
        id_file.write_text(_anonymous_id)
    except Exception:
        # Not critical if we can't save
        pass

    return _anonymous_id


def initialize_telemetry() -> None:
    """Initialize PostHog telemetry if enabled."""
    # Ensure PostHog is disabled in test mode
    _ensure_posthog_disabled_in_test_mode()
    
    # Don't initialize if PostHog is disabled (test mode)
    if posthog.disabled:
        return
        
    if not is_telemetry_enabled():
        return

    # Skip initialization if no valid API key (empty or placeholder)
    if not POSTHOG_API_KEY or POSTHOG_API_KEY.startswith("phc_YOUR"):
        return

    try:
        posthog.project_api_key = POSTHOG_API_KEY
        posthog.host = POSTHOG_HOST

        # Disable PostHog's own logging to avoid noise
        posthog.disabled = False
        posthog.debug = False

    except Exception:
        # Telemetry should never break the application
        pass


def track_event(event_name: str, properties: dict[str, Any] | None = None) -> None:
    """Track an anonymous event with minimal data.

    Args:
        event_name: Name of the event (e.g., "cli_init", "cli_build")
        properties: Optional properties to include with the event
    """
    global _user_identified

    # Ensure PostHog is disabled in test mode
    _ensure_posthog_disabled_in_test_mode()

    # Early return if PostHog is disabled (test mode)
    if posthog.disabled:
        return

    if not is_telemetry_enabled():
        return

    # Skip if no valid API key (empty or placeholder)
    if not POSTHOG_API_KEY or POSTHOG_API_KEY.startswith("phc_YOUR"):
        return

    try:
        # Initialize if needed
        if posthog.project_api_key != POSTHOG_API_KEY:
            initialize_telemetry()

        # Get anonymous ID
        anonymous_id = get_anonymous_id()

        # Only identify the user once per session
        if not _user_identified:
            # Set person properties to differentiate installations
            # Only include non-identifying information
            person_properties = {
                "$set": {
                    "golf_version": __version__,
                    "os": platform.system(),
                    "python_version": f"{platform.python_version_tuple()[0]}.{platform.python_version_tuple()[1]}",
                }
            }

            # Identify the user with properties
            posthog.identify(distinct_id=anonymous_id, properties=person_properties)

            _user_identified = True

        # Only include minimal, non-identifying properties
        safe_properties = {
            "golf_version": __version__,
            "python_version": f"{platform.python_version_tuple()[0]}.{platform.python_version_tuple()[1]}",
            "os": platform.system(),
            # Explicitly disable IP tracking
            "$ip": None,
        }

        # Filter properties to only include safe ones
        if properties:
            # Only include specific safe properties
            safe_keys = {
                "success",
                "environment",
                "template",
                "command_type",
                "error_type",
                "error_message",
            }
            for key in safe_keys:
                if key in properties:
                    safe_properties[key] = properties[key]

        # Send event
        posthog.capture(
            distinct_id=anonymous_id,
            event=event_name,
            properties=safe_properties,
        )

    except Exception:
        # Telemetry should never break the application
        pass


def track_command(
    command: str,
    success: bool = True,
    error_type: str | None = None,
    error_message: str | None = None,
) -> None:
    """Track a CLI command execution with minimal info.

    Args:
        command: The command being executed (e.g., "init", "build", "run")
        success: Whether the command was successful
        error_type: Type of error if command failed (e.g., "ValueError", "FileNotFoundError")
        error_message: Sanitized error message (no sensitive data)
    """
    properties = {"success": success}

    # Add error details if command failed
    if not success and (error_type or error_message):
        if error_type:
            properties["error_type"] = error_type
        if error_message:
            # Sanitize error message - remove file paths and sensitive info
            sanitized_message = _sanitize_error_message(error_message)
            properties["error_message"] = sanitized_message

    track_event(f"cli_{command}", properties)


def _sanitize_error_message(message: str) -> str:
    """Sanitize error message to remove sensitive information.

    Args:
        message: Raw error message

    Returns:
        Sanitized error message
    """
    import re

    # Remove absolute file paths but keep the filename
    # Unix-style paths
    message = re.sub(
        r'/(?:Users|home|var|tmp|opt|usr|etc)/[^\s"\']+/([^/\s"\']+)', r"\1", message
    )
    # Windows-style paths
    message = re.sub(r'[A-Za-z]:\\[^\s"\']+\\([^\\s"\']+)', r"\1", message)
    # Generic path pattern (catches remaining paths)
    message = re.sub(r'(?:^|[\s"])(/[^\s"\']+/)+([^/\s"\']+)', r"\2", message)

    # Remove potential API keys or tokens (common patterns)
    # Generic API keys (20+ alphanumeric with underscores/hyphens)
    message = re.sub(r"\b[a-zA-Z0-9_-]{32,}\b", "[REDACTED]", message)
    # Bearer tokens
    message = re.sub(r"Bearer\s+[a-zA-Z0-9_.-]+", "Bearer [REDACTED]", message)

    # Remove email addresses
    message = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", message
    )

    # Remove IP addresses
    message = re.sub(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "[IP]", message)

    # Remove port numbers in URLs
    message = re.sub(r":[0-9]{2,5}(?=/|$|\s)", ":[PORT]", message)

    # Truncate to reasonable length
    if len(message) > 200:
        message = message[:197] + "..."

    return message


def flush() -> None:
    """Flush any pending telemetry events."""
    if not is_telemetry_enabled():
        return

    try:
        posthog.flush()
    except Exception:
        # Ignore flush errors
        pass


def shutdown() -> None:
    """Shutdown telemetry and flush pending events."""
    if not is_telemetry_enabled():
        return

    try:
        posthog.shutdown()
    except Exception:
        # Ignore shutdown errors
        pass
