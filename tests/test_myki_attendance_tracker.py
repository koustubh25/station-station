"""Tests for Myki Attendance Tracker functionality."""

import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


# ============================================================================
# Task Group 2: Configuration Loading and Validation Tests
# ============================================================================

class TestConfigurationLoading:
    """Tests for configuration loading and validation (Task Group 2)."""

    def test_valid_config_loads_successfully(self, tmp_path):
        """Test: Valid JSON config loads successfully with all required fields."""
        from src.config_manager import load_user_config, validate_user_config

        # Create valid config file
        config_data = {
            "koustubh": {
                "mykiCardNumber": "308425279093478",
                "targetStation": "Heathmont Station",
                "skipDates": ["2025-03-15", "2025-06-20"],
                "startDate": "2025-04-15",
                "endDate": "2025-06-15"
            }
        }

        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Load config
        loaded_config = load_user_config(str(config_file))

        # Verify structure
        assert loaded_config is not None
        assert "koustubh" in loaded_config
        assert loaded_config["koustubh"]["mykiCardNumber"] == "308425279093478"
        assert loaded_config["koustubh"]["targetStation"] == "Heathmont Station"
        assert loaded_config["koustubh"]["skipDates"] == ["2025-03-15", "2025-06-20"]

        # Validate config
        validate_user_config(loaded_config)  # Should not raise any exceptions

    def test_missing_environment_variable_raises_error(self, tmp_path):
        """Test: Missing environment variable for user raises clear error."""
        from src.config_manager import load_user_config, load_user_passwords

        # Create config with two users
        config_data = {
            "user1": {
                "mykiCardNumber": "123456789012345",
                "targetStation": "Test Station",
                "skipDates": [],
                "startDate": "2025-01-01",
                "endDate": "2025-12-31"
            },
            "user2": {
                "mykiCardNumber": "987654321098765",
                "targetStation": "Another Station",
                "skipDates": [],
                "startDate": "2025-01-01",
                "endDate": "2025-12-31"
            }
        }

        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        loaded_config = load_user_config(str(config_file))

        # Ensure environment variables are NOT set
        for username in ["user1", "user2"]:
            env_var = f"MYKI_PASSWORD_{username.upper()}"
            if env_var in os.environ:
                del os.environ[env_var]

        # Should raise ValueError with clear message about missing passwords
        with pytest.raises(ValueError) as exc_info:
            load_user_passwords(loaded_config)

        error_message = str(exc_info.value)
        assert "MYKI_PASSWORD_USER1" in error_message
        assert "MYKI_PASSWORD_USER2" in error_message

    def test_invalid_date_format_raises_validation_error(self, tmp_path):
        """Test: Invalid date format in config raises validation error."""
        from src.config_manager import load_user_config, validate_user_config

        # Create config with invalid date format
        config_data = {
            "testuser": {
                "mykiCardNumber": "123456789012345",
                "targetStation": "Test Station",
                "skipDates": ["2025-03-15"],
                "startDate": "2025/04/15",  # Invalid format (should be YYYY-MM-DD)
                "endDate": "2025-06-15"
            }
        }

        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        loaded_config = load_user_config(str(config_file))

        # Should raise ValueError for invalid date format
        with pytest.raises(ValueError) as exc_info:
            validate_user_config(loaded_config)

        error_message = str(exc_info.value)
        assert "startDate" in error_message or "date format" in error_message.lower()

    def test_missing_required_field_raises_schema_error(self, tmp_path):
        """Test: Missing required field in config raises schema error."""
        from src.config_manager import load_user_config, validate_user_config

        # Create config missing targetStation field (endDate is optional so not testing that)
        config_data = {
            "testuser": {
                "mykiCardNumber": "123456789012345",
                # "targetStation": "Test Station",  # Missing required field
                "skipDates": [],
                "startDate": "2025-01-01"
                # endDate is optional, so not including it should be fine
            }
        }

        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        loaded_config = load_user_config(str(config_file))

        # Should raise ValueError for missing required field
        with pytest.raises(ValueError) as exc_info:
            validate_user_config(loaded_config)

        error_message = str(exc_info.value)
        assert "targetStation" in error_message or "required" in error_message.lower()

    def test_optional_enddate_defaults_to_current_date(self, tmp_path):
        """Test: endDate is optional and defaults to current date when not specified."""
        from src.config_manager import load_user_config, validate_user_config, get_effective_end_date
        from datetime import date

        # Create config without endDate
        config_data = {
            "testuser": {
                "mykiCardNumber": "123456789012345",
                "targetStation": "Test Station",
                "skipDates": [],
                "startDate": "2025-01-01"
                # endDate is not specified - should default to current date
            }
        }

        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        loaded_config = load_user_config(str(config_file))

        # Validation should pass even without endDate
        validate_user_config(loaded_config)  # Should not raise

        # get_effective_end_date should return current date
        effective_end_date = get_effective_end_date(loaded_config, "testuser")
        today_str = date.today().strftime('%Y-%m-%d')
        assert effective_end_date == today_str

    def test_optional_skipdates_defaults_to_empty_array(self, tmp_path):
        """Test: skipDates is optional and defaults to empty array when not specified."""
        from src.config_manager import load_user_config, validate_user_config, get_effective_skip_dates

        # Create config without skipDates
        config_data = {
            "testuser": {
                "mykiCardNumber": "123456789012345",
                "targetStation": "Test Station",
                "startDate": "2025-01-01"
                # skipDates and endDate are not specified
            }
        }

        config_file = tmp_path / "test_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        loaded_config = load_user_config(str(config_file))

        # Validation should pass even without skipDates
        validate_user_config(loaded_config)  # Should not raise

        # get_effective_skip_dates should return empty list
        effective_skip_dates = get_effective_skip_dates(loaded_config, "testuser")
        assert effective_skip_dates == []


