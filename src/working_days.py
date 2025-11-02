"""Working days calculation for Myki Attendance Tracker.

Handles calculation of working days, excluding weekends, public holidays, and user skip dates.
"""

from datetime import date, datetime
from typing import List

import holidays


# Initialize Melbourne VIC holidays at module level for reuse
VIC_HOLIDAYS = holidays.country_holidays('AU', subdiv='VIC')


def is_working_day(date_obj: date, skip_dates: List[date], vic_holidays: holidays.HolidayBase) -> bool:
    """Determine if a given date is a working day.

    Working day is defined as:
    - Monday through Friday (weekday() returns 0-4)
    - AND NOT a Melbourne VIC public holiday
    - AND NOT in user skip dates

    Args:
        date_obj: Date to check (date object, not datetime)
        skip_dates: List of user skip dates as date objects
        vic_holidays: Melbourne VIC holidays object from holidays package

    Returns:
        True if working day, False otherwise
    """
    # Check if it's a weekday (Monday=0 to Friday=4)
    is_weekday = date_obj.weekday() in range(0, 5)

    # Check if it's NOT a public holiday
    is_not_holiday = date_obj not in vic_holidays

    # Check if it's NOT in skip dates
    is_not_skipped = date_obj not in skip_dates

    # Working day = weekday AND NOT holiday AND NOT skipped
    return is_weekday and is_not_holiday and is_not_skipped


def parse_skip_dates(skip_dates_str: List[str]) -> List[date]:
    """Parse skip dates from ISO string format to date objects.

    Args:
        skip_dates_str: List of ISO date strings (YYYY-MM-DD)

    Returns:
        List of date objects

    Raises:
        ValueError: If any date string is in invalid format
    """
    skip_dates_obj = []

    for date_str in skip_dates_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            skip_dates_obj.append(date_obj)
        except ValueError:
            raise ValueError(
                f"Failed to parse skip date '{date_str}'. "
                f"Expected ISO format (YYYY-MM-DD)"
            )

    return skip_dates_obj
