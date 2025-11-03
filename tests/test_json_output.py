"""Tests for JSON output structure with manual attendance dates.

Task Group 3: Backend JSON Output Structure Changes
- Test manualAttendanceDates appears as separate top-level field
- Test attendanceDays remains separate from manual dates
- Test statistics calculations include manual dates
- Test empty manualAttendanceDates array when no manual dates specified
"""

import pytest
from datetime import date, datetime
from src.output_manager import update_user_output, calculate_statistics


class TestJSONOutputStructure:
    """Test JSON output structure with manual attendance dates."""

    def test_manualAttendanceDates_field_present(self):
        """Test that manualAttendanceDates appears as separate top-level field in output."""
        from working_days import VIC_HOLIDAYS

        existing_output = {}

        updated_output = update_user_output(
            existing_output=existing_output,
            username="testuser",
            new_attendance_days=[],
            latest_txn_datetime=None,
            target_station="Test Station",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip_dates=[],
            vic_holidays=VIC_HOLIDAYS,
            manual_attendance_dates=["2025-01-15", "2025-01-20"]
        )

        # Check that manualAttendanceDates field exists
        assert "manualAttendanceDates" in updated_output["testuser"]

        # Check that it contains the manual dates
        assert updated_output["testuser"]["manualAttendanceDates"] == ["2025-01-15", "2025-01-20"]

    def test_attendanceDays_separate_from_manual_dates(self):
        """Test that attendanceDays and manualAttendanceDates are kept separate."""
        from working_days import VIC_HOLIDAYS

        existing_output = {}

        # PTV attendance on 2025-01-10, manual attendance on 2025-01-15
        updated_output = update_user_output(
            existing_output=existing_output,
            username="testuser",
            new_attendance_days=["2025-01-10"],  # Pass as string
            latest_txn_datetime=datetime(2025, 1, 10, 18, 30),
            target_station="Test Station",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip_dates=[],
            vic_holidays=VIC_HOLIDAYS,
            manual_attendance_dates=["2025-01-15"]
        )

        user_data = updated_output["testuser"]

        # attendanceDays should only have PTV dates
        assert len(user_data["attendanceDays"]) == 1
        assert user_data["attendanceDays"][0] == "2025-01-10"

        # manualAttendanceDates should only have manual dates
        assert user_data["manualAttendanceDates"] == ["2025-01-15"]

    def test_empty_manualAttendanceDates_when_not_specified(self):
        """Test that manualAttendanceDates is empty array when no manual dates specified."""
        from working_days import VIC_HOLIDAYS

        existing_output = {}

        updated_output = update_user_output(
            existing_output=existing_output,
            username="testuser",
            new_attendance_days=[],
            latest_txn_datetime=None,
            target_station="Test Station",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip_dates=[],
            vic_holidays=VIC_HOLIDAYS,
            manual_attendance_dates=[]
        )

        # Should have empty array, not missing field
        assert "manualAttendanceDates" in updated_output["testuser"]
        assert updated_output["testuser"]["manualAttendanceDates"] == []

    def test_statistics_include_manual_dates(self):
        """Test that statistics calculations include manual attendance dates."""
        from working_days import VIC_HOLIDAYS

        # 2 PTV dates + 2 manual dates = 4 total attendance days
        attendance_days = ["2025-01-10", "2025-01-12"]  # Pass as strings not dicts
        manual_dates = ["2025-01-15", "2025-01-20"]

        stats = calculate_statistics(
            attendance_days=attendance_days,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip_dates=[],
            vic_holidays=VIC_HOLIDAYS,
            manual_attendance_dates=manual_dates
        )

        # Total attendance should be 4 (2 PTV + 2 manual)
        assert stats["daysAttended"] == 4

    def test_statistics_without_manual_dates(self):
        """Test that statistics work correctly when no manual dates provided."""
        from working_days import VIC_HOLIDAYS

        # 2 PTV dates, 0 manual dates = 2 total
        attendance_days = ["2025-01-10", "2025-01-12"]  # Pass as strings not dicts

        stats = calculate_statistics(
            attendance_days=attendance_days,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip_dates=[],
            vic_holidays=VIC_HOLIDAYS,
            manual_attendance_dates=[]
        )

        # Total attendance should be 2 (only PTV)
        assert stats["daysAttended"] == 2

    def test_monthly_breakdown_includes_manual_dates(self):
        """Test that monthly breakdown includes both manual and PTV dates."""
        from working_days import VIC_HOLIDAYS

        # January: 1 PTV date + 1 manual date = 2 total
        attendance_days = ["2025-01-10"]  # Pass as string not dict
        manual_dates = ["2025-01-15"]

        stats = calculate_statistics(
            attendance_days=attendance_days,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            skip_dates=[],
            vic_holidays=VIC_HOLIDAYS,
            manual_attendance_dates=manual_dates
        )

        # Check monthly breakdown
        monthly = stats["monthlyBreakdown"]
        jan_data = next(m for m in monthly if m["month"] == "2025-01")

        # January should show 2 attendance days
        assert jan_data["daysAttended"] == 2
