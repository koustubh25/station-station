"""Output management and incremental processing for Myki Attendance Tracker.

Handles loading existing output, filtering new transactions, updating user data, and saving output.
"""

import json
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from working_days import is_working_day


def calculate_statistics(
    attendance_days: List[str],
    start_date: date,
    end_date: date,
    skip_dates: List[date],
    vic_holidays,
    manual_attendance_dates: List[str] = None
) -> Dict:
    """Calculate attendance statistics for a user.

    Args:
        attendance_days: List of ISO date strings when user attended (PTV-detected)
        start_date: Period start date
        end_date: Period end date
        skip_dates: Dates to exclude from working days
        vic_holidays: Melbourne VIC holidays object
        manual_attendance_dates: List of ISO date strings for manually recorded attendance (optional)

    Returns:
        Dictionary containing overall and monthly statistics

    Note:
        Manual attendance dates are included in total attendance calculations.
    """
    # Convert attendance days to date objects for easier processing
    attendance_date_objects = [
        datetime.strptime(day, '%Y-%m-%d').date() for day in attendance_days
    ]

    # Convert manual attendance dates to date objects
    manual_date_objects = []
    if manual_attendance_dates:
        manual_date_objects = [
            datetime.strptime(day, '%Y-%m-%d').date() for day in manual_attendance_dates
        ]

    # Combine PTV and manual attendance dates for total calculation
    all_attendance_dates = attendance_date_objects + manual_date_objects

    # Calculate total working days and build monthly working days map
    total_working_days = 0
    monthly_working_days = {}  # {month_key: count}
    current_date = start_date

    while current_date <= end_date:
        if is_working_day(current_date, skip_dates, vic_holidays):
            total_working_days += 1

            # Track monthly working days
            month_key = current_date.strftime('%Y-%m')
            monthly_working_days[month_key] = monthly_working_days.get(month_key, 0) + 1

        current_date += timedelta(days=1)

    # Calculate attendance stats (include manual attendance in total)
    days_attended = len(all_attendance_dates)
    days_missed = max(0, total_working_days - days_attended)

    # Calculate overall percentage (avoid division by zero)
    if total_working_days > 0:
        attendance_percentage = round((days_attended / total_working_days) * 100, 2)
    else:
        attendance_percentage = 0.0

    # Get first and last attendance dates
    first_attendance = attendance_days[0] if attendance_days else None
    last_attendance = attendance_days[-1] if attendance_days else None

    # Calculate monthly statistics (include both PTV and manual attendance)
    monthly_attendance = {}  # {month_key: [attendance_dates]}
    for att_date in all_attendance_dates:
        month_key = att_date.strftime('%Y-%m')
        if month_key not in monthly_attendance:
            monthly_attendance[month_key] = []
        monthly_attendance[month_key].append(att_date)

    # Build monthly statistics array
    monthly_stats = []
    for month_key in sorted(monthly_working_days.keys()):
        working_days_in_month = monthly_working_days[month_key]
        attended_days_in_month = len(monthly_attendance.get(month_key, []))
        missed_days_in_month = working_days_in_month - attended_days_in_month

        # Calculate monthly percentage
        if working_days_in_month > 0:
            monthly_percentage = round((attended_days_in_month / working_days_in_month) * 100, 2)
        else:
            monthly_percentage = 0.0

        monthly_stats.append({
            "month": month_key,
            "workingDays": working_days_in_month,
            "daysAttended": attended_days_in_month,
            "daysMissed": missed_days_in_month,
            "attendancePercentage": monthly_percentage
        })

    return {
        "totalWorkingDays": total_working_days,
        "daysAttended": days_attended,
        "daysMissed": days_missed,
        "attendancePercentage": attendance_percentage,
        "firstAttendance": first_attendance,
        "lastAttendance": last_attendance,
        "periodStart": start_date.strftime('%Y-%m-%d'),
        "periodEnd": end_date.strftime('%Y-%m-%d'),
        "monthlyBreakdown": monthly_stats
    }


