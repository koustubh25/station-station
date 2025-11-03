"""Tests for manual attendance configuration.

Task Group 2: Backend Manual Attendance Configuration
- Test manualAttendanceDates array parsing and validation
- Test date format validation (YYYY-MM-DD pattern)
- Test date range validation (within startDate/endDate)
- Test conflict resolution (manual takes precedence over skipDates)
- Test empty array default when manualAttendanceDates not specified
"""

import pytest
from datetime import date
from src.config_manager import validate_user_config, get_effective_skip_dates


class TestManualAttendanceDatesValidation:
    """Test manualAttendanceDates config field validation."""

    def test_manualAttendanceDates_optional_field(self):
        """Test that manualAttendanceDates is optional and defaults to empty array."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01"
            }
        }

        # Should not raise any errors - manualAttendanceDates is optional
        validate_user_config(user_config)

    def test_manualAttendanceDates_array_type(self):
        """Test that manualAttendanceDates must be an array."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01",
                "manualAttendanceDates": "2025-01-15"  # String instead of array
            }
        }

        with pytest.raises(ValueError) as exc_info:
            validate_user_config(user_config)

        assert "manualattendancedates" in str(exc_info.value).lower()
        assert "array" in str(exc_info.value).lower() or "list" in str(exc_info.value).lower()

    def test_manualAttendanceDates_date_format_validation(self):
        """Test that manual dates must be in YYYY-MM-DD format."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01",
                "manualAttendanceDates": ["2025-01-15", "15/01/2025", "2025-01-20"]  # Middle date is invalid
            }
        }

        with pytest.raises(ValueError) as exc_info:
            validate_user_config(user_config)

        assert "15/01/2025" in str(exc_info.value)
        assert "yyyy-mm-dd" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()

    def test_manualAttendanceDates_range_validation_start_date(self):
        """Test that manual dates must be >= startDate."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-15",
                "endDate": "2025-01-31",
                "manualAttendanceDates": ["2025-01-10", "2025-01-20"]  # First date before startDate
            }
        }

        with pytest.raises(ValueError) as exc_info:
            validate_user_config(user_config)

        assert "2025-01-10" in str(exc_info.value)
        assert "range" in str(exc_info.value).lower() or "before" in str(exc_info.value).lower()

    def test_manualAttendanceDates_range_validation_end_date(self):
        """Test that manual dates must be <= endDate."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01",
                "endDate": "2025-01-31",
                "manualAttendanceDates": ["2025-01-15", "2025-02-05"]  # Second date after endDate
            }
        }

        with pytest.raises(ValueError) as exc_info:
            validate_user_config(user_config)

        assert "2025-02-05" in str(exc_info.value)
        assert "range" in str(exc_info.value).lower() or "after" in str(exc_info.value).lower()

    def test_manualAttendanceDates_empty_array_valid(self):
        """Test that empty manualAttendanceDates array is valid."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01",
                "manualAttendanceDates": []
            }
        }

        # Should not raise any errors
        validate_user_config(user_config)

    def test_manualAttendanceDates_valid_dates(self):
        """Test that valid manual dates pass validation."""
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01",
                "endDate": "2025-01-31",
                "manualAttendanceDates": ["2025-01-05", "2025-01-10", "2025-01-15"]
            }
        }

        # Should not raise any errors
        validate_user_config(user_config)


class TestManualAttendanceDatesConflictResolution:
    """Test conflict resolution between manualAttendanceDates and skipDates."""

    def test_manual_dates_override_skip_dates(self):
        """Test that manual attendance dates take precedence over skip dates.

        When a date appears in both manualAttendanceDates and skipDates,
        it should be treated as an attendance day (manual attendance wins).
        """
        user_config = {
            "koustubh": {
                "targetStation": "Test Station",
                "startDate": "2025-01-01",
                "skipDates": ["2025-01-10", "2025-01-15", "2025-01-20"],
                "manualAttendanceDates": ["2025-01-15", "2025-01-25"]  # 2025-01-15 conflicts
            }
        }

        # Should not raise errors - conflict is resolved by manual taking precedence
        validate_user_config(user_config)

        # Get effective skip dates - should exclude 2025-01-15
        effective_skip_dates = get_effective_skip_dates(user_config, "koustubh")

        # 2025-01-15 should be removed from effective skip dates
        assert "2025-01-15" not in effective_skip_dates
        assert "2025-01-10" in effective_skip_dates
        assert "2025-01-20" in effective_skip_dates