# ============================================================================
# Task Group 3: Working Days Calculation Logic Tests
# ============================================================================

class TestWorkingDaysCalculation:
    """Tests for working day calculation logic (Task Group 3)."""

    def test_monday_through_friday_identified_as_potential_working_days(self):
        """Test: Monday-Friday dates identified as potential working days."""
        from src.working_days import is_working_day
        import holidays

        # Initialize Melbourne VIC holidays
        vic_holidays = holidays.country_holidays('AU', subdiv='VIC')
        skip_dates = []

        # Test a week in 2025 that doesn't have public holidays
        # Week of May 19-23, 2025 (Monday to Friday)
        monday = date(2025, 5, 19)      # Monday
        tuesday = date(2025, 5, 20)     # Tuesday
        wednesday = date(2025, 5, 21)   # Wednesday
        thursday = date(2025, 5, 22)    # Thursday
        friday = date(2025, 5, 23)      # Friday

        # All weekdays should be working days
        assert is_working_day(monday, skip_dates, vic_holidays) is True
        assert is_working_day(tuesday, skip_dates, vic_holidays) is True
        assert is_working_day(wednesday, skip_dates, vic_holidays) is True
        assert is_working_day(thursday, skip_dates, vic_holidays) is True
        assert is_working_day(friday, skip_dates, vic_holidays) is True

    def test_saturday_sunday_excluded_from_working_days(self):
        """Test: Saturday-Sunday excluded from working days."""
        from src.working_days import is_working_day
        import holidays

        # Initialize Melbourne VIC holidays
        vic_holidays = holidays.country_holidays('AU', subdiv='VIC')
        skip_dates = []

        # Test a weekend in 2025
        saturday = date(2025, 5, 24)    # Saturday
        sunday = date(2025, 5, 25)      # Sunday

        # Weekend days should NOT be working days
        assert is_working_day(saturday, skip_dates, vic_holidays) is False
        assert is_working_day(sunday, skip_dates, vic_holidays) is False

    def test_melbourne_vic_public_holiday_excluded(self):
        """Test: Melbourne VIC public holiday excluded from working days."""
        from src.working_days import is_working_day
        import holidays

        # Initialize Melbourne VIC holidays
        vic_holidays = holidays.country_holidays('AU', subdiv='VIC')
        skip_dates = []

        # Test known Melbourne VIC public holidays
        # Australia Day 2025 - January 27, 2025 (Monday)
        australia_day = date(2025, 1, 27)

        # ANZAC Day 2025 - April 25, 2025 (Friday)
        anzac_day = date(2025, 4, 25)

        # Public holidays should NOT be working days (even though they fall on weekdays)
        assert is_working_day(australia_day, skip_dates, vic_holidays) is False
        assert is_working_day(anzac_day, skip_dates, vic_holidays) is False

    def test_user_skip_date_excluded_from_working_days(self):
        """Test: User skip date excluded from working days."""
        from src.working_days import is_working_day
        import holidays

        # Initialize Melbourne VIC holidays
        vic_holidays = holidays.country_holidays('AU', subdiv='VIC')

        # Define skip dates (user-specified leave days)
        skip_dates = [
            date(2025, 5, 19),  # Monday - personal leave
            date(2025, 5, 21),  # Wednesday - personal leave
        ]

        # These dates are weekdays and not public holidays, but should be excluded due to skip_dates
        monday = date(2025, 5, 19)
        wednesday = date(2025, 5, 21)

        # Skip dates should NOT be working days
        assert is_working_day(monday, skip_dates, vic_holidays) is False
        assert is_working_day(wednesday, skip_dates, vic_holidays) is False

        # But other weekdays in the same week should still be working days
        tuesday = date(2025, 5, 20)
        thursday = date(2025, 5, 22)
        assert is_working_day(tuesday, skip_dates, vic_holidays) is True
        assert is_working_day(thursday, skip_dates, vic_holidays) is True


