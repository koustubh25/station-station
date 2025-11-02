"""Transaction processing and attendance calculation for Myki Attendance Tracker.

Handles filtering transactions and calculating attendance days.
"""

from datetime import date, datetime
from typing import List, Dict, Any

import holidays

from working_days import is_working_day


def parse_transaction_date(transaction_datetime: str) -> date:
    """Parse transaction datetime string to date object.

    Parses ISO 8601 datetime string from Myki API (format: "2025-10-29T13:04:45+11:00")
    and extracts just the date portion.

    Args:
        transaction_datetime: ISO 8601 datetime string with timezone
                             (e.g., "2025-10-29T13:04:45+11:00")

    Returns:
        date object representing the transaction date

    Raises:
        ValueError: If datetime string is in invalid format

    Example:
        >>> parse_transaction_date("2025-10-29T13:04:45+11:00")
        date(2025, 10, 29)
    """
    try:
        # Parse ISO 8601 datetime string with timezone
        # Format: "2025-10-29T13:04:45+11:00"
        dt = datetime.fromisoformat(transaction_datetime)

        # Extract just the date portion (ignore time)
        return dt.date()

    except (ValueError, AttributeError) as e:
        raise ValueError(
            f"Failed to parse transaction datetime: '{transaction_datetime}'. "
            f"Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SS+TZ). Error: {e}"
        )


def filter_transactions(
    transactions: List[Dict[str, Any]],
    target_station: str,
    start_date: date,
    end_date: date
) -> List[Dict[str, Any]]:
    """Filter transactions by station, type, and date range.

    Filters transaction list to only include:
    - Transactions at exact target station (case-sensitive match on 'description')
    - Transactions with transactionType == "Touch off"
    - Transactions within date range [start_date, end_date] (inclusive bounds)

    Args:
        transactions: List of transaction dictionaries from API
        target_station: Exact station name to match (case-sensitive)
                       (e.g., "Heathmont Station")
        start_date: Start date for filtering (inclusive)
        end_date: End date for filtering (inclusive)

    Returns:
        Filtered list of transaction dictionaries matching all criteria

    Example:
        >>> transactions = [
        ...     {"transactionType": "Touch off", "transactionDateTime": "2025-05-15T17:00:00+10:00",
        ...      "description": "Heathmont Station"},
        ...     {"transactionType": "Touch on", "transactionDateTime": "2025-05-15T08:00:00+10:00",
        ...      "description": "Heathmont Station"}
        ... ]
        >>> filtered = filter_transactions(transactions, "Heathmont Station",
        ...                                date(2025, 5, 1), date(2025, 5, 31))
        >>> len(filtered)
        1  # Only the "Touch off" transaction
    """
    filtered = []

    for txn in transactions:
        # Filter 1: Exact station name match (case-sensitive)
        if txn.get("description") != target_station:
            continue

        # Filter 2: Only "Touch off" transactions
        if txn.get("transactionType") != "Touch off":
            continue

        # Filter 3: Date range (inclusive bounds)
        try:
            txn_date = parse_transaction_date(txn.get("transactionDateTime", ""))

            # Check if within range (inclusive)
            if not (start_date <= txn_date <= end_date):
                continue

        except ValueError:
            # Skip transactions with invalid date format
            print(f"  Warning: Skipping transaction with invalid date: {txn.get('transactionDateTime')}")
            continue

        # All filters passed - include this transaction
        filtered.append(txn)

    return filtered


def calculate_attendance_days(
    transactions: List[Dict[str, Any]],
    skip_dates: List[date],
    vic_holidays: holidays.HolidayBase
) -> List[str]:
    """Calculate attendance days from filtered transactions.

    Extracts dates from transactions, filters to working days only, removes duplicates,
    and returns sorted list of attendance days as ISO date strings.

    Working day criteria:
    - Monday-Friday (weekdays)
    - NOT a Melbourne VIC public holiday
    - NOT in user's skip dates

    If a working day has >= 1 "Touch off" transaction, it counts as attended.

    Args:
        transactions: List of filtered transaction dictionaries (already filtered by
                     station, type, and date range)
        skip_dates: List of user skip dates as date objects
        vic_holidays: Melbourne VIC holidays object from holidays package

    Returns:
        List of ISO date strings (YYYY-MM-DD) representing attendance days,
        sorted in chronological order

    Example:
        >>> transactions = [
        ...     {"transactionDateTime": "2025-05-19T17:00:00+10:00"},  # Monday
        ...     {"transactionDateTime": "2025-05-19T17:30:00+10:00"},  # Monday (duplicate)
        ...     {"transactionDateTime": "2025-05-20T17:00:00+10:00"},  # Tuesday
        ...     {"transactionDateTime": "2025-05-24T17:00:00+10:00"}   # Saturday (weekend)
        ... ]
        >>> attendance = calculate_attendance_days(transactions, [], vic_holidays)
        >>> attendance
        ['2025-05-19', '2025-05-20']  # Only working days, no duplicates
    """
    # Step 1: Extract dates from transactions
    transaction_dates = []
    for txn in transactions:
        try:
            txn_date = parse_transaction_date(txn.get("transactionDateTime", ""))
            transaction_dates.append(txn_date)
        except ValueError:
            # Skip transactions with invalid dates
            continue

    # Step 2: Filter to working days only
    working_days = []
    for txn_date in transaction_dates:
        if is_working_day(txn_date, skip_dates, vic_holidays):
            working_days.append(txn_date)

    # Step 3: Remove duplicates (convert to set, then back to list)
    unique_working_days = list(set(working_days))

    # Step 4: Sort in chronological order
    unique_working_days.sort()

    # Step 5: Convert to ISO date strings (YYYY-MM-DD)
    attendance_days = [day.strftime('%Y-%m-%d') for day in unique_working_days]

    return attendance_days