def load_existing_output(output_path: str = "output/attendance.json") -> Dict:
    """Load existing output JSON file for incremental processing.

    Args:
        output_path: Path to output JSON file (default: output/attendance.json)

    Returns:
        Dictionary containing existing output data.
        Returns empty dict {} if file doesn't exist.
        Returns empty dict {} if file contains malformed JSON (logs warning).

    Example:
        >>> existing = load_existing_output()
        >>> if "koustubh" in existing:
        ...     print(f"Found existing data for koustubh")
    """
    path = Path(output_path)

    # If file doesn't exist, return empty dict (first run)
    if not path.exists():
        print(f"No existing output file found at: {path.absolute()}")
        print("This is the first run - will process all transactions")
        return {}

    # File exists - try to load it
    try:
        with open(path, 'r') as f:
            output_data = json.load(f)

        print(f"Loaded existing output from: {path.absolute()}")

        # Count users in existing output (exclude metadata)
        user_count = len([k for k in output_data.keys() if k != "metadata"])
        print(f"Found existing data for {user_count} user(s)")

        return output_data

    except json.JSONDecodeError as e:
        # Malformed JSON - log warning and return empty dict
        print(f"WARNING: Existing output file contains malformed JSON: {e}")
        print(f"  File: {path.absolute()}")
        print(f"  Error: {e.msg} at position {e.pos}")
        print("  Returning empty dict - will overwrite file on save")
        return {}

    except Exception as e:
        # Other unexpected errors
        print(f"WARNING: Unexpected error loading existing output: {e}")
        print(f"  File: {path.absolute()}")
        print("  Returning empty dict - will overwrite file on save")
        return {}


def get_latest_processed_date(existing_output: Dict, username: str) -> Optional[datetime]:
    """Extract latestProcessedDate for a user from existing output.

    Args:
        existing_output: Dictionary containing existing output data
        username: Username to get latest processed date for

    Returns:
        datetime object representing latest processed transaction datetime.
        Returns None if:
        - Username doesn't exist in existing output (new user)
        - latestProcessedDate field is null/None (first run for user)
        - latestProcessedDate field doesn't exist

    Example:
        >>> existing = {"koustubh": {"latestProcessedDate": "2025-05-17T18:30:00+10:00"}}
        >>> latest = get_latest_processed_date(existing, "koustubh")
        >>> print(latest)
        datetime(2025, 5, 17, 18, 30, 0, tzinfo=...)
    """
    # Check if user exists in output
    if username not in existing_output:
        print(f"  User '{username}' not found in existing output (new user)")
        return None

    user_data = existing_output[username]

    # Check if latestProcessedDate field exists
    if "latestProcessedDate" not in user_data:
        print(f"  No latestProcessedDate for user '{username}' (first run)")
        return None

    latest_date_str = user_data["latestProcessedDate"]

    # Check if latestProcessedDate is null/None
    if latest_date_str is None:
        print(f"  latestProcessedDate is null for user '{username}' (first run)")
        return None

    # Parse ISO datetime string to datetime object
    try:
        latest_datetime = datetime.fromisoformat(latest_date_str)
        print(f"  Latest processed date for '{username}': {latest_date_str}")
        return latest_datetime

    except (ValueError, AttributeError) as e:
        print(f"  WARNING: Invalid latestProcessedDate format for user '{username}': {latest_date_str}")
        print(f"  Error: {e}")
        print(f"  Treating as first run (returning None)")
        return None


def filter_new_transactions(
    transactions: List[Dict[str, Any]],
    latest_processed_date: Optional[datetime]
) -> List[Dict[str, Any]]:
    """Filter transactions to only those after latest_processed_date.

    Used for incremental processing - only process transactions that haven't
    been seen before. Compares transaction datetime with latest_processed_date.

    Args:
        transactions: List of transaction dictionaries from API
        latest_processed_date: datetime object representing latest processed transaction.
                              If None, returns all transactions (first run).

    Returns:
        List of transaction dictionaries where transactionDateTime > latest_processed_date.
        If latest_processed_date is None, returns all transactions unchanged.

    Note:
        Uses STRICT GREATER THAN (>), not >= to avoid reprocessing the latest transaction.

    Example:
        >>> transactions = [
        ...     {"transactionDateTime": "2025-05-15T17:00:00+10:00"},
        ...     {"transactionDateTime": "2025-05-17T17:00:00+10:00"}
        ... ]
        >>> latest = datetime.fromisoformat("2025-05-16T00:00:00+10:00")
        >>> new_txns = filter_new_transactions(transactions, latest)
        >>> len(new_txns)
        1  # Only the 05-17 transaction
    """
    # First run - no existing processed date
    if latest_processed_date is None:
        print(f"  No latest processed date - returning all {len(transactions)} transactions (first run)")
        return transactions

    # Incremental run - filter to only new transactions
    new_transactions = []

    for txn in transactions:
        try:
            txn_datetime_str = txn.get("transactionDateTime", "")
            txn_datetime = datetime.fromisoformat(txn_datetime_str)

            # Only include transactions AFTER latest processed date
            # Use strict > to avoid reprocessing the latest transaction
            if txn_datetime > latest_processed_date:
                new_transactions.append(txn)

        except (ValueError, AttributeError):
            # Skip transactions with invalid datetime format
            print(f"  Warning: Skipping transaction with invalid datetime: {txn.get('transactionDateTime')}")
            continue

    print(f"  Filtered to {len(new_transactions)} new transactions (after {latest_processed_date.isoformat()})")
    print(f"  Skipped {len(transactions) - len(new_transactions)} already-processed transactions")

    return new_transactions