class TestParseSkipDates:
    """Tests for parse_skip_dates helper function (Task Group 3)."""

    def test_parse_valid_iso_date_strings(self):
        """Test: Parse valid ISO date strings to date objects."""
        from src.working_days import parse_skip_dates

        skip_dates_str = ["2025-03-15", "2025-06-20", "2025-12-25"]
        skip_dates_obj = parse_skip_dates(skip_dates_str)

        # Should return list of date objects
        assert len(skip_dates_obj) == 3
        assert skip_dates_obj[0] == date(2025, 3, 15)
        assert skip_dates_obj[1] == date(2025, 6, 20)
        assert skip_dates_obj[2] == date(2025, 12, 25)

    def test_parse_empty_skip_dates_array(self):
        """Test: Parse empty skip dates array returns empty list."""
        from src.working_days import parse_skip_dates

        skip_dates_str = []
        skip_dates_obj = parse_skip_dates(skip_dates_str)

        # Should return empty list
        assert skip_dates_obj == []

    def test_parse_invalid_date_format_raises_error(self):
        """Test: Invalid date format raises clear error message."""
        from src.working_days import parse_skip_dates

        skip_dates_str = ["2025-03-15", "2025/06/20", "2025-12-25"]  # Second date has invalid format

        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            parse_skip_dates(skip_dates_str)

        error_message = str(exc_info.value)
        assert "2025/06/20" in error_message  # Should mention the problematic date


# ============================================================================
# Task Group 4: Transaction Fetching and Pagination Tests
# ============================================================================

class TestTransactionFetching:
    """Tests for transaction fetching with pagination handling (Task Group 4)."""

    def test_fetch_transactions_page_0_successfully(self):
        """Test: Fetch transactions from page 0 successfully."""
        from src.transaction_fetcher import fetch_all_transactions
        from unittest.mock import MagicMock
        import requests

        # Mock client
        mock_client = MagicMock()

        # Page 0: successful response with data
        # Page 1+: raises special 409 error (end of data)
        def mock_get_transactions(card_number, page):
            if page == 0:
                return {
                    "transactions": [
                        {"id": "txn1", "transactionDateTime": "2025-05-01T10:00:00"},
                        {"id": "txn2", "transactionDateTime": "2025-05-02T10:00:00"}
                    ]
                }
            else:
                # Simulate end-of-data with special 409 error
                response = MagicMock()
                response.status_code = 409
                response.json.return_value = {
                    "code": 409,
                    "message": "txnTimestamp: Expected a non-empty value. Got: null"
                }
                error = requests.HTTPError(response=response)
                raise error

        mock_client.get_transactions.side_effect = mock_get_transactions

        # Fetch transactions
        card_number = "308425279093478"
        transactions = fetch_all_transactions(mock_client, card_number)

        # Verify: successfully fetched page 0
        assert len(transactions) == 2
        assert transactions[0]["id"] == "txn1"
        assert transactions[1]["id"] == "txn2"
        # Should have called page 0 and attempted page 1
        assert mock_client.get_transactions.call_count == 2

    def test_stop_pagination_on_special_409_error(self):
        """Test: Stop pagination when 409 error with null txnTimestamp occurs (treat as normal)."""
        from src.transaction_fetcher import fetch_all_transactions
        from unittest.mock import MagicMock
        import requests

        # Mock client
        mock_client = MagicMock()

        # Page 0: successful response
        # Page 1: raises special 409 error
        def mock_get_transactions(card_number, page):
            if page == 0:
                return {
                    "transactions": [
                        {"id": "txn1", "transactionDateTime": "2025-05-01T10:00:00"}
                    ]
                }
            else:
                # Simulate 409 error with special message
                response = MagicMock()
                response.status_code = 409
                response.json.return_value = {
                    "code": 409,
                    "message": "txnTimestamp: Expected a non-empty value. Got: null"
                }
                error = requests.HTTPError(response=response)
                raise error

        mock_client.get_transactions.side_effect = mock_get_transactions

        # Fetch transactions - should complete gracefully without raising exception
        card_number = "308425279093478"
        transactions = fetch_all_transactions(mock_client, card_number)

        # Verify: only page 0 transactions returned, no exception raised
        assert len(transactions) == 1
        assert transactions[0]["id"] == "txn1"
        assert mock_client.get_transactions.call_count == 2  # Called page 0 and 1

    def test_respect_five_page_safety_limit(self):
        """Test: Respect 5-page safety limit to prevent infinite loops."""
        from src.transaction_fetcher import fetch_all_transactions
        from unittest.mock import MagicMock

        # Mock client that returns data for all pages
        mock_client = MagicMock()

        def mock_get_transactions(card_number, page):
            # Return data for any page (simulating API with many pages)
            return {
                "transactions": [
                    {"id": f"txn_page_{page}", "transactionDateTime": "2025-05-01T10:00:00"}
                ]
            }

        mock_client.get_transactions.side_effect = mock_get_transactions

        # Fetch transactions
        card_number = "308425279093478"
        transactions = fetch_all_transactions(mock_client, card_number)

        # Verify: should only fetch 5 pages (0-4)
        assert len(transactions) == 5
        assert mock_client.get_transactions.call_count == 5

        # Verify pages 0-4 were called
        for page in range(5):
            assert any(txn["id"] == f"txn_page_{page}" for txn in transactions)

    def test_handle_non_409_errors_as_failures(self):
        """Test: Handle non-409 HTTP errors as actual failures."""
        from src.transaction_fetcher import fetch_all_transactions
        from unittest.mock import MagicMock
        import requests

        # Mock client
        mock_client = MagicMock()

        # Simulate 500 Internal Server Error
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        error = requests.HTTPError(response=response)

        mock_client.get_transactions.side_effect = error

        # Fetch transactions - should raise exception
        card_number = "308425279093478"

        with pytest.raises(requests.HTTPError) as exc_info:
            fetch_all_transactions(mock_client, card_number)

        # Verify error details
        assert exc_info.value.response.status_code == 500


