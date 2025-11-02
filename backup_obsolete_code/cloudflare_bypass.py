"""
Cloudflare Turnstile bypass implementation.

This module handles detection and bypass of Cloudflare verification challenges
using stealth browser configuration and retry logic.
"""

import time
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CloudflareBypassError(Exception):
    """Raised when Cloudflare bot detection cannot be bypassed."""
    pass


def detect_cloudflare_challenge(page: Page) -> bool:
    """
    Detect if Cloudflare verification challenge is present on the page.

    Args:
        page: Playwright page to check for Cloudflare challenge.

    Returns:
        True if Cloudflare challenge is detected, False otherwise.
    """
    try:
        # Check for Cloudflare "Verifying..." text
        verifying_text = page.locator('text=Verifying').first
        if verifying_text.is_visible(timeout=1000):
            logger.info("Cloudflare 'Verifying...' overlay detected")
            return True

        # Check for Cloudflare logo/branding
        cloudflare_logo = page.locator('[alt*="Cloudflare"], [title*="Cloudflare"]').first
        if cloudflare_logo.is_visible(timeout=1000):
            logger.info("Cloudflare branding detected")
            return True

        # Check for Cloudflare Turnstile widget iframe
        turnstile_iframe = page.frame_locator('iframe[src*="challenges.cloudflare.com"]').first
        if turnstile_iframe:
            logger.info("Cloudflare Turnstile iframe detected")
            return True

    except Exception as e:
        logger.debug(f"Cloudflare detection check error (may be normal): {e}")

    return False


def try_interact_with_turnstile(page: Page) -> bool:
    """
    Try to interact with Cloudflare Turnstile widget to trigger verification.

    Args:
        page: Playwright page with Turnstile widget.

    Returns:
        True if interaction successful, False otherwise.
    """
    try:
        # Look for the Turnstile iframe
        turnstile_frames = page.frames
        for frame in turnstile_frames:
            if 'challenges.cloudflare.com' in frame.url:
                logger.info("Found Turnstile iframe, attempting to interact...")

                # Wait a moment for the iframe to fully load
                time.sleep(2)

                # Try to find and click the checkbox/widget inside the iframe
                try:
                    # Look for common Turnstile selectors
                    selectors = [
                        'input[type="checkbox"]',
                        '.cf-turnstile',
                        '#cf-turnstile',
                        '[id*="turnstile"]',
                        '[class*="turnstile"]',
                    ]

                    for selector in selectors:
                        try:
                            element = frame.locator(selector).first
                            if element.is_visible(timeout=1000):
                                logger.info(f"Clicking Turnstile element: {selector}")
                                element.click(timeout=2000)
                                time.sleep(1)
                                return True
                        except Exception:
                            continue

                except Exception as e:
                    logger.debug(f"Could not interact with Turnstile iframe: {e}")

        return False

    except Exception as e:
        logger.debug(f"Turnstile interaction error: {e}")
        return False


def wait_for_cloudflare_completion(page: Page, max_wait_seconds: int = 30) -> bool:
    """
    Wait for Cloudflare verification to complete.

    Args:
        page: Playwright page with Cloudflare challenge.
        max_wait_seconds: Maximum time to wait for challenge completion (default: 30)

    Returns:
        True if Cloudflare challenge passed, False if failed or timed out.

    Raises:
        CloudflareBypassError: If Cloudflare blocks access or times out.
    """
    logger.info(f"Waiting for Cloudflare verification to complete (max {max_wait_seconds}s)...")
    start_time = time.time()

    # Try to interact with Turnstile widget
    try_interact_with_turnstile(page)

    while time.time() - start_time < max_wait_seconds:
        # Check if challenge is still present
        if not detect_cloudflare_challenge(page):
            # Check if login form is now accessible
            if is_login_form_accessible(page):
                elapsed_time = time.time() - start_time
                logger.info(f"Cloudflare verification passed after {elapsed_time:.2f}s")
                return True

        # Periodically try to interact again
        if int(time.time() - start_time) % 5 == 0:
            try_interact_with_turnstile(page)

        # Wait a bit before checking again
        time.sleep(0.5)

    # Timeout reached
    elapsed_time = time.time() - start_time
    logger.error(f"Cloudflare verification timeout after {elapsed_time:.2f}s")
    return False