def update_user_output(
    existing_output: Dict,
    username: str,
    new_attendance_days: List[str],
    latest_txn_datetime: Optional[datetime],
    target_station: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip_dates: Optional[List[date]] = None,
    vic_holidays = None,
    manual_attendance_dates: Optional[List[str]] = None
) -> Dict:
    """Update user output with new attendance data and calculate statistics.

    Merges new attendance days with existing days, updates latestProcessedDate,
    sets targetStation, calculates statistics, and updates lastUpdated timestamp.

    Args:
        existing_output: Dictionary containing existing output data
        username: Username to update
        new_attendance_days: List of new attendance day strings (YYYY-MM-DD)
        latest_txn_datetime: datetime of most recent transaction processed.
                            If None, keeps existing latestProcessedDate.
        target_station: Target station name for this user
        start_date: Period start date for statistics calculation (optional)
        end_date: Period end date for statistics calculation (optional)
        skip_dates: Dates to exclude from working days (optional)
        vic_holidays: Melbourne VIC holidays object (optional)

    Returns:
        Updated output dictionary with merged user data and statistics

    Logic:
        - Merges new_attendance_days with existing attendanceDays (no duplicates)
        - Sorts merged days in chronological order
        - Updates latestProcessedDate to max(existing, new)
        - Sets targetStation
        - Calculates statistics (if date range provided)
        - Sets lastUpdated to current ISO timestamp (UTC)

    Example:
        >>> existing = {"user1": {"attendanceDays": ["2025-05-15"]}}
        >>> new_days = ["2025-05-16", "2025-05-17"]
        >>> latest = datetime(2025, 5, 17, 18, 30)
        >>> output = update_user_output(existing, "user1", new_days, latest, "Test Station")
        >>> output["user1"]["attendanceDays"]
        ['2025-05-15', '2025-05-16', '2025-05-17']
    """
    # Make a copy of existing output to avoid mutating input
    updated_output = existing_output.copy()

    # Get existing user data or initialize empty
    if username in updated_output and updated_output[username] is not None:
        user_data = updated_output[username].copy()
    else:
        user_data = {
            "attendanceDays": [],
            "manualAttendanceDates": [],
            "latestProcessedDate": None,
            "targetStation": target_station,
            "lastUpdated": None
        }

    # Step 1: Merge attendance days (remove duplicates, sort)
    existing_days = user_data.get("attendanceDays", [])

    # Combine existing and new days
    all_days = existing_days + new_attendance_days

    # Remove duplicates by converting to set, then back to list
    unique_days = list(set(all_days))

    # Sort in chronological order
    unique_days.sort()

    user_data["attendanceDays"] = unique_days

    print(f"  Merged attendance days for '{username}':")
    print(f"    Existing: {len(existing_days)} days")
    print(f"    New: {len(new_attendance_days)} days")
    print(f"    Total unique: {len(unique_days)} days")

    # Step 2: Update latestProcessedDate (use max of existing and new)
    existing_latest_str = user_data.get("latestProcessedDate")

    if existing_latest_str is not None:
        try:
            existing_latest_dt = datetime.fromisoformat(existing_latest_str)
        except (ValueError, AttributeError):
            existing_latest_dt = None
    else:
        existing_latest_dt = None

    # Determine new latestProcessedDate
    if latest_txn_datetime is not None and existing_latest_dt is not None:
        # Both exist - use the maximum
        new_latest_dt = max(existing_latest_dt, latest_txn_datetime)
    elif latest_txn_datetime is not None:
        # Only new exists
        new_latest_dt = latest_txn_datetime
    elif existing_latest_dt is not None:
        # Only existing exists
        new_latest_dt = existing_latest_dt
    else:
        # Neither exists
        new_latest_dt = None

    # Convert to ISO string
    if new_latest_dt is not None:
        user_data["latestProcessedDate"] = new_latest_dt.isoformat()
        print(f"    Updated latestProcessedDate: {user_data['latestProcessedDate']}")
    else:
        user_data["latestProcessedDate"] = None
        print(f"    latestProcessedDate: null (no transactions processed)")

    # Step 3: Set targetStation
    user_data["targetStation"] = target_station

    # Step 4: Set lastUpdated to current timestamp (ISO format, UTC)
    current_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    user_data["lastUpdated"] = current_timestamp
    print(f"    Updated lastUpdated: {current_timestamp}")

    # Step 5: Add skip dates to output (convert date objects to ISO strings)
    if skip_dates is not None:
        skip_dates_iso = [d.strftime('%Y-%m-%d') for d in skip_dates]
        skip_dates_iso.sort()  # Sort chronologically
        user_data["skipDates"] = skip_dates_iso
        print(f"    Added {len(skip_dates_iso)} skip dates to output")

    # Step 5.5: Add manual attendance dates to output (sorted chronologically)
    if manual_attendance_dates is not None and len(manual_attendance_dates) > 0:
        manual_dates_sorted = sorted(manual_attendance_dates)
        user_data["manualAttendanceDates"] = manual_dates_sorted
        print(f"    Added {len(manual_dates_sorted)} manual attendance dates to output")
    else:
        user_data["manualAttendanceDates"] = []

    # Step 6: Calculate statistics (if date range provided)
    if start_date is not None and end_date is not None and skip_dates is not None and vic_holidays is not None:
        # Use manual_attendance_dates if provided, otherwise empty list
        manual_dates = manual_attendance_dates if manual_attendance_dates is not None else []
        statistics = calculate_statistics(
            attendance_days=unique_days,
            start_date=start_date,
            end_date=end_date,
            skip_dates=skip_dates,
            vic_holidays=vic_holidays,
            manual_attendance_dates=manual_dates
        )
        user_data["statistics"] = statistics
        print(f"  Statistics:")
        print(f"    Total working days: {statistics['totalWorkingDays']}")
        print(f"    Days attended: {statistics['daysAttended']}")
        print(f"    Days missed: {statistics['daysMissed']}")
        print(f"    Attendance rate: {statistics['attendancePercentage']}%")

    # Update the output dictionary
    updated_output[username] = user_data

    return updated_output