# ============================================================================
# Task Group 5: Transaction Filtering and Attendance Tracking Tests
# ============================================================================

class TestTransactionFiltering:
    """Tests for transaction filtering and attendance calculation (Task Group 5)."""

    def test_filter_transactions_by_exact_station_name(self):
        """Test: Filter transactions by exact station name match (case-sensitive)."""
        from src.transaction_processor import filter_transactions
        from datetime import date

        # Sample transactions with different station names
        transactions = [
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-15T08:30:00+10:00",
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-15T08:31:00+10:00",
                "description": "heathmont station"  # Different case
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-15T08:32:00+10:00",
                "description": "Ringwood Station"  # Different station
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-15T08:33:00+10:00",
                "description": "Heathmont Station"  # Match
            }
        ]

        # Filter for exact match
        filtered = filter_transactions(
            transactions=transactions,
            target_station="Heathmont Station",
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31)
        )

        # Should only match exact station name (case-sensitive)
        assert len(filtered) == 2
        assert all(t["description"] == "Heathmont Station" for t in filtered)

    def test_filter_transactions_by_touch_off_type(self):
        """Test: Filter transactions by transactionType == 'Touch off'."""
        from src.transaction_processor import filter_transactions
        from datetime import date

        # Sample transactions with different types
        transactions = [
            {
                "transactionType": "Touch on",
                "transactionDateTime": "2025-05-15T08:00:00+10:00",
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-15T17:00:00+10:00",
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-16T17:00:00+10:00",
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Top up",
                "transactionDateTime": "2025-05-17T12:00:00+10:00",
                "description": "Heathmont Station"
            }
        ]

        # Filter for Touch off at target station
        filtered = filter_transactions(
            transactions=transactions,
            target_station="Heathmont Station",
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31)
        )

        # Should only include "Touch off" transactions
        assert len(filtered) == 2
        assert all(t["transactionType"] == "Touch off" for t in filtered)

    def test_filter_transactions_by_date_range_inclusive(self):
        """Test: Filter transactions within date range (startDate to endDate inclusive)."""
        from src.transaction_processor import filter_transactions, parse_transaction_date
        from datetime import date

        # Sample transactions across different dates
        transactions = [
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-04-30T17:00:00+10:00",  # Before start
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-01T17:00:00+10:00",  # On start date
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-15T17:00:00+10:00",  # Within range
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-05-31T17:00:00+10:00",  # On end date
                "description": "Heathmont Station"
            },
            {
                "transactionType": "Touch off",
                "transactionDateTime": "2025-06-01T17:00:00+10:00",  # After end
                "description": "Heathmont Station"
            }
        ]

        # Filter for May 2025 (inclusive)
        filtered = filter_transactions(
            transactions=transactions,
            target_station="Heathmont Station",
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 31)
        )

        # Should include start date, within range, and end date (3 transactions)
        assert len(filtered) == 3
        # Verify dates are within range
        for txn in filtered:
            txn_date = parse_transaction_date(txn["transactionDateTime"])
            assert date(2025, 5, 1) <= txn_date <= date(2025, 5, 31)

    def test_parse_transaction_date_from_iso_string(self):
        """Test: Extract and parse transactionDateTime ISO string to date object."""
        from src.transaction_processor import parse_transaction_date
        from datetime import date

        # Test various ISO datetime formats from API
        test_cases = [
            ("2025-10-29T13:04:45+11:00", date(2025, 10, 29)),  # With timezone
            ("2025-05-15T08:30:00+10:00", date(2025, 5, 15)),   # Different timezone
            ("2025-01-01T00:00:00+11:00", date(2025, 1, 1)),    # Midnight
            ("2025-12-31T23:59:59+10:00", date(2025, 12, 31))   # End of day
        ]

        for iso_string, expected_date in test_cases:
            result = parse_transaction_date(iso_string)
            assert result == expected_date, f"Failed for {iso_string}"

        # Test error handling for invalid format
        with pytest.raises(ValueError) as exc_info:
            parse_transaction_date("2025/05/15 08:30:00")  # Wrong format

        assert "Failed to parse" in str(exc_info.value)