def is_login_form_accessible(page: Page) -> bool:
    """
    Check if the login form is accessible and interactive.

    Args:
        page: Playwright page to check.

    Returns:
        True if login form is accessible, False otherwise.
    """
    try:
        # Check for username field
        username_field = page.locator('input[name="username"], input[type="text"]').first
        if username_field.is_visible(timeout=2000) and username_field.is_enabled():
            logger.debug("Login form username field is accessible")
            return True
    except Exception as e:
        logger.debug(f"Login form accessibility check failed: {e}")

    return False


def capture_failure_screenshot(page: Page, reason: str = "cloudflare_failure") -> str:
    """
    Capture screenshot on Cloudflare bypass failure for debugging.

    Args:
        page: Playwright page to screenshot.
        reason: Reason for failure (used in filename).

    Returns:
        Path to saved screenshot file.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{reason}_{timestamp}.png"
    screenshots_dir = Path(__file__).parent.parent / 'screenshots'
    screenshots_dir.mkdir(exist_ok=True)
    filepath = screenshots_dir / filename

    try:
        page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Failure screenshot saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return ""


def capture_browser_console_errors(page: Page) -> list:
    """
    Capture browser console errors for debugging.

    Args:
        page: Playwright page to capture console from.

    Returns:
        List of console error messages.
    """
    console_errors = []

    def handle_console(msg):
        if msg.type == 'error':
            console_errors.append(msg.text)
            logger.debug(f"Browser console error: {msg.text}")

    page.on('console', handle_console)
    return console_errors


def navigate_with_cloudflare_handling(
    page: Page,
    url: str,
    max_wait_seconds: int = 30
) -> bool:
    """
    Navigate to URL and handle Cloudflare verification if present.

    Args:
        page: Playwright page to navigate.
        url: URL to navigate to.
        max_wait_seconds: Maximum time to wait for Cloudflare (default: 30)

    Returns:
        True if navigation successful and Cloudflare passed (if present).

    Raises:
        CloudflareBypassError: If Cloudflare blocks access.
    """
    logger.info(f"Navigating to {url}")

    try:
        # Navigate to page
        page.goto(url, wait_until='domcontentloaded', timeout=15000)
        logger.info("Page loaded successfully")

        # Wait a moment for any Cloudflare challenge to appear
        time.sleep(2)

        # Check for Cloudflare challenge
        if detect_cloudflare_challenge(page):
            logger.warning("Cloudflare challenge detected, waiting for completion...")

            # Wait for challenge to complete
            if not wait_for_cloudflare_completion(page, max_wait_seconds):
                # Cloudflare failed - capture debugging info
                screenshot_path = capture_failure_screenshot(page, "cloudflare_timeout")
                raise CloudflareBypassError(
                    f"Cloudflare verification timeout after {max_wait_seconds}s. "
                    f"Screenshot saved: {screenshot_path}"
                )
        else:
            logger.info("No Cloudflare challenge detected or already passed")

        # Verify login form is accessible
        if not is_login_form_accessible(page):
            screenshot_path = capture_failure_screenshot(page, "login_form_inaccessible")
            raise CloudflareBypassError(
                f"Login form not accessible after navigation. "
                f"Screenshot saved: {screenshot_path}"
            )

        return True

    except PlaywrightTimeoutError as e:
        screenshot_path = capture_failure_screenshot(page, "navigation_timeout")
        raise CloudflareBypassError(
            f"Page navigation timeout: {e}. Screenshot saved: {screenshot_path}"
        ) from e


def bypass_cloudflare_with_retry(
    page: Page,
    url: str,
    max_retries: int = 3,
    max_wait_per_attempt: int = 30
) -> bool:
    """
    Attempt to bypass Cloudflare with exponential backoff retry logic.

    Args:
        page: Playwright page to use.
        url: URL to navigate to.
        max_retries: Maximum number of retry attempts (default: 3)
        max_wait_per_attempt: Max wait time per attempt (default: 30s)

    Returns:
        True if bypass successful.

    Raises:
        CloudflareBypassError: If all retry attempts fail.
    """
    retry_delays = [2, 4, 8]  # Exponential backoff in seconds

    for attempt in range(1, max_retries + 1):
        logger.info(f"Cloudflare bypass attempt {attempt}/{max_retries}")

        try:
            return navigate_with_cloudflare_handling(page, url, max_wait_per_attempt)

        except CloudflareBypassError as e:
            if attempt < max_retries:
                delay = retry_delays[attempt - 1]
                logger.warning(
                    f"Attempt {attempt} failed: {e}. "
                    f"Retrying in {delay} seconds..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries} bypass attempts failed")
                raise CloudflareBypassError(
                    f"Cloudflare bot detection triggered after {max_retries} attempts. "
                    f"Last error: {e}"
                ) from e

    return False
