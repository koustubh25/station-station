"""Configuration management for Myki Attendance Tracker.

Handles loading, validating, and parsing user configuration files and environment variables.
Supports both unified config format (recommended) and legacy separate configs.
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple, Optional


def load_unified_config(config_path: str = "config/myki_config.json") -> Dict:
    """Load unified configuration file for multi-user tracking.

    Args:
        config_path: Path to unified config JSON file

    Returns:
        User config dictionary: {"user1": {...}, "user2": {...}}
        Each user has: mykiUsername, mykiCardNumber, targetStation, startDate, etc.

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config structure is invalid
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"  Create config file first (see config/myki_config.example.json)"
        )

    with open(path, 'r') as f:
        config = json.load(f)

    # Extract users config
    if "users" not in config:
        raise ValueError(
            "Invalid unified config: missing 'users' section\n"
            f"  See config/myki_config.example.json for correct format"
        )

    user_config = config["users"]

    # Filter out comment keys
    user_config = {k: v for k, v in user_config.items() if not k.startswith("_")}

    if not user_config:
        raise ValueError(
            "Invalid unified config: 'users' section is empty\n"
            f"  Add at least one user to track in {config_path}"
        )

    print(f"Loaded unified config from: {path.absolute()}")
    print(f"  Users to track: {len(user_config)}")

    return user_config


def load_user_config(config_path: str = "config/myki_tracker_config.json") -> Dict:
    """Load user configuration from JSON file.

    Args:
        config_path: Path to configuration file (default: config/myki_tracker_config.json)

    Returns:
        Dictionary containing user configurations

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file contains invalid JSON
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found at: {path.absolute()}\n"
            f"Create config file first. See config/myki_tracker_config.example.json for template."
        )

    try:
        with open(path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in config file: {e.msg}",
            e.doc,
            e.pos
        )

    print(f"Loaded config from: {path.absolute()}")
    return config


def validate_user_config(user_config: Dict) -> None:
    """Validate user configuration JSON schema and data formats.

    Args:
        user_config: Dictionary containing user configurations

    Raises:
        ValueError: If validation fails with specific error details

    Note:
        Required fields: mykiCardNumber, targetStation, startDate
        Optional fields: endDate (defaults to current date), skipDates (defaults to empty array).
        The config key itself (e.g., "koustubh") is used as the Myki username.
    """
    from datetime import datetime

    required_fields = ["mykiCardNumber", "targetStation", "startDate"]

    for username, config in user_config.items():
        # Skip comment keys (those starting with underscore)
        if username.startswith("_"):
            continue

        # Check all required fields are present
        for field in required_fields:
            if field not in config:
                raise ValueError(
                    f"Missing required field '{field}' for user '{username}'"
                )

        # Validate mykiCardNumber is a string
        if not isinstance(config["mykiCardNumber"], str):
            raise ValueError(
                f"Field 'mykiCardNumber' must be a string for user '{username}'"
            )

        # Validate targetStation is a string
        if not isinstance(config["targetStation"], str):
            raise ValueError(
                f"Field 'targetStation' must be a string for user '{username}'"
            )

        # Validate skipDates is a list (if provided)
        if "skipDates" in config:
            if not isinstance(config["skipDates"], list):
                raise ValueError(
                    f"Field 'skipDates' must be an array for user '{username}'"
                )

            # Validate date formats for skipDates
            for skip_date in config["skipDates"]:
                if not isinstance(skip_date, str):
                    raise ValueError(
                        f"All skipDates must be strings for user '{username}'"
                    )
                try:
                    datetime.strptime(skip_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(
                        f"Invalid date format in skipDates for user '{username}': '{skip_date}'. "
                        f"Expected ISO format (YYYY-MM-DD)"
                    )

        # Validate startDate format
        try:
            datetime.strptime(config["startDate"], '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                f"Invalid date format for startDate in user '{username}': '{config['startDate']}'. "
                f"Expected ISO format (YYYY-MM-DD)"
            )

        # Validate endDate format (if provided)
        if "endDate" in config:
            try:
                datetime.strptime(config["endDate"], '%Y-%m-%d')
            except ValueError:
                raise ValueError(
                    f"Invalid date format for endDate in user '{username}': '{config['endDate']}'. "
                    f"Expected ISO format (YYYY-MM-DD)"
                )

    print(f"Config validation passed for {len([k for k in user_config.keys() if not k.startswith('_')])} user(s)")


def get_effective_end_date(user_config: Dict, username: str) -> str:
    """Get the effective end date for a user.

    Args:
        user_config: Dictionary containing user configurations
        username: Username to get end date for

    Returns:
        End date as ISO string (YYYY-MM-DD). If endDate not in config, returns current date.
    """
    from datetime import date

    config = user_config[username]
    if "endDate" in config:
        return config["endDate"]
    else:
        # Default to current date if not specified
        return date.today().strftime('%Y-%m-%d')


def get_effective_skip_dates(user_config: Dict, username: str) -> list:
    """Get the effective skip dates for a user.

    Args:
        user_config: Dictionary containing user configurations
        username: Username to get skip dates for

    Returns:
        List of skip date strings (YYYY-MM-DD). If skipDates not in config, returns empty list.
    """
    config = user_config[username]
    if "skipDates" in config:
        return config["skipDates"]
    else:
        # Default to empty list if not specified
        return []


def load_user_passwords(user_config: Dict) -> Dict[str, str]:
    """Load user passwords from environment variables.

    Args:
        user_config: Dictionary containing user configurations

    Returns:
        Dictionary mapping username to password

    Raises:
        ValueError: If any required password environment variables are missing
    """
    passwords = {}
    missing_passwords = []

    for username in user_config.keys():
        # Skip comment keys (those starting with underscore)
        if username.startswith("_"):
            continue

        env_var_name = f"MYKI_PASSWORD_{username.upper()}"
        password = os.getenv(env_var_name)

        if password is None:
            missing_passwords.append(env_var_name)
        else:
            passwords[username] = password

    if missing_passwords:
        raise ValueError(
            f"Missing required environment variables for passwords:\n" +
            "\n".join(f"  - {var}" for var in missing_passwords) +
            f"\n\nSet these environment variables before running the tracker."
        )

    print(f"Loaded passwords for {len(passwords)} user(s)")
    return passwords