# ============================================================================
# Task Group 6: Incremental Processing and Output Generation Tests
# ============================================================================

class TestIncrementalProcessing:
    """Tests for incremental processing and output generation (Task Group 6)."""

    def test_first_run_processes_all_transactions_and_sets_latest_processed_date(self, tmp_path):
        """Test: First run (no existing output) processes all transactions and sets latestProcessedDate."""
        from src.output_manager import (
            load_existing_output, filter_new_transactions,
            update_user_output, get_latest_processed_date
        )
        from datetime import datetime

        # Create non-existent output file path
        output_file = tmp_path / "attendance.json"

        # Load existing output (should return empty dict on first run)
        existing_output = load_existing_output(str(output_file))
        assert existing_output == {}

        # Sample transactions from API
        transactions = [
            {"transactionDateTime": "2025-05-15T08:30:00+10:00", "id": "txn1"},
            {"transactionDateTime": "2025-05-16T08:30:00+10:00", "id": "txn2"},
            {"transactionDateTime": "2025-05-17T08:30:00+10:00", "id": "txn3"}
        ]

        # Get latest processed date for new user (should be None)
        latest_date = get_latest_processed_date(existing_output, "testuser")
        assert latest_date is None

        # Filter new transactions (first run should return all)
        new_transactions = filter_new_transactions(transactions, latest_date)
        assert len(new_transactions) == 3
        assert new_transactions == transactions

        # Calculate latest transaction datetime
        latest_txn_datetime = datetime.fromisoformat(transactions[-1]["transactionDateTime"])

        # Update output with new attendance days
        new_attendance_days = ["2025-05-15", "2025-05-16", "2025-05-17"]
        user_output = update_user_output(
            existing_output=existing_output,
            username="testuser",
            new_attendance_days=new_attendance_days,
            latest_txn_datetime=latest_txn_datetime,
            target_station="Heathmont Station"
        )

        # Verify user output structure
        assert "testuser" in user_output
        assert user_output["testuser"]["attendanceDays"] == new_attendance_days
        assert user_output["testuser"]["latestProcessedDate"] is not None
        assert user_output["testuser"]["targetStation"] == "Heathmont Station"
        assert user_output["testuser"]["lastUpdated"] is not None

    def test_subsequent_run_only_processes_new_transactions(self):
        """Test: Subsequent run only processes transactions after latestProcessedDate."""
        from src.output_manager import (
            get_latest_processed_date, filter_new_transactions
        )
        from datetime import datetime

        # Existing output from previous run
        existing_output = {
            "testuser": {
                "attendanceDays": ["2025-05-15", "2025-05-16"],
                "latestProcessedDate": "2025-05-16T17:30:00+10:00",
                "targetStation": "Heathmont Station",
                "lastUpdated": "2025-11-01T10:00:00Z"
            }
        }

        # Get latest processed date for existing user
        latest_date = get_latest_processed_date(existing_output, "testuser")
        assert latest_date is not None
        assert latest_date == datetime.fromisoformat("2025-05-16T17:30:00+10:00")

        # New transactions from API (mix of old and new)
        all_transactions = [
            {"transactionDateTime": "2025-05-15T17:00:00+10:00", "id": "old1"},  # Already processed
            {"transactionDateTime": "2025-05-16T17:30:00+10:00", "id": "old2"},  # Already processed (equal to latest)
            {"transactionDateTime": "2025-05-17T17:00:00+10:00", "id": "new1"},  # New!
            {"transactionDateTime": "2025-05-18T17:00:00+10:00", "id": "new2"}   # New!
        ]

        # Filter to only new transactions
        new_transactions = filter_new_transactions(all_transactions, latest_date)

        # Verify only transactions AFTER latestProcessedDate are returned
        assert len(new_transactions) == 2
        assert new_transactions[0]["id"] == "new1"
        assert new_transactions[1]["id"] == "new2"

        # Verify old transactions excluded
        from src.transaction_processor import parse_transaction_date
        for txn in new_transactions:
            txn_datetime = datetime.fromisoformat(txn["transactionDateTime"])
            assert txn_datetime > latest_date

    def test_merge_new_attendance_days_with_existing_no_duplicates(self):
        """Test: Merge new attendance days with existing (deduplicate and sort)."""
        from src.myki_attendance_tracker import update_user_output
        from datetime import datetime

        # Existing output with some attendance days
        existing_output = {
            "testuser": {
                "attendanceDays": ["2025-05-15", "2025-05-17", "2025-05-19"],
                "latestProcessedDate": "2025-05-19T17:30:00+10:00",
                "targetStation": "Heathmont Station",
                "lastUpdated": "2025-11-01T10:00:00Z"
            }
        }

        # New attendance days (some overlap with existing)
        new_attendance_days = ["2025-05-17", "2025-05-20", "2025-05-22"]  # 05-17 is duplicate
        latest_txn_datetime = datetime.fromisoformat("2025-05-22T17:30:00+10:00")

        # Update user output with merge
        user_output = update_user_output(
            existing_output=existing_output,
            username="testuser",
            new_attendance_days=new_attendance_days,
            latest_txn_datetime=latest_txn_datetime,
            target_station="Heathmont Station"
        )

        # Verify merged attendance days
        merged_days = user_output["testuser"]["attendanceDays"]

        # Should contain all unique dates from both lists
        expected_days = ["2025-05-15", "2025-05-17", "2025-05-19", "2025-05-20", "2025-05-22"]
        assert merged_days == expected_days

        # Verify no duplicates
        assert len(merged_days) == len(set(merged_days))

        # Verify sorted in chronological order
        assert merged_days == sorted(merged_days)

        # Verify latestProcessedDate updated to new latest
        assert user_output["testuser"]["latestProcessedDate"] == "2025-05-22T17:30:00+10:00"

    def test_update_last_updated_timestamp_on_each_run(self):
        """Test: Update lastUpdated timestamp on each run."""
        from src.myki_attendance_tracker import update_user_output
        from datetime import datetime
        import time

        # Existing output with old timestamp
        existing_output = {
            "testuser": {
                "attendanceDays": ["2025-05-15"],
                "latestProcessedDate": "2025-05-15T17:30:00+10:00",
                "targetStation": "Heathmont Station",
                "lastUpdated": "2025-11-01T10:00:00Z"  # Old timestamp
            }
        }

        old_timestamp = existing_output["testuser"]["lastUpdated"]

        # Wait a moment to ensure timestamp changes
        time.sleep(0.1)

        # Update with new data
        new_attendance_days = ["2025-05-16"]
        latest_txn_datetime = datetime.fromisoformat("2025-05-16T17:30:00+10:00")

        user_output = update_user_output(
            existing_output=existing_output,
            username="testuser",
            new_attendance_days=new_attendance_days,
            latest_txn_datetime=latest_txn_datetime,
            target_station="Heathmont Station"
        )

        # Verify lastUpdated changed
        new_timestamp = user_output["testuser"]["lastUpdated"]
        assert new_timestamp != old_timestamp

        # Verify timestamp is valid ISO format
        datetime.fromisoformat(new_timestamp.replace('Z', '+00:00'))  # Should not raise

        # Verify timestamp is recent (within last few seconds)
        # Parse and compare (remove timezone for comparison)
        timestamp_dt = datetime.fromisoformat(new_timestamp.replace('Z', '+00:00'))
        now = datetime.now(timestamp_dt.tzinfo)
        time_diff = (now - timestamp_dt).total_seconds()
        assert time_diff < 5  # Should be within 5 seconds