def save_output(
    output_data: Dict,
    output_path: str = "output/attendance.json",
    config_path: str = "config/myki_tracker_config.json"
) -> None:
    """Save output data to JSON file with metadata.

    Creates output directory if it doesn't exist. Adds metadata section
    with generatedAt timestamp, config path, and user count. Writes JSON
    with proper formatting (indent=2) for human readability.

    Args:
        output_data: Dictionary containing user output data
        output_path: Path to output JSON file (default: output/attendance.json)
        config_path: Path to config file used (for metadata)

    Output Structure:
        {
            "metadata": {
                "generatedAt": "2025-11-01T14:30:00Z",
                "configPath": "config/myki_tracker_config.json",
                "totalUsers": 1
            },
            "username": {
                "attendanceDays": ["2025-04-15", "2025-04-16"],
                "latestProcessedDate": "2025-04-17T18:30:00+10:00",
                "targetStation": "Heathmont Station",
                "lastUpdated": "2025-11-01T14:30:00Z"
            }
        }

    Example:
        >>> output = {"koustubh": {"attendanceDays": ["2025-05-15"]}}
        >>> save_output(output, "output/attendance.json")
        Saved output to: /path/to/output/attendance.json
    """
    path = Path(output_path)

    # Create output directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nSaving output to: {path.absolute()}")

    # Count users (exclude metadata key if already present)
    user_count = len([k for k in output_data.keys() if k != "metadata"])

    # Add metadata section
    output_with_metadata = {
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "configPath": config_path,
            "totalUsers": user_count
        }
    }

    # Add all user data (preserve existing order)
    for username, user_data in output_data.items():
        if username != "metadata":  # Skip metadata if already in output_data
            output_with_metadata[username] = user_data

    # Write JSON with proper formatting (indent=2 for readability)
    try:
        with open(path, 'w') as f:
            json.dump(output_with_metadata, f, indent=2)

        print(f"✓ Successfully saved output for {user_count} user(s)")
        print(f"  File: {path.absolute()}")
        print(f"  Size: {path.stat().st_size} bytes")

    except Exception as e:
        print(f"✗ ERROR: Failed to save output file")
        print(f"  File: {path.absolute()}")
        print(f"  Error: {e}")
        raise  # Re-raise to allow caller to handle
