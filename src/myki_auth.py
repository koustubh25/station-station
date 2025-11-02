"""Myki authentication with Cloudflare bypass using Chrome profile trust signals.

This module authenticates with the Myki portal using a profile-based approach
that bypasses Cloudflare Turnstile detection by leveraging browser trust signals.
"""

import os
import time
import random
import json
from typing import Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from profile_manager import ProfileManager
from auth_loader import get_session_suffix


class MykiAuthenticator:
    """Handles Myki authentication with Cloudflare bypass."""

    MYKI_URL = "https://transport.vic.gov.au/manage-myki"
    AUTH_TIMEOUT = 60  # seconds

    def __init__(self):
        """Initialize authenticator."""
        load_dotenv()
        self.username = os.getenv("MYKI_USERNAME")
        self.password = os.getenv("MYKI_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "MYKI_USERNAME and MYKI_PASSWORD must be set in .env file"
            )

        self.profile_manager = ProfileManager()

    def launch_browser_with_profile(self, playwright, profile_dir: Path) -> BrowserContext:
        """Launch browser with copied profile to bypass Cloudflare.

        Args:
            playwright: Playwright instance
            profile_dir: Path to temporary profile directory

        Returns:
            Browser context
        """
        print("\nLaunching Chrome with profile...")

        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            channel='chrome',
            args=[
                '--disable-blink-features=AutomationControlled',
            ],
            viewport={'width': 1920, 'height': 1080},
            # Use profile's natural locale/timezone settings - don't override
        )

        print("  ✓ Chrome launched")
        return context

    def check_cloudflare(self, page: Page, wait_seconds: int = 15) -> bool:
        """Check for Cloudflare verification and wait for it to complete.

        Args:
            page: Playwright page
            wait_seconds: Seconds to wait for Cloudflare

        Returns:
            True if Cloudflare cleared, False if still blocking
        """
        print(f"\nWaiting {wait_seconds} seconds for Cloudflare check...")
        time.sleep(wait_seconds)

        try:
            cf_verifying = page.locator('text=Verifying').first.is_visible(timeout=2000)
            if cf_verifying:
                print("  ⚠ Cloudflare 'Verifying' message still present")
                return False
            else:
                print("  ✓ No Cloudflare blocking detected")
                return True
        except:
            print("  ✓ No Cloudflare blocking detected")
            return True

    def check_login_form(self, page: Page) -> Tuple[bool, bool]:
        """Check if login form is visible and enabled.

        Args:
            page: Playwright page

        Returns:
            Tuple of (form_found, form_enabled)
        """
        print("\nChecking for login form...")
        time.sleep(3)

        try:
            username_field = page.locator(
                'input[name="username"], input[type="text"], input[placeholder*="username" i]'
            ).first

            if username_field.is_visible(timeout=5000):
                print("  ✓ Username field found")
                is_enabled = username_field.is_enabled()
                print(f"  ✓ Username field enabled: {is_enabled}")

                if is_enabled:
                    password_field = page.locator(
                        'input[name="password"], input[type="password"]'
                    ).first

                    if password_field.is_visible(timeout=2000):
                        print("  ✓ Password field found")
                        is_pass_enabled = password_field.is_enabled()
                        print(f"  ✓ Password field enabled: {is_pass_enabled}")
                        return (True, is_pass_enabled)

                return (True, False)
            else:
                print("  ✗ Login form not visible")
                return (False, False)

        except Exception as e:
            print(f"  ✗ Login form check error: {e}")
            return (False, False)

    def add_human_behavior(self, page: Page):
        """Add realistic human behavior before interacting with form.

        Args:
            page: Playwright page
        """
        print("\nSimulating human behavior...")

        # Random mouse movements
        for _ in range(3):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))

        # Scroll slightly
        page.evaluate("window.scrollBy(0, 100)")
        time.sleep(random.uniform(0.5, 1.0))
        page.evaluate("window.scrollBy(0, -50)")
        time.sleep(random.uniform(0.3, 0.7))

        print("  ✓ Human behavior simulated")

    def fill_login_form(self, page: Page) -> Dict:
        """Fill and submit login form with human-like behavior.

        Args:
            page: Playwright page

        Returns:
            Dictionary containing authentication request and response details
        """
        print("\nFilling login form...")

        # Set up network monitoring to capture auth POST request and response
        auth_request_data = {}

        def handle_request(request):
            if '/authenticate' in request.url and request.method == 'POST':
                print(f"  → Captured authenticate POST request: {request.url}")
                auth_request_data['url'] = request.url
                auth_request_data['method'] = request.method
                auth_request_data['headers'] = request.headers
                auth_request_data['post_data'] = request.post_data

        def handle_response(response):
            if '/authenticate' in response.url and response.request.method == 'POST':
                print(f"  → Captured authenticate response: {response.status}")
                auth_request_data['response_status'] = response.status
                auth_request_data['response_headers'] = dict(response.headers)

                # Capture response body
                try:
                    response_text = response.text()
                    auth_request_data['response_body'] = response_text
                    # Try to parse as JSON
                    try:
                        import json
                        response_json = json.loads(response_text)
                        auth_request_data['response_json'] = response_json
                        print(f"  → Response JSON captured")

                        # Look for Bearer token in response
                        if 'token' in response_json:
                            print(f"  → Found 'token' in response!")
                        if 'accessToken' in response_json:
                            print(f"  → Found 'accessToken' in response!")
                        if 'bearerToken' in response_json:
                            print(f"  → Found 'bearerToken' in response!")

                    except json.JSONDecodeError:
                        print(f"  → Response is not JSON")
                except Exception as e:
                    print(f"  ⚠ Could not read response body: {e}")

        page.on('request', handle_request)
        page.on('response', handle_response)

        # Wait and observe like a human would
        print("  - Pausing to 'read' the page...")
        time.sleep(random.uniform(2.0, 4.0))

        # Add some mouse movement before clicking
        self.add_human_behavior(page)

        # Click username field first (like a human would)
        username_field = page.locator(
            'input[name="username"], input[type="text"], input[placeholder*="username" i]'
        ).first
        username_field.click()
        time.sleep(random.uniform(0.3, 0.7))

        # Type username slowly with realistic delays
        username_field.type(self.username, delay=random.randint(80, 150))
        print("  ✓ Username typed")

        # Pause between fields
        time.sleep(random.uniform(0.5, 1.2))

        # Click password field
        password_field = page.locator(
            'input[name="password"], input[type="password"]'
        ).first
        password_field.click()
        time.sleep(random.uniform(0.3, 0.7))

        # Type password slowly
        password_field.type(self.password, delay=random.randint(80, 150))
        print("  ✓ Password typed")

        # Human pause before clicking submit
        print("  - Pausing before submit...")
        time.sleep(random.uniform(1.5, 3.0))

        # Use more specific selector for login button
        login_button = page.locator(
            'button.login-form__button[type="submit"]'
        ).first

        # Verify button is visible and enabled
        if not login_button.is_visible(timeout=5000):
            print("  ✗ Login button not visible!")
            return auth_request_data

        if not login_button.is_enabled():
            print("  ✗ Login button not enabled!")
            return auth_request_data

        print("  ✓ Login button is visible and enabled")

        # Get button position and move mouse
        box = login_button.bounding_box()
        if box:
            # Move mouse near button
            page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            time.sleep(random.uniform(0.3, 0.6))

        # Click login button
        print("\nClicking login button...")
        try:
            login_button.click(timeout=10000)
            print("  ✓ Login button clicked")
        except Exception as e:
            print(f"  ✗ Error clicking login button: {e}")
            # Try JavaScript click as fallback
            print("  → Trying JavaScript click...")
            page.evaluate('document.querySelector("button.login-form__button[type=submit]").click()')
            print("  ✓ JavaScript click executed")

        # Wait for authenticate request to complete
        print("  - Waiting for authentication request...")
        time.sleep(random.uniform(3.0, 5.0))

        return auth_request_data

    def wait_for_dashboard(self, page: Page, timeout: int = 15) -> bool:
        """Wait for dashboard to load after login.

        Args:
            page: Playwright page
            timeout: Timeout in seconds

        Returns:
            True if dashboard loaded, False otherwise
        """
        print(f"\nWaiting for dashboard (timeout: {timeout}s)...")

        # First check for Cloudflare blocking message
        try:
            refresh_msg = page.locator('text=Please refresh and try again').first
            if refresh_msg.is_visible(timeout=2000):
                print("  ✗ Cloudflare blocked login submission")
                print("  ✗ Error: 'Please refresh and try again' message detected")
                return False
        except:
            pass  # No refresh message, continue

        # Check if login button is disabled (Cloudflare block indicator)
        try:
            login_btn = page.locator('button[type="submit"]').first
            if login_btn.is_visible(timeout=2000):
                is_disabled = page.evaluate(
                    '(el) => el.disabled || el.getAttribute("disabled") !== null',
                    login_btn.element_handle()
                )
                if is_disabled:
                    print("  ✗ Login button disabled - Cloudflare blocked submission")
                    return False
        except:
            pass

        # Check for dashboard element
        try:
            # Wait for dashboard element
            dashboard = page.locator('div.myki-tabs__tab-menu[role="tablist"]').first
            dashboard.wait_for(state='visible', timeout=timeout * 1000)

            # Double-check we're actually on dashboard, not still on login page
            try:
                # If we can still see username field, we're not on dashboard
                username_field = page.locator('input[name="username"]').first
                if username_field.is_visible(timeout=1000):
                    print("  ✗ Still on login page - authentication failed")
                    return False
            except:
                pass  # Username field not visible, good sign

            print("  ✓ Dashboard loaded successfully")
            return True
        except Exception as e:
            print(f"  ✗ Dashboard not loaded: {e}")
            return False

    def extract_cookies(self, context: BrowserContext) -> Dict:
        """Extract authentication cookies.

        Args:
            context: Browser context

        Returns:
            Dictionary of cookies
        """
        print("\nExtracting cookies...")
        cookies = context.cookies()

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
            print(f"  ✓ {cookie['name']}")

        return cookie_dict

    def extract_headers(self, page: Page) -> Dict:
        """Extract authentication headers.

        Args:
            page: Playwright page

        Returns:
            Dictionary of headers
        """
        print("\nExtracting headers...")

        headers = {
            'User-Agent': page.evaluate('navigator.userAgent'),
            'Origin': 'https://transport.vic.gov.au',
            'Referer': 'https://transport.vic.gov.au/',
        }

        print(f"  ✓ User-Agent: {headers['User-Agent'][:50]}...")
        print(f"  ✓ Origin: {headers['Origin']}")
        print(f"  ✓ Referer: {headers['Referer']}")

        return headers

    def save_auth_data(self, cookies: Dict, headers: Dict, auth_request_data: Dict):
        """Save authentication data to files for later use.

        Supports multi-user sessions via MYKI_AUTH_USERNAME_KEY environment variable.

        Args:
            cookies: Cookie dictionary
            headers: Headers dictionary
            auth_request_data: Authentication request and response data
        """
        # Create auth_data directory if it doesn't exist
        # Support environment variable override for Docker permission issues
        auth_data_dir = Path(os.getenv('AUTH_DATA_DIR', 'auth_data'))
        auth_data_dir.mkdir(exist_ok=True)

        # Get session suffix for multi-user support
        suffix = get_session_suffix()

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Extract Bearer token from auth response
        bearer_token = None
        if auth_request_data and 'response_json' in auth_request_data:
            response_json = auth_request_data['response_json']
            if isinstance(response_json, dict) and 'data' in response_json:
                bearer_token = response_json['data'].get('token')
                if bearer_token:
                    print(f"\n  ✓ Extracted Bearer token from auth response")
                    print(f"    Token: {bearer_token[:50]}...")

        # Save cookies (with user suffix if multi-user)
        cookies_file = auth_data_dir / f'cookies{suffix}.json'
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        print(f"  ✓ Cookies saved to: {cookies_file}")

        # Save headers (with user suffix if multi-user)
        headers_file = auth_data_dir / f'headers{suffix}.json'
        with open(headers_file, 'w') as f:
            json.dump(headers, f, indent=2)
        print(f"  ✓ Headers saved to: {headers_file}")

        # Save auth request data (with user suffix if multi-user)
        if auth_request_data:
            auth_request_file = auth_data_dir / f'auth_request{suffix}.json'
            with open(auth_request_file, 'w') as f:
                json.dump(auth_request_data, f, indent=2)
            print(f"  ✓ Auth request data saved to: {auth_request_file}")

        # Save Bearer token separately for easy access (with user suffix if multi-user)
        if bearer_token:
            bearer_token_file = auth_data_dir / f'bearer_token{suffix}.txt'
            with open(bearer_token_file, 'w') as f:
                f.write(bearer_token)
            print(f"  ✓ Bearer token saved to: {bearer_token_file}")

        # Save combined session data with timestamp (with user suffix if multi-user)
        session_data = {
            'timestamp': timestamp,
            'cookies': cookies,
            'headers': headers,
            'auth_request': auth_request_data,
            'bearer_token': bearer_token
        }
        session_file = auth_data_dir / f'session{suffix}.json'
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        print(f"  ✓ Complete session saved to: {session_file}")

        # Also save a timestamped backup (with user suffix if multi-user)
        backup_file = auth_data_dir / f'session{suffix}_{timestamp}.json'
        with open(backup_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        print(f"  ✓ Backup saved to: {backup_file}")

    def authenticate(self) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], bool]:
        """Perform full authentication flow.

        Returns:
            Tuple of (cookies, headers, auth_request_data, success)
        """
        print("=" * 60)
        print("MYKI AUTHENTICATION WITH PROFILE-BASED CLOUDFLARE BYPASS")
        print("=" * 60)

        try:
            # Copy Chrome profile
            print("\n1. Copying Chrome profile...")
            profile_dir = self.profile_manager.copy_profile()
            print(f"  ✓ Profile ready: {profile_dir}")

            with sync_playwright() as p:
                # Launch browser with profile
                print("\n2. Launching browser with profile...")
                context = self.launch_browser_with_profile(p, profile_dir)
                page = context.pages[0] if context.pages else context.new_page()

                try:
                    # Navigate to Myki
                    print("\n3. Navigating to Myki portal...")
                    page.goto(self.MYKI_URL, wait_until='domcontentloaded')
                    print("  ✓ Page loaded")

                    # Wait for Cloudflare Turnstile to complete
                    print("\n4. Waiting for Cloudflare Turnstile to complete...")
                    print("   (Invisible Turnstile widget needs time to verify)")
                    time.sleep(35)  # Give Turnstile time to complete in background

                    cloudflare_cleared = self.check_cloudflare(page, wait_seconds=0)

                    if not cloudflare_cleared:
                        print("  ⚠ Waiting additional 15 seconds...")
                        time.sleep(15)
                        cloudflare_cleared = self.check_cloudflare(page, wait_seconds=0)

                    # Check login form
                    print("\n5. Verifying login form...")
                    form_found, form_enabled = self.check_login_form(page)

                    if not form_found or not form_enabled:
                        # Take screenshot
                        screenshots_dir = os.getenv('SCREENSHOTS_DIR', 'screenshots')
                        screenshot_path = os.path.join(screenshots_dir, 'auth_form_not_ready.png')
                        page.screenshot(path=screenshot_path, full_page=True)
                        print(f"\n  ✗ Login form not ready. Screenshot: {screenshot_path}")
                        return (None, None, None, False)

                    # Fill and submit login
                    print("\n6. Logging in...")
                    auth_request_data = self.fill_login_form(page)

                    # Display captured auth request
                    if auth_request_data:
                        print("\n  → Authentication request captured:")
                        print(f"     URL: {auth_request_data.get('url', 'N/A')}")
                        print(f"     Method: {auth_request_data.get('method', 'N/A')}")
                        if auth_request_data.get('headers'):
                            print(f"     Headers: {len(auth_request_data['headers'])} headers captured")

                    # Wait for dashboard
                    print("\n7. Waiting for dashboard...")
                    dashboard_loaded = self.wait_for_dashboard(page)

                    if not dashboard_loaded:
                        screenshot_path = 'screenshots/auth_dashboard_failed.png'
                        page.screenshot(path=screenshot_path, full_page=True)
                        print(f"\n  ✗ Dashboard not loaded. Screenshot: {screenshot_path}")
                        return (None, None, None, False)

                    # Extract session data
                    print("\n8. Extracting session data...")
                    cookies = self.extract_cookies(context)
                    headers = self.extract_headers(page)

                    # Success!
                    print("\n" + "=" * 60)
                    print("AUTHENTICATION SUCCESSFUL!")
                    print("=" * 60)
                    print(f"\nExtracted {len(cookies)} cookies")
                    print(f"Extracted {len(headers)} headers")
                    if auth_request_data:
                        print(f"Captured authentication POST request with {len(auth_request_data.get('headers', {}))} headers")

                    # Save authentication data to files
                    print("\n9. Saving authentication data to files...")
                    self.save_auth_data(cookies, headers, auth_request_data)

                    # Take success screenshot
                    page.screenshot(path='screenshots/auth_success.png', full_page=True)
                    print("\nScreenshot saved: screenshots/auth_success.png")

                    # Keep browser open briefly
                    print("\nKeeping browser open for 5 seconds...")
                    time.sleep(5)

                    return (cookies, headers, auth_request_data, True)

                finally:
                    context.close()

        except Exception as e:
            print(f"\n✗ Authentication error: {e}")
            import traceback
            traceback.print_exc()
            return (None, None, None, False)

        finally:
            # Cleanup profile
            self.profile_manager.cleanup()


def main():
    """Main entry point."""
    try:
        authenticator = MykiAuthenticator()
        cookies, headers, auth_request_data, success = authenticator.authenticate()

        if success:
            print("\n" + "=" * 60)
            print("SESSION DATA READY FOR API CALLS")
            print("=" * 60)
            print(f"\nCookies: {list(cookies.keys())}")
            print(f"Headers: {list(headers.keys())}")

            if auth_request_data and auth_request_data.get('headers'):
                print(f"\nAuthentication POST request headers:")
                for key, value in auth_request_data['headers'].items():
                    # Don't print full cookie values for security
                    if key.lower() == 'cookie':
                        print(f"  {key}: [REDACTED]")
                    else:
                        print(f"  {key}: {value}")

            return 0
        else:
            print("\n" + "=" * 60)
            print("AUTHENTICATION FAILED")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