# ============================================================================
# Task Group 7: Main Orchestration and Error Handling Tests
# ============================================================================

class TestMainOrchestration:
    """Tests for main orchestration and multi-user processing (Task Group 7)."""

    def test_process_multiple_users_sequentially(self, tmp_path):
        """Test: Process multiple users sequentially in single execution."""
        from src.myki_attendance_tracker import process_user
        from src.working_days import VIC_HOLIDAYS
        from unittest.mock import MagicMock

        # Mock client
        mock_client = MagicMock()

        # Mock successful transaction fetching for both users
        def mock_get_transactions(card_number, page):
            if page == 0:
                if card_number == "111111111111111":
                    return {
                        "transactions": [
                            {
                                "transactionType": "Touch off",
                                "transactionDateTime": "2025-05-15T17:00:00+10:00",
                                "description": "Station A"
                            }
                        ]
                    }
                elif card_number == "222222222222222":
                    return {
                        "transactions": [
                            {
                                "transactionType": "Touch off",
                                "transactionDateTime": "2025-05-16T17:00:00+10:00",
                                "description": "Station B"
                            }
                        ]
                    }
            else:
                # Simulate end of pagination
                response = MagicMock()
                response.status_code = 409
                response.json.return_value = {
                    "code": 409,
                    "message": "txnTimestamp: Expected a non-empty value. Got: null"
                }
                import requests
                raise requests.HTTPError(response=response)

        mock_client.get_transactions.side_effect = mock_get_transactions

        # User configs
        user1_config = {
            "mykiCardNumber": "111111111111111",
            "targetStation": "Station A",
            "startDate": "2025-05-01",
            "endDate": "2025-05-31"
        }

        user2_config = {
            "mykiCardNumber": "222222222222222",
            "targetStation": "Station B",
            "startDate": "2025-05-01",
            "endDate": "2025-05-31"
        }

        # Process both users
        existing_output = {}

        success1, output1, error1 = process_user(
            username="user1",
            user_config=user1_config,
            client=mock_client,
            existing_output=existing_output,
            vic_holidays=VIC_HOLIDAYS
        )

        success2, output2, error2 = process_user(
            username="user2",
            user_config=user2_config,
            client=mock_client,
            existing_output=existing_output,
            vic_holidays=VIC_HOLIDAYS
        )

        # Verify both users processed successfully
        assert success1 is True
        assert error1 is None
        assert output1 is not None
        assert "user1" in output1

        assert success2 is True
        assert error2 is None
        assert output2 is not None
        assert "user2" in output2

    def test_continue_processing_other_users_if_one_fails(self):
        """Test: Continue processing other users if one user fails."""
        from src.myki_attendance_tracker import process_user
        from src.working_days import VIC_HOLIDAYS
        from unittest.mock import MagicMock
        import requests

        # Mock client
        mock_client = MagicMock()

        # Mock: user1 succeeds, user2 fails with API error, user3 succeeds
        def mock_get_transactions(card_number, page):
            if card_number == "111111111111111":
                # User1: success
                if page == 0:
                    return {
                        "transactions": [
                            {
                                "transactionType": "Touch off",
                                "transactionDateTime": "2025-05-15T17:00:00+10:00",
                                "description": "Station A"
                            }
                        ]
                    }
                else:
                    # End of pagination
                    response = MagicMock()
                    response.status_code = 409
                    response.json.return_value = {
                        "code": 409,
                        "message": "txnTimestamp: Expected a non-empty value. Got: null"
                    }
                    raise requests.HTTPError(response=response)

            elif card_number == "222222222222222":
                # User2: API failure (500 error)
                response = MagicMock()
                response.status_code = 500
                response.text = "Internal Server Error"
                raise requests.HTTPError(response=response)

            elif card_number == "333333333333333":
                # User3: success
                if page == 0:
                    return {
                        "transactions": [
                            {
                                "transactionType": "Touch off",
                                "transactionDateTime": "2025-05-17T17:00:00+10:00",
                                "description": "Station C"
                            }
                        ]
                    }
                else:
                    # End of pagination
                    response = MagicMock()
                    response.status_code = 409
                    response.json.return_value = {
                        "code": 409,
                        "message": "txnTimestamp: Expected a non-empty value. Got: null"
                    }
                    raise requests.HTTPError(response=response)

        mock_client.get_transactions.side_effect = mock_get_transactions

        # User configs
        user1_config = {
            "mykiCardNumber": "111111111111111",
            "targetStation": "Station A",
            "startDate": "2025-05-01",
            "endDate": "2025-05-31"
        }

        user2_config = {
            "mykiCardNumber": "222222222222222",
            "targetStation": "Station B",
            "startDate": "2025-05-01",
            "endDate": "2025-05-31"
        }

        user3_config = {
            "mykiCardNumber": "333333333333333",
            "targetStation": "Station C",
            "startDate": "2025-05-01",
            "endDate": "2025-05-31"
        }

        existing_output = {}

        # Process all three users
        success1, output1, error1 = process_user(
            "user1", user1_config, mock_client, existing_output, VIC_HOLIDAYS
        )
        success2, output2, error2 = process_user(
            "user2", user2_config, mock_client, existing_output, VIC_HOLIDAYS
        )
        success3, output3, error3 = process_user(
            "user3", user3_config, mock_client, existing_output, VIC_HOLIDAYS
        )

        # Verify: user1 succeeded
        assert success1 is True
        assert error1 is None
        assert output1 is not None

        # Verify: user2 failed with HTTPError
        assert success2 is False
        assert output2 is None
        assert error2 is not None
        assert isinstance(error2, requests.HTTPError)

        # Verify: user3 succeeded (despite user2 failure)
        assert success3 is True
        assert error3 is None
        assert output3 is not None

    def test_collect_and_report_all_errors_at_end(self):
        """Test: Collect and report all errors at end of processing."""
        from src.myki_attendance_tracker import main
        from unittest.mock import patch, MagicMock
        import tempfile
        import json

        # Create temporary config file with two users
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "user1": {
                    "mykiCardNumber": "111111111111111",
                    "targetStation": "Station A",
                    "startDate": "2025-05-01",
                    "endDate": "2025-05-31"
                },
                "user2": {
                    "mykiCardNumber": "222222222222222",
                    "targetStation": "Station B",
                    "startDate": "2025-05-01",
                    "endDate": "2025-05-31"
                }
            }
            json.dump(config_data, f)
            config_path = f.name

        # Mock environment variables for passwords
        with patch.dict('os.environ', {
            'MYKI_PASSWORD_USER1': 'password1',
            'MYKI_PASSWORD_USER2': 'password2'
        }):
            # Mock MykiAPIClient to simulate user2 failing
            with patch('src.myki_attendance_tracker.MykiAPIClient') as mock_api_class:
                mock_client = MagicMock()

                def mock_get_transactions(card_number, page):
                    if card_number == "111111111111111":
                        # User1: success
                        if page == 0:
                            return {
                                "transactions": [
                                    {
                                        "transactionType": "Touch off",
                                        "transactionDateTime": "2025-05-15T17:00:00+10:00",
                                        "description": "Station A"
                                    }
                                ]
                            }
                        else:
                            # End of pagination
                            response = MagicMock()
                            response.status_code = 409
                            response.json.return_value = {
                                "code": 409,
                                "message": "txnTimestamp: Expected a non-empty value. Got: null"
                            }
                            import requests
                            raise requests.HTTPError(response=response)
                    elif card_number == "222222222222222":
                        # User2: API failure
                        response = MagicMock()
                        response.status_code = 500
                        response.text = "Internal Server Error"
                        import requests
                        raise requests.HTTPError(response=response)

                mock_client.get_transactions.side_effect = mock_get_transactions
                mock_api_class.return_value = mock_client

                # Call main with config path
                import sys
                with patch.object(sys, 'argv', ['myki_attendance_tracker.py', config_path]):
                    exit_code = main()

                # Verify: exit code 1 (indicating failure)
                assert exit_code == 1

        # Clean up temp file
        import os
        os.unlink(config_path)

    def test_successful_run_returns_exit_code_0(self):
        """Test: Successful run returns exit code 0."""
        from src.myki_attendance_tracker import main
        from unittest.mock import patch, MagicMock
        import tempfile
        import json

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {
                "user1": {
                    "mykiCardNumber": "111111111111111",
                    "targetStation": "Station A",
                    "startDate": "2025-05-01",
                    "endDate": "2025-05-31"
                }
            }
            json.dump(config_data, f)
            config_path = f.name

        # Mock environment variables
        with patch.dict('os.environ', {'MYKI_PASSWORD_USER1': 'password1'}):
            # Mock MykiAPIClient to return successful response
            with patch('src.myki_attendance_tracker.MykiAPIClient') as mock_api_class:
                mock_client = MagicMock()

                def mock_get_transactions(card_number, page):
                    if page == 0:
                        return {
                            "transactions": [
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-15T17:00:00+10:00",
                                    "description": "Station A"
                                }
                            ]
                        }
                    else:
                        # End of pagination
                        response = MagicMock()
                        response.status_code = 409
                        response.json.return_value = {
                            "code": 409,
                            "message": "txnTimestamp: Expected a non-empty value. Got: null"
                        }
                        import requests
                        raise requests.HTTPError(response=response)

                mock_client.get_transactions.side_effect = mock_get_transactions
                mock_api_class.return_value = mock_client

                # Call main with config path
                import sys
                with patch.object(sys, 'argv', ['myki_attendance_tracker.py', config_path]):
                    exit_code = main()

                # Verify: exit code 0 (success)
                assert exit_code == 0

        # Clean up temp file
        import os
        os.unlink(config_path)
