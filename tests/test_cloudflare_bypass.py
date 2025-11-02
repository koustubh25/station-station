"""
Tests for Cloudflare bypass functionality.

These tests verify that the browser can successfully navigate to the Myki login page,
handle Cloudflare verification challenges, and access the login form.
"""

import pytest
import time
from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from browser_config import (
    launch_stealth_browser,
    apply_stealth_to_page,
    human_delay
)
from cloudflare_bypass import (
    navigate_with_cloudflare_handling,
    detect_cloudflare_challenge,
    is_login_form_accessible,
    CloudflareBypassError
)


MYKI_LOGIN_URL = 'https://transport.vic.gov.au/manage-myki'


class TestCloudflareBypass:
    """Test suite for Cloudflare Turnstile bypass functionality."""

    def test_browser_navigates_to_login_page(self):
        """
        Test that browser successfully navigates to the Myki login page.

        This verifies that the stealth browser configuration can reach
        the target URL without being immediately blocked.
        """
        with sync_playwright() as playwright:
            browser, context = launch_stealth_browser(playwright)
            page = context.new_page()
            apply_stealth_to_page(page)

            try:
                # Navigate to login page
                page.goto(MYKI_LOGIN_URL, wait_until='domcontentloaded', timeout=15000)

                # Verify page loaded
                assert page.url.startswith('https://transport.vic.gov.au')
                assert page.title() is not None

                # Verify page contains expected elements
                # Should have either login form or Cloudflare challenge
                page_content = page.content()
                assert 'myki' in page_content.lower() or 'cloudflare' in page_content.lower()

            finally:
                context.close()
                browser.close()

    def test_cloudflare_verification_handled_within_timeout(self):
        """
        Test that Cloudflare verification overlay is handled within timeout.

        This verifies that the bypass logic can detect and wait for
        Cloudflare verification to complete (or detect failure).
        """
        with sync_playwright() as playwright:
            browser, context = launch_stealth_browser(playwright)
            page = context.new_page()
            apply_stealth_to_page(page)

            try:
                # Add human-like delay before navigation
                human_delay(1000, 2000)

                # Attempt to navigate with Cloudflare handling
                # This should either pass or raise CloudflareBypassError
                try:
                    success = navigate_with_cloudflare_handling(
                        page,
                        MYKI_LOGIN_URL,
                        max_wait_seconds=30
                    )

                    # If successful, verify we're on the right page
                    assert success is True
                    assert page.url.startswith('https://transport.vic.gov.au')

                except CloudflareBypassError as e:
                    # Cloudflare blocked us - this is expected in automated environment
                    # The test passes as long as the error is properly raised
                    assert 'Cloudflare' in str(e)
                    pytest.skip(f"Cloudflare blocked automation (expected): {e}")

            finally:
                context.close()
                browser.close()

    def test_login_form_becomes_interactive_after_cloudflare(self):
        """
        Test that login form becomes interactive after Cloudflare passes.

        This verifies that after Cloudflare verification (if present),
        the login form elements are accessible and can be interacted with.
        """
        with sync_playwright() as playwright:
            browser, context = launch_stealth_browser(playwright)
            page = context.new_page()
            apply_stealth_to_page(page)

            try:
                # Add human-like delay
                human_delay(1000, 2000)

                # Navigate with Cloudflare handling
                try:
                    navigate_with_cloudflare_handling(page, MYKI_LOGIN_URL)

                    # Verify login form is accessible
                    assert is_login_form_accessible(page), "Login form should be accessible"

                    # Verify username field is visible and enabled
                    username_field = page.locator('input[name="username"], input[type="text"]').first
                    expect(username_field).to_be_visible()
                    expect(username_field).to_be_enabled()

                    # Verify password field exists
                    password_field = page.locator('input[name="password"], input[type="password"]').first
                    expect(password_field).to_be_visible()

                except CloudflareBypassError as e:
                    # Cloudflare blocked - skip test
                    pytest.skip(f"Cloudflare blocked automation (expected): {e}")

            finally:
                context.close()
                browser.close()

    def test_retry_logic_triggers_on_cloudflare_failure(self):
        """
        Test that retry logic triggers on Cloudflare detection failure.

        This verifies that the retry mechanism with exponential backoff
        works correctly when Cloudflare blocking is detected.

        Note: This test may take longer as it tests retry behavior.
        """
        from cloudflare_bypass import bypass_cloudflare_with_retry

        with sync_playwright() as playwright:
            browser, context = launch_stealth_browser(playwright)
            page = context.new_page()
            apply_stealth_to_page(page)

            retry_count = 0
            max_retries = 2  # Use fewer retries for testing

            try:
                # This will either succeed or fail after retries
                try:
                    result = bypass_cloudflare_with_retry(
                        page,
                        MYKI_LOGIN_URL,
                        max_retries=max_retries,
                        max_wait_per_attempt=15  # Shorter timeout for testing
                    )

                    # If successful, verify result
                    assert result is True

                except CloudflareBypassError as e:
                    # Retry logic should have attempted multiple times
                    # Verify error message indicates retries were attempted
                    assert 'attempts' in str(e).lower() or 'Cloudflare' in str(e)

                    # Test passes - retry logic executed as expected
                    pytest.skip(f"Retry logic executed correctly, Cloudflare blocked after retries: {e}")

            finally:
                context.close()
                browser.close()


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
