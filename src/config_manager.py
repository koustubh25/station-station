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
        Required fields: targetStation, startDate
        Optional fields: username (for display), endDate (defaults to current date), skipDates (defaults to empty array).
        The config key itself (e.g., "koustubh") maps to environment variables for credentials.

        SECURITY: mykiCardNumber field is NOT ALLOWED in config - use environment variables instead.
    """
    from datetime import datetime

    required_fields = ["targetStation", "startDate"]
    forbidden_fields = ["mykiCardNumber"]

    for username, config in user_config.items():
        # Skip comment keys (those starting with underscore)
        if username.startswith("_"):
            continue

        # Check for forbidden fields (security)
        for field in forbidden_fields:
            if field in config:
                raise ValueError(
                    f"Field '{field}' is not allowed in config for user '{username}'. "
                    f"Security requirement: Use environment variable MYKI_CARDNUMBER_{username.upper()} instead. "
                    f"See .env.example for correct format."
                )

        # Check all required fields are present
        for field in required_fields:
            if field not in config:
                raise ValueError(
                    f"Missing required field '{field}' for user '{username}'"
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

        # Validate manualAttendanceDates (if provided)
        if "manualAttendanceDates" in config:
            # Must be a list
            if not isinstance(config["manualAttendanceDates"], list):
                raise ValueError(
                    f"Field 'manualAttendanceDates' must be an array for user '{username}'"
                )

            # Get date range for validation
            start_date = datetime.strptime(config["startDate"], '%Y-%m-%d').date()
            if "endDate" in config:
                end_date = datetime.strptime(config["endDate"], '%Y-%m-%d').date()
            else:
                # Default to current date if endDate not specified
                from datetime import date
                end_date = date.today()

            # Validate each date
            for manual_date_str in config["manualAttendanceDates"]:
                # Must be a string
                if not isinstance(manual_date_str, str):
                    raise ValueError(
                        f"All manualAttendanceDates must be strings for user '{username}'"
                    )

                # Validate date format
                try:
                    manual_date = datetime.strptime(manual_date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(
                        f"Invalid date format in manualAttendanceDates for user '{username}': '{manual_date_str}'. "
                        f"Expected ISO format (YYYY-MM-DD)"
                    )

                # Validate date is within range
                if manual_date < start_date:
                    raise ValueError(
                        f"Manual attendance date '{manual_date_str}' is before startDate '{config['startDate']}' "
                        f"for user '{username}'"
                    )

                if manual_date > end_date:
                    end_date_str = config.get("endDate", end_date.strftime('%Y-%m-%d'))
                    raise ValueError(
                        f"Manual attendance date '{manual_date_str}' is after endDate '{end_date_str}' "
                        f"for user '{username}'"
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
    """Get the effective skip dates for a user, with conflict resolution.

    Manual attendance dates take precedence over skip dates. If a date appears
    in both manualAttendanceDates and skipDates, it will be excluded from the
    effective skip dates (manual attendance wins).

    Args:
        user_config: Dictionary containing user configurations
        username: Username to get skip dates for

    Returns:
        List of skip date strings (YYYY-MM-DD) after conflict resolution.
        If skipDates not in config, returns empty list.
    """
    config = user_config[username]

    # Get skip dates
    skip_dates = config.get("skipDates", [])

    # Get manual attendance dates
    manual_dates = config.get("manualAttendanceDates", [])

    # If no manual dates, return skip dates as-is
    if not manual_dates:
        return skip_dates

    # Remove any skip dates that conflict with manual attendance dates
    # Manual attendance takes precedence
    effective_skip_dates = [d for d in skip_dates if d not in manual_dates]

    # Log if conflicts were resolved
    conflicts = set(skip_dates) & set(manual_dates)
    if conflicts:
        print(f"INFO: Resolved {len(conflicts)} conflict(s) for user '{username}': "
              f"Manual attendance overrides skip dates for: {sorted(conflicts)}")

    return effective_skip_dates


def load_user_credentials(user_config: Dict) -> Dict[str, Dict[str, str]]:
    """Load user credentials (username, card number, password) from environment variables.

    Args:
        user_config: Dictionary containing user configurations

    Returns:
        Dictionary mapping config key to credentials dict with keys:
            - username: Myki account username
            - card_number: Myki card number
            - password: Myki account password
            - display_username: Username for frontend display (from config or defaults to key)

    Raises:
        ValueError: If any required credential environment variables are missing

    Environment Variable Pattern:
        For config key "koustubh", environment variables must be:
        - MYKI_USERNAME_KOUSTUBH=actual_myki_username
        - MYKI_CARDNUMBER_KOUSTUBH=card_number
        - MYKI_PASSWORD_KOUSTUBH=password

    Note:
        Config key is converted to UPPERCASE for environment variable names.
        Example: "john_doe" -> MYKI_USERNAME_JOHN_DOE
    """
    credentials = {}
    missing_vars = []

    for config_key in user_config.keys():
        # Skip comment keys (those starting with underscore)
        if config_key.startswith("_"):
            continue

        # Convert config key to uppercase for environment variable names
        config_key_upper = config_key.upper()

        # Define required environment variable names
        env_var_username = f"MYKI_USERNAME_{config_key_upper}"
        env_var_cardnumber = f"MYKI_CARDNUMBER_{config_key_upper}"
        env_var_password = f"MYKI_PASSWORD_{config_key_upper}"

        # Load credentials from environment variables
        username = os.getenv(env_var_username)
        card_number = os.getenv(env_var_cardnumber)
        password = os.getenv(env_var_password)

        # Track missing variables
        if username is None:
            missing_vars.append(env_var_username)
        if card_number is None:
            missing_vars.append(env_var_cardnumber)
        if password is None:
            missing_vars.append(env_var_password)

        # If all credentials are present, store them
        if username and card_number and password:
            # Get display username from config or default to config key
            display_username = user_config[config_key].get("username", config_key)

            credentials[config_key] = {
                "username": username,
                "card_number": card_number,
                "password": password,
                "display_username": display_username
            }

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables for credentials:\n" +
            "\n".join(f"  - {var}" for var in missing_vars) +
            f"\n\nSee .env.example for correct format and variable naming pattern."
        )

    print(f"Loaded credentials for {len(credentials)} user(s)")
    return credentials
