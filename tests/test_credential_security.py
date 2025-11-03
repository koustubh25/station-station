"""Tests for credential security enhancements.

Task Group 1: Backend Credential Security Schema Changes
- Test environment variable loading for username and card number
- Test config key uppercase conversion
- Test display username fallback
- Test error handling for missing credentials
"""

import pytest
import os
from src.config_manager import load_user_credentials, validate_user_config


class TestCredentialLoading:
    """Test credential loading from environment variables."""

    def test_load_username_from_env(self, monkeypatch):
        """Test username loading from MYKI_USERNAME_<KEY> environment variable."""
        user_config = {"koustubh": {"targetStation": "Test Station", "startDate": "2025-01-01"}}

        # Set environment variables
        monkeypatch.setenv("MYKI_USERNAME_KOUSTUBH", "koustubh25")
        monkeypatch.setenv("MYKI_CARDNUMBER_KOUSTUBH", "1234567890")
        monkeypatch.setenv("MYKI_PASSWORD_KOUSTUBH", "test_password")

        credentials = load_user_credentials(user_config)

        assert "koustubh" in credentials
        assert credentials["koustubh"]["username"] == "koustubh25"

    def test_load_card_number_from_env(self, monkeypatch):
        """Test card number loading from MYKI_CARDNUMBER_<KEY> environment variable."""
        user_config = {"koustubh": {"targetStation": "Test Station", "startDate": "2025-01-01"}}

        # Set environment variables
        monkeypatch.setenv("MYKI_USERNAME_KOUSTUBH", "koustubh25")
        monkeypatch.setenv("MYKI_CARDNUMBER_KOUSTUBH", "1234567890")
        monkeypatch.setenv("MYKI_PASSWORD_KOUSTUBH", "test_password")

        credentials = load_user_credentials(user_config)

        assert "koustubh" in credentials
        assert credentials["koustubh"]["card_number"] == "1234567890"

    def test_config_key_uppercase_conversion(self, monkeypatch):
        """Test that config key is converted to uppercase for environment variable names."""
        user_config = {"john_doe": {"targetStation": "Test Station", "startDate": "2025-01-01"}}

        # Set environment variables with uppercase config key
        monkeypatch.setenv("MYKI_USERNAME_JOHN_DOE", "johndoe123")
        monkeypatch.setenv("MYKI_CARDNUMBER_JOHN_DOE", "9876543210")
        monkeypatch.setenv("MYKI_PASSWORD_JOHN_DOE", "test_password")

        credentials = load_user_credentials(user_config)

        assert "john_doe" in credentials
        assert credentials["john_doe"]["username"] == "johndoe123"
        assert credentials["john_doe"]["card_number"] == "9876543210"

    def test_missing_username_env_raises_error(self, monkeypatch):
        """Test that missing MYKI_USERNAME_* environment variable raises clear error."""
        user_config = {"koustubh": {"targetStation": "Test Station", "startDate": "2025-01-01"}}

        # Only set password, not username
        monkeypatch.setenv("MYKI_CARDNUMBER_KOUSTUBH", "1234567890")
        monkeypatch.setenv("MYKI_PASSWORD_KOUSTUBH", "test_password")

        with pytest.raises(ValueError) as exc_info:
            load_user_credentials(user_config)

        assert "MYKI_USERNAME_KOUSTUBH" in str(exc_info.value)

    def test_missing_cardnumber_env_raises_error(self, monkeypatch):
        """Test that missing MYKI_CARDNUMBER_* environment variable raises clear error."""
        user_config = {"koustubh": {"targetStation": "Test Station", "startDate": "2025-01-01"}}

        # Only set password, not card number
        monkeypatch.setenv("MYKI_USERNAME_KOUSTUBH", "koustubh25")
        monkeypatch.setenv("MYKI_PASSWORD_KOUSTUBH", "test_password")

        with pytest.raises(ValueError) as exc_info:
            load_user_credentials(user_config)

        assert "MYKI_CARDNUMBER_KOUSTUBH" in str(exc_info.value)

    def test_display_username_fallback_to_config_key(self, monkeypatch):
        """Test that display username falls back to config key when not provided."""
        user_config = {"koustubh": {"targetStation": "Test Station", "startDate": "2025-01-01"}}

        # Set environment variables
        monkeypatch.setenv("MYKI_USERNAME_KOUSTUBH", "koustubh25")
        monkeypatch.setenv("MYKI_CARDNUMBER_KOUSTUBH", "1234567890")
        monkeypatch.setenv("MYKI_PASSWORD_KOUSTUBH", "test_password")

        credentials = load_user_credentials(user_config)

        # Display username should default to config key if not in config
        assert credentials["koustubh"]["display_username"] == "koustubh"

    def test_display_username_from_config(self, monkeypatch):
        """Test that display username is read from config when provided."""
        user_config = {
            "koustubh": {
                "username": "Koustubh Gaikwad",
                "targetStation": "Test Station",
                "startDate": "2025-01-01"
            }
        }

        # Set environment variables
        monkeypatch.setenv("MYKI_USERNAME_KOUSTUBH", "koustubh25")
        monkeypatch.setenv("MYKI_CARDNUMBER_KOUSTUBH", "1234567890")
        monkeypatch.setenv("MYKI_PASSWORD_KOUSTUBH", "test_password")

        credentials = load_user_credentials(user_config)

        # Display username should come from config
        assert credentials["koustubh"]["display_username"] == "Koustubh Gaikwad"


class TestConfigSchemaValidation:
    """Test config schema validation for security changes."""

    def test_config_rejects_mykiCardNumber_field(self):
        """Test that config validation rejects configs with mykiCardNumber field."""
        user_config = {
            "koustubh": {
                "mykiCardNumber": "1234567890",  # This should be rejected
                "targetStation": "Test Station",
                "startDate": "2025-01-01"
            }
        }

        with pytest.raises(ValueError) as exc_info:
            validate_user_config(user_config)

        assert "mykicardnumber" in str(exc_info.value).lower()
        assert "not allowed" in str(exc_info.value).lower() or "forbidden" in str(exc_info.value).lower()
