"""Myki Transaction Tracker - Work Attendance Monitor.

This module tracks work attendance by monitoring Myki "Touch off" events
at designated stations for multiple users.

Main orchestration and CLI entry point.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Tuple, Optional

import requests

from myki_api_client import MykiAPIClient
from config_manager import (
    load_unified_config,
    validate_user_config,
    load_user_credentials,
    get_effective_end_date,
    get_effective_skip_dates
)
from working_days import VIC_HOLIDAYS, parse_skip_dates
from transaction_fetcher import fetch_all_transactions
from transaction_processor import filter_transactions, calculate_attendance_days
from output_manager import (
    load_existing_output,
    get_latest_processed_date,
    filter_new_transactions,
    update_user_output,
    save_output
)


def process_user(
    username: str,
    user_config: Dict,
    user_credentials: Dict,
    client: MykiAPIClient,
    existing_output: Dict,
    vic_holidays
) -> Tuple[bool, Optional[Dict], Optional[Exception]]:
    """Process a single user's attendance tracking.

    Orchestrates all steps for one user:
    1. Parse user config (station, dates, skip dates) and credentials (card number)
    2. Fetch all transactions (handle pagination)
    3. Filter new transactions (incremental processing)
    4. Filter by station, type, and date range
    5. Calculate attendance days (working days only)
    6. Update output data for user

    Args:
        username: Username (key in config)
        user_config: User configuration dictionary
        user_credentials: User credentials dictionary with card_number, username, password
        client: MykiAPIClient instance (reused across users)
        existing_output: Existing output data for incremental processing
        vic_holidays: Melbourne VIC holidays object

    Returns:
        Tuple of (success: bool, user_output_data: dict or None, error: Exception or None)
        - If success: (True, updated_output_dict, None)
        - If failure: (False, None, exception_object)

    Note:
        Catches all exceptions within function and returns them (doesn't raise).
        Uses print statements for user-friendly logging at each step.
    """
    try:
        print(f"\n{'=' * 60}")
        print(f"Processing user: {username}")
        print(f"{'=' * 60}")

        # Step 1: Parse user config and credentials
        card_number = user_credentials["card_number"]
        target_station = user_config["targetStation"]
        start_date_str = user_config["startDate"]
        end_date_str = get_effective_end_date({username: user_config}, username)
        skip_dates_str = get_effective_skip_dates({username: user_config}, username)
        manual_attendance_dates = user_config.get("manualAttendanceDates", [])

        print(f"Configuration:")
        print(f"  Card Number: {card_number}")
        print(f"  Target Station: {target_station}")
        print(f"  Date Range: {start_date_str} to {end_date_str}")
        print(f"  Skip Dates: {len(skip_dates_str)} day(s)")
        print(f"  Manual Attendance Dates: {len(manual_attendance_dates)} day(s)")

        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        skip_dates = parse_skip_dates(skip_dates_str)

        # Step 2: Fetch all transactions (handle pagination)
        all_transactions = fetch_all_transactions(client, card_number)

        # Step 3: Get latest processed date and filter new transactions
        print(f"\nIncremental Processing:")
        latest_processed_date = get_latest_processed_date(existing_output, username)
        new_transactions = filter_new_transactions(all_transactions, latest_processed_date)

        # Step 4: Filter by station, type, and date range
        print(f"\nFiltering Transactions:")
        filtered_transactions = filter_transactions(
            transactions=new_transactions,
            target_station=target_station,
            start_date=start_date,
            end_date=end_date
        )
        print(f"  Filtered to {len(filtered_transactions)} relevant transactions")
        print(f"    (Touch off at '{target_station}' within date range)")

        # Step 5: Calculate attendance days (working days only)
        print(f"\nCalculating Attendance Days:")
        attendance_days = calculate_attendance_days(
            transactions=filtered_transactions,
            skip_dates=skip_dates,
            vic_holidays=vic_holidays
        )
        print(f"  Found {len(attendance_days)} working day(s) with attendance")

        # Determine latest transaction datetime from filtered transactions
        latest_txn_datetime = None
        if filtered_transactions:
            # Get the latest datetime from filtered transactions
            latest_txn_datetime_str = max(
                txn["transactionDateTime"] for txn in filtered_transactions
            )
            latest_txn_datetime = datetime.fromisoformat(latest_txn_datetime_str)

        # Step 6: Update output data for user
        print(f"\nUpdating Output:")
        updated_output = update_user_output(
            existing_output=existing_output,
            username=username,
            new_attendance_days=attendance_days,
            latest_txn_datetime=latest_txn_datetime,
            target_station=target_station,
            start_date=start_date,
            end_date=end_date,
            skip_dates=skip_dates,
            vic_holidays=vic_holidays,
            manual_attendance_dates=manual_attendance_dates
        )

        print(f"\n✓ Successfully processed user: {username}")
        return (True, updated_output, None)

    except Exception as e:
        print(f"\n✗ ERROR processing user '{username}': {type(e).__name__}")
        print(f"  Details: {str(e)}")
        return (False, None, e)


def main() -> int:
    """Main orchestration function for multi-user attendance tracking.

    Orchestrates:
    - Load and validate user config
    - Initialize MykiAPIClient once (reuse for all users)
    - Initialize Melbourne VIC holidays object
    - Load existing output file
    - Loop through all users sequentially
    - Collect successes and failures
    - Merge all successful user outputs
    - Save combined output file
    - Print summary

    Returns:
        Exit code: 0 if all users succeed, 1 if any failures

    Note:
        - Uses saved session from Phase 1 authentication (no passwords needed)
        - Uses print statements for logging (no complex framework)
        - Follows fail-fast for missing config/invalid schema
        - Follows graceful degradation for per-user API failures
        - One user's failure doesn't prevent other users from processing
    """
    print("=" * 80)
    print("Myki Attendance Tracker - Work Attendance Monitor")
    print("=" * 80)

    try:
        # Step 1: Get config path from CLI argument or use default
        if len(sys.argv) > 1:
            config_path = sys.argv[1]
        else:
            config_path = "config/myki_tracker_config.json"

        print(f"\nConfiguration file: {config_path}")

        # Step 2: Load and validate user config
        print("\n" + "-" * 80)
        print("Loading Configuration")
        print("-" * 80)

        user_config = load_unified_config(config_path)
        validate_user_config(user_config)

        # Step 2.5: Load user credentials from environment variables
        print("\n" + "-" * 80)
        print("Loading Credentials")
        print("-" * 80)

        user_credentials = load_user_credentials(user_config)

        # Step 3: Initialize MykiAPIClient once (reuse for all users)
        print("\n" + "-" * 80)
        print("Initializing Myki API Client")
        print("-" * 80)
        client = MykiAPIClient()
        print("✓ MykiAPIClient initialized (session auto-loaded)")

        # Step 4: Initialize Melbourne VIC holidays object
        vic_holidays = VIC_HOLIDAYS

        # Step 5: Load existing output file
        print("\n" + "-" * 80)
        print("Loading Existing Output")
        print("-" * 80)
        # Support environment variable override for Docker permission issues
        output_path = os.path.join(os.getenv('OUTPUT_DIR', 'output'), 'attendance.json')
        existing_output = load_existing_output(output_path)

        # Step 6: Initialize results tracking
        successes = []
        failures = []

        # Step 7: Loop through all users sequentially
        print("\n" + "-" * 80)
        print("Processing Users")
        print("-" * 80)

        # Filter out comment keys (those starting with underscore)
        usernames = [k for k in user_config.keys() if not k.startswith("_")]

        for username in usernames:
            user_cfg = user_config[username]
            user_creds = user_credentials[username]

            # Set environment variable for session file lookup (multi-user support)
            os.environ['MYKI_AUTH_USERNAME_KEY'] = username

            # Process user (catch all exceptions)
            # Note: Passwords not needed - MykiAPIClient uses saved session from Phase 1
            success, user_output, error = process_user(
                username=username,
                user_config=user_cfg,
                user_credentials=user_creds,
                client=client,
                existing_output=existing_output,
                vic_holidays=vic_holidays
            )

            if success:
                successes.append((username, user_output))
                # Merge user output into existing_output for next user
                if user_output is not None:
                    existing_output = user_output
            else:
                failures.append((username, error))

        # Step 8: Merge all successful user outputs
        if successes:
            # The last successful user output contains all merged data
            final_output = successes[-1][1] if successes else {}

            # Step 9: Save combined output file
            if final_output is not None:
                print("\n" + "-" * 80)
                print("Saving Output")
                print("-" * 80)
                save_output(final_output, output_path=output_path, config_path=config_path)

        # Step 10: Print summary
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)

        total_users = len(usernames)
        success_count = len(successes)
        failure_count = len(failures)

        print(f"Total users: {total_users}")
        print(f"  ✓ Successful: {success_count}")
        print(f"  ✗ Failed: {failure_count}")

        # Step 11: Print error details for failures
        if failures:
            print("\n" + "-" * 80)
            print("Error Details")
            print("-" * 80)

            for username, error in failures:
                print(f"\nUser: {username}")
                print(f"  Error Type: {type(error).__name__}")
                print(f"  Error Message: {str(error)}")

                # Add specific guidance based on error type
                if isinstance(error, requests.HTTPError):
                    if hasattr(error, 'response') and error.response:
                        print(f"  HTTP Status: {error.response.status_code}")
                        print(f"  Suggestion: Check API connectivity and authentication")
                elif isinstance(error, ValueError):
                    print(f"  Suggestion: Check configuration file for invalid values")
                elif isinstance(error, KeyError):
                    print(f"  Suggestion: Check configuration file for missing required fields")

        # Step 12: Return exit code
        if failure_count > 0:
            print("\n" + "=" * 80)
            print("⚠ COMPLETED WITH ERRORS - Some users failed to process")
            print("=" * 80)
            return 1  # Exit code 1 indicates failures
        else:
            print("\n" + "=" * 80)
            print("✓ COMPLETED SUCCESSFULLY - All users processed")
            print("=" * 80)
            return 0  # Exit code 0 indicates success

    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {str(e)}")
        return 1
    except json.JSONDecodeError as e:
        print(f"\n✗ ERROR: Malformed JSON in config file")
        print(f"  Details: {e.msg} at position {e.pos}")
        return 1
    except ValueError as e:
        print(f"\n✗ ERROR: Configuration validation failed")
        print(f"  Details: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {type(e).__name__}")
        print(f"  Details: {str(e)}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
