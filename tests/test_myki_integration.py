"""Integration tests for Myki Attendance Tracker.

Task Group 8: Integration Testing and Validation

Tests the complete system end-to-end with realistic scenarios.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import requests


# ============================================================================
# Task Group 8.3: End-to-End Testing
# ============================================================================

class TestEndToEndWorkflow:
    """End-to-end integration tests for complete workflow."""

    def test_first_run_complete_workflow(self, tmp_path):
        """Test: First run processes all transactions and creates output file."""
        from src.myki_attendance_tracker import main

        # Create test config file
        config_file = tmp_path / "test_config.json"
        config_data = {
            "testuser": {
                "mykiCardNumber": "308425279093478",
                "targetStation": "Heathmont Station",
                "startDate": "2025-05-01",
                "endDate": "2025-05-31",
                "skipDates": []
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Create output directory
        output_file = tmp_path / "attendance.json"

        # Mock environment variables
        with patch.dict('os.environ', {'MYKI_PASSWORD_TESTUSER': 'password123'}):
            # Mock MykiAPIClient
            with patch('src.myki_attendance_tracker.MykiAPIClient') as mock_api_class:
                mock_client = MagicMock()

                # Mock transaction data - simulate May 2025 weekdays with touch-offs
                def mock_get_transactions(card_number, page):
                    if page == 0:
                        return {
                            "transactions": [
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-05T17:30:00+10:00",  # Monday
                                    "description": "Heathmont Station"
                                },
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-06T17:30:00+10:00",  # Tuesday
                                    "description": "Heathmont Station"
                                },
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-07T17:30:00+10:00",  # Wednesday
                                    "description": "Heathmont Station"
                                },
                                {
                                    "transactionType": "Touch on",  # Should be filtered out
                                    "transactionDateTime": "2025-05-08T08:30:00+10:00",  # Thursday
                                    "description": "Heathmont Station"
                                },
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-10T17:30:00+10:00",  # Saturday - weekend
                                    "description": "Heathmont Station"
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
                mock_api_class.return_value = mock_client

                # Capture written output
                written_data = {}

                # Mock file operations more comprehensively
                original_open = open
                original_path = Path

                def mock_open_func(*args, **kwargs):
                    file_path = str(args[0]) if args else ''
                    mode = args[1] if len(args) > 1 else kwargs.get('mode', 'r')

                    if 'attendance.json' in file_path:
                        if mode == 'r':
                            # First run - file doesn't exist
                            raise FileNotFoundError(f"No such file: {file_path}")
                        elif mode == 'w':
                            # Writing output file
                            import io
                            buffer = io.StringIO()
                            original_close = buffer.close

                            def close_with_capture():
                                written_data['content'] = buffer.getvalue()
                                original_close()

                            buffer.close = close_with_capture
                            return buffer
                    # Use original open for other files
                    return original_open(*args, **kwargs)

                class MockPath:
                    def __init__(self, path_str):
                        self.path_str = str(path_str)
                        self._real_path = original_path(path_str)

                    def exists(self):
                        if 'attendance.json' in self.path_str:
                            return False  # First run
                        return self._real_path.exists()

                    def __str__(self):
                        return self.path_str

                    def absolute(self):
                        return self.path_str

                    @property
                    def parent(self):
                        mock_parent = MagicMock()
                        mock_parent.mkdir = MagicMock()
                        return mock_parent

                    def stat(self):
                        mock_stat = MagicMock()
                        mock_stat.st_size = 500
                        return mock_stat

                with patch('src.output_manager.Path', MockPath):
                    with patch('builtins.open', mock_open_func):
                        # Run main
                        import sys
                        with patch.object(sys, 'argv', ['myki_attendance_tracker.py', str(config_file)]):
                            exit_code = main()

        # Verify exit code
        assert exit_code == 0

        # Verify output was written
        assert 'content' in written_data
        output = json.loads(written_data['content'])

        # Verify output structure
        assert "metadata" in output
        assert "testuser" in output

        # Verify metadata
        assert output["metadata"]["totalUsers"] == 1
        assert output["metadata"]["configPath"] == str(config_file)

        # Verify user data
        user_data = output["testuser"]
        assert user_data["targetStation"] == "Heathmont Station"
        assert "attendanceDays" in user_data
        assert "latestProcessedDate" in user_data
        assert "lastUpdated" in user_data

        # Verify attendance days - should only include weekdays (Mon-Wed)
        # Saturday excluded (weekend), Thursday excluded (Touch on, not Touch off)
        assert len(user_data["attendanceDays"]) == 3
        assert "2025-05-05" in user_data["attendanceDays"]  # Monday
        assert "2025-05-06" in user_data["attendanceDays"]  # Tuesday
        assert "2025-05-07" in user_data["attendanceDays"]  # Wednesday
        assert "2025-05-10" not in user_data["attendanceDays"]  # Saturday - weekend

    def test_incremental_processing_second_run(self, tmp_path):
        """Test: Second run only processes new transactions (incremental)."""
        from src.myki_attendance_tracker import main

        # Create test config
        config_file = tmp_path / "test_config.json"
        config_data = {
            "testuser": {
                "mykiCardNumber": "308425279093478",
                "targetStation": "Heathmont Station",
                "startDate": "2025-05-01",
                "endDate": "2025-05-31"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Create existing output (simulating first run)
        output_file = tmp_path / "attendance.json"
        existing_output = {
            "metadata": {
                "generatedAt": "2025-05-07T10:00:00Z",
                "configPath": str(config_file),
                "totalUsers": 1
            },
            "testuser": {
                "attendanceDays": ["2025-05-05", "2025-05-06"],
                "latestProcessedDate": "2025-05-06T17:30:00+10:00",
                "targetStation": "Heathmont Station",
                "lastUpdated": "2025-05-07T10:00:00Z"
            }
        }

        # Mock environment
        with patch.dict('os.environ', {'MYKI_PASSWORD_TESTUSER': 'password123'}):
            with patch('src.myki_attendance_tracker.MykiAPIClient') as mock_api_class:
                mock_client = MagicMock()

                # Mock API returns old + new transactions
                def mock_get_transactions(card_number, page):
                    if page == 0:
                        return {
                            "transactions": [
                                # Old transactions (already processed)
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-05T17:30:00+10:00",
                                    "description": "Heathmont Station"
                                },
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-06T17:30:00+10:00",
                                    "description": "Heathmont Station"
                                },
                                # New transactions (should be processed)
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-07T17:30:00+10:00",  # New!
                                    "description": "Heathmont Station"
                                },
                                {
                                    "transactionType": "Touch off",
                                    "transactionDateTime": "2025-05-08T17:30:00+10:00",  # New!
                                    "description": "Heathmont Station"
                                }
                            ]
                        }
                    else:
                        response = MagicMock()
                        response.status_code = 409
                        response.json.return_value = {
                            "code": 409,
                            "message": "txnTimestamp: Expected a non-empty value. Got: null"
                        }
                        raise requests.HTTPError(response=response)

                mock_client.get_transactions.side_effect = mock_get_transactions
                mock_api_class.return_value = mock_client

                # Mock file operations
                written_data = {}
                original_path = Path

                def mock_path_func(path_str):
                    path_obj = original_path(path_str)
                    if 'attendance.json' in str(path_str):
                        # Mock output file operations
                        mock_instance = MagicMock()
                        mock_instance.exists.return_value = True  # File exists (second run)
                        mock_instance.parent.mkdir = MagicMock()
                        mock_instance.absolute.return_value = output_file
                        mock_instance.stat.return_value.st_size = 600
                        return mock_instance
                    return path_obj

                with patch('src.output_manager.Path', side_effect=mock_path_func):
                    original_open = open

                    def mock_open_func(*args, **kwargs):
                        file_path = str(args[0]) if args else ''
                        mode = args[1] if len(args) > 1 else kwargs.get('mode', 'r')

                        if 'attendance.json' in file_path and mode == 'r':
                            # Reading existing output
                            import io
                            return io.StringIO(json.dumps(existing_output))
                        elif mode == 'w':
                            # Writing output
                            import io
                            buffer = io.StringIO()
                            original_close = buffer.close

                            def close_with_capture():
                                written_data['content'] = buffer.getvalue()
                                original_close()

                            buffer.close = close_with_capture
                            return buffer
                        # Use original open for reading config
                        return original_open(*args, **kwargs)

                    with patch('builtins.open', mock_open_func):
                        import sys
                        with patch.object(sys, 'argv', ['myki_attendance_tracker.py', str(config_file)]):
                            exit_code = main()

        # Verify exit code
        assert exit_code == 0

        # Verify output
        assert 'content' in written_data
        output = json.loads(written_data['content'])

        # Verify incremental processing worked
        user_data = output["testuser"]

        # Should have old + new days (4 total: 05, 06, 07, 08)
        assert len(user_data["attendanceDays"]) == 4
        assert "2025-05-05" in user_data["attendanceDays"]  # Old
        assert "2025-05-06" in user_data["attendanceDays"]  # Old
        assert "2025-05-07" in user_data["attendanceDays"]  # New
        assert "2025-05-08" in user_data["attendanceDays"]  # New

        # Latest processed date should be updated to most recent
        assert user_data["latestProcessedDate"] == "2025-05-08T17:30:00+10:00"


# ============================================================================
# Task Group 8.6: Error Scenario Testing
# ============================================================================

class TestErrorScenarios:
    """Test error handling for various failure scenarios."""

    def test_missing_config_file_error(self):
        """Test: Clear error message when config file doesn't exist."""
        from src.myki_attendance_tracker import main

        import sys
        with patch.object(sys, 'argv', ['myki_attendance_tracker.py', '/nonexistent/config.json']):
            exit_code = main()

        # Should fail with exit code 1
        assert exit_code == 1

    def test_malformed_json_config_error(self, tmp_path):
        """Test: Clear error message for malformed JSON config."""
        from src.myki_attendance_tracker import main

        # Create malformed JSON file
        config_file = tmp_path / "bad_config.json"
        with open(config_file, 'w') as f:
            f.write('{"user": {invalid json}')

        import sys
        with patch.object(sys, 'argv', ['myki_attendance_tracker.py', str(config_file)]):
            exit_code = main()

        # Should fail with exit code 1
        assert exit_code == 1

    def test_missing_environment_variable_error(self, tmp_path):
        """Test: Clear error listing all missing environment variables."""
        from src.myki_attendance_tracker import main

        # Create valid config
        config_file = tmp_path / "config.json"
        config_data = {
            "user1": {
                "mykiCardNumber": "111111111111111",
                "targetStation": "Station A",
                "startDate": "2025-05-01"
            },
            "user2": {
                "mykiCardNumber": "222222222222222",
                "targetStation": "Station B",
                "startDate": "2025-05-01"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Ensure env vars are NOT set
        env_vars_to_remove = ['MYKI_PASSWORD_USER1', 'MYKI_PASSWORD_USER2']
        with patch.dict('os.environ', {}, clear=False):
            for var in env_vars_to_remove:
                if var in os.environ:
                    del os.environ[var]

            import sys
            with patch.object(sys, 'argv', ['myki_attendance_tracker.py', str(config_file)]):
                exit_code = main()

        # Should fail with exit code 1
        assert exit_code == 1

    def test_invalid_date_format_error(self, tmp_path):
        """Test: Clear error for invalid date format with field name."""
        from src.myki_attendance_tracker import main

        # Create config with invalid date
        config_file = tmp_path / "config.json"
        config_data = {
            "testuser": {
                "mykiCardNumber": "308425279093478",
                "targetStation": "Test Station",
                "startDate": "2025/05/01"  # Invalid format (should be YYYY-MM-DD)
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        with patch.dict('os.environ', {'MYKI_PASSWORD_TESTUSER': 'password123'}):
            import sys
            with patch.object(sys, 'argv', ['myki_attendance_tracker.py', str(config_file)]):
                exit_code = main()

        # Should fail with exit code 1
        assert exit_code == 1

    def test_api_failure_error_handling(self, tmp_path):
        """Test: API failure logged with HTTP status and continues to next user."""
        from src.myki_attendance_tracker import main

        # Create config with two users
        config_file = tmp_path / "config.json"
        config_data = {
            "user1": {
                "mykiCardNumber": "111111111111111",
                "targetStation": "Station A",
                "startDate": "2025-05-01"
            },
            "user2": {
                "mykiCardNumber": "222222222222222",
                "targetStation": "Station B",
                "startDate": "2025-05-01"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        with patch.dict('os.environ', {
            'MYKI_PASSWORD_USER1': 'password1',
            'MYKI_PASSWORD_USER2': 'password2'
        }):
            with patch('src.myki_attendance_tracker.MykiAPIClient') as mock_api_class:
                mock_client = MagicMock()

                # User1 fails with 500 error, User2 succeeds
                def mock_get_transactions(card_number, page):
                    if card_number == "111111111111111":
                        # Simulate 500 error for user1
                        response = MagicMock()
                        response.status_code = 500
                        response.text = "Internal Server Error"
                        raise requests.HTTPError(response=response)
                    elif card_number == "222222222222222":
                        # User2 succeeds
                        if page == 0:
                            return {"transactions": []}
                        else:
                            response = MagicMock()
                            response.status_code = 409
                            response.json.return_value = {
                                "code": 409,
                                "message": "txnTimestamp: Expected a non-empty value. Got: null"
                            }
                            raise requests.HTTPError(response=response)

                mock_client.get_transactions.side_effect = mock_get_transactions
                mock_api_class.return_value = mock_client

                # Mock output operations
                with patch('src.output_manager.Path') as mock_path_class:
                    mock_path_instance = MagicMock()
                    mock_path_instance.exists.return_value = False
                    mock_path_instance.parent.mkdir = MagicMock()
                    mock_path_instance.absolute.return_value = tmp_path / "output.json"
                    mock_path_instance.stat.return_value.st_size = 100
                    mock_path_class.return_value = mock_path_instance

                    with patch('builtins.open', MagicMock()):
                        import sys
                        with patch.object(sys, 'argv', ['myki_attendance_tracker.py', str(config_file)]):
                            exit_code = main()

        # Should fail with exit code 1 (user1 failed)
        # But user2 should have been processed
        assert exit_code == 1


# ============================================================================
# Task Group 8.5: Output JSON Structure Validation
# ============================================================================

class TestOutputJSONValidation:
    """Test output JSON structure and data types."""

    def test_output_json_structure_complete(self, tmp_path):
        """Test: Output JSON has all required fields with correct types."""
        from src.output_manager import save_output
        from datetime import datetime, timezone

        # Create test output data
        output_data = {
            "user1": {
                "attendanceDays": ["2025-05-05", "2025-05-06", "2025-05-07"],
                "latestProcessedDate": "2025-05-07T17:30:00+10:00",
                "targetStation": "Heathmont Station",
                "lastUpdated": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }

        output_file = tmp_path / "test_output.json"

        # Save output
        save_output(output_data, str(output_file), "test_config.json")

        # Load and validate
        with open(output_file, 'r') as f:
            output = json.load(f)

        # Validate metadata structure
        assert "metadata" in output
        assert "generatedAt" in output["metadata"]
        assert "configPath" in output["metadata"]
        assert "totalUsers" in output["metadata"]

        # Validate metadata types
        assert isinstance(output["metadata"]["generatedAt"], str)
        assert isinstance(output["metadata"]["configPath"], str)
        assert isinstance(output["metadata"]["totalUsers"], int)

        # Validate metadata values
        assert output["metadata"]["totalUsers"] == 1
        assert output["metadata"]["configPath"] == "test_config.json"

        # Validate generatedAt is ISO format
        datetime.fromisoformat(output["metadata"]["generatedAt"].replace('Z', '+00:00'))

        # Validate user data structure
        assert "user1" in output
        user_data = output["user1"]

        # Validate user fields exist
        assert "attendanceDays" in user_data
        assert "latestProcessedDate" in user_data
        assert "targetStation" in user_data
        assert "lastUpdated" in user_data

        # Validate user field types
        assert isinstance(user_data["attendanceDays"], list)
        assert isinstance(user_data["latestProcessedDate"], str)
        assert isinstance(user_data["targetStation"], str)
        assert isinstance(user_data["lastUpdated"], str)

        # Validate attendanceDays format (all ISO date strings)
        for day in user_data["attendanceDays"]:
            assert isinstance(day, str)
            datetime.strptime(day, '%Y-%m-%d')  # Should parse as YYYY-MM-DD

        # Validate attendanceDays is sorted
        assert user_data["attendanceDays"] == sorted(user_data["attendanceDays"])

        # Validate no duplicate dates
        assert len(user_data["attendanceDays"]) == len(set(user_data["attendanceDays"]))

        # Validate latestProcessedDate is ISO datetime
        datetime.fromisoformat(user_data["latestProcessedDate"])

        # Validate lastUpdated is ISO timestamp
        datetime.fromisoformat(user_data["lastUpdated"].replace('Z', '+00:00'))


# ============================================================================
# Task Group 8.4: Special 409 Error Handling Validation
# ============================================================================

class TestSpecial409ErrorHandling:
    """Test special pagination 409 error is handled gracefully."""

    def test_409_null_timestamp_handled_gracefully(self):
        """Test: 409 error with null txnTimestamp doesn't cause failure."""
        from src.transaction_fetcher import fetch_all_transactions

        mock_client = MagicMock()

        # Simulate normal end of pagination with 409 error
        def mock_get_transactions(card_number, page):
            if page == 0:
                return {
                    "transactions": [
                        {"id": "txn1", "transactionDateTime": "2025-05-01T10:00:00+10:00"}
                    ]
                }
            else:
                # Special 409 error - end of data
                response = MagicMock()
                response.status_code = 409
                response.json.return_value = {
                    "code": 409,
                    "message": "txnTimestamp: Expected a non-empty value. Got: null"
                }
                raise requests.HTTPError(response=response)

        mock_client.get_transactions.side_effect = mock_get_transactions

        # Should NOT raise exception
        transactions = fetch_all_transactions(mock_client, "308425279093478")

        # Should successfully return page 0 transactions
        assert len(transactions) == 1
        assert transactions[0]["id"] == "txn1"

    def test_non_409_errors_still_raise(self):
        """Test: Non-409 HTTP errors are still raised as failures."""
        from src.transaction_fetcher import fetch_all_transactions

        mock_client = MagicMock()

        # Simulate 500 error
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        mock_client.get_transactions.side_effect = requests.HTTPError(response=response)

        # Should raise HTTPError
        with pytest.raises(requests.HTTPError):
            fetch_all_transactions(mock_client, "308425279093478")

    def test_different_409_error_still_raises(self):
        """Test: 409 errors with different messages are still raised."""
        from src.transaction_fetcher import fetch_all_transactions

        mock_client = MagicMock()

        # Simulate 409 error with different message
        response = MagicMock()
        response.status_code = 409
        response.json.return_value = {
            "code": 409,
            "message": "Conflict: Different error"
        }
        mock_client.get_transactions.side_effect = requests.HTTPError(response=response)

        # Should raise HTTPError (not the special pagination error)
        with pytest.raises(requests.HTTPError):
            fetch_all_transactions(mock_client, "308425279093478")
