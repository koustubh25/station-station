"""Test with user's actual Chrome profile to bypass Cloudflare."""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

def get_chrome_profile_path():
    """Get the default Chrome profile path on macOS."""
    home = Path.home()
    chrome_user_data = home / "Library" / "Application Support" / "Google" / "Chrome"

    if chrome_user_data.exists():
        return str(chrome_user_data)
    else:
        raise FileNotFoundError(f"Chrome profile not found at {chrome_user_data}")

def test_with_real_profile():
    """Test Cloudflare bypass using user's actual Chrome profile."""
    print("=" * 60)
    print("TESTING WITH REAL CHROME PROFILE")
    print("=" * 60)

    try:
        profile_path = get_chrome_profile_path()
        print(f"\n1. Found Chrome profile at: {profile_path}")
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        return False

    with sync_playwright() as p:
        print("\n2. Launching Chrome with your actual profile...")
        print("   NOTE: Close all Chrome windows first!")

        try:
            # Launch Chrome with user's profile
            # Note: Chrome must be completely closed for this to work
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=False,
                channel='chrome',
                args=[
                    '--disable-blink-features=AutomationControlled',
                ],
                # Use default viewport
                viewport={'width': 1920, 'height': 1080},
            )

            page = context.pages[0] if context.pages else context.new_page()

            print("   ✓ Chrome launched with your profile")

            # Navigate to Myki
            print("\n3. Navigating to Myki portal...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')
            print("   ✓ Page loaded")

            # Wait a bit for any Cloudflare challenge
            print("\n4. Waiting 10 seconds for Cloudflare check...")
            time.sleep(10)

            # Check for Cloudflare
            print("\n5. Checking for Cloudflare...")
            try:
                cf_verifying = page.locator('text=Verifying').first.is_visible(timeout=2000)
                if cf_verifying:
                    print("   ⚠ Cloudflare 'Verifying' message detected")
                    print("   Waiting 30 more seconds...")
                    time.sleep(30)
            except:
                print("   ✓ No 'Verifying' message detected")

            # Check for login form
            print("\n6. Checking for login form...")
            time.sleep(3)

            try:
                # Look for username field
                username = page.locator('input[name="username"], input[type="text"], input[placeholder*="username" i]').first
                if username.is_visible(timeout=5000):
                    print("   ✓ Username field found!")

                    # Check if it's actually enabled
                    is_enabled = username.is_enabled()
                    print(f"   ✓ Username field enabled: {is_enabled}")

                    # Look for password field
                    password = page.locator('input[name="password"], input[type="password"], input[placeholder*="password" i]').first
                    if password.is_visible(timeout=2000):
                        print("   ✓ Password field found!")
                        is_enabled = password.is_enabled()
                        print(f"   ✓ Password field enabled: {is_enabled}")

                        # Look for login button
                        login_btn = page.locator('button[type="submit"], button:has-text("Sign in"), button:has-text("Login")').first
                        if login_btn.is_visible(timeout=2000):
                            is_enabled = login_btn.is_enabled()
                            print(f"   ✓ Login button enabled: {is_enabled}")

                            if is_enabled:
                                print("\n" + "=" * 60)
                                print("SUCCESS! REAL CHROME PROFILE BYPASSED CLOUDFLARE!")
                                print("=" * 60)
                                print("\nThe form is accessible and interactive!")
                                print("This proves that your actual browser profile is trusted.")

                                # Take screenshot
                                page.screenshot(path='screenshots/real_profile_success.png', full_page=True)
                                print("\nScreenshot saved to screenshots/real_profile_success.png")

                                # Keep browser open
                                print("\nKeeping browser open for 30 seconds...")
                                time.sleep(30)
                                return True
                            else:
                                print("\n   ⚠ Form fields are disabled - Cloudflare still blocking")

            except Exception as e:
                print(f"   ✗ Login form not found or error: {e}")

            # Check page content
            print("\n7. Analyzing page content...")
            content = page.content().lower()

            print(f"   - Has 'cloudflare': {'cloudflare' in content}")
            print(f"   - Has 'verifying': {'verifying' in content}")
            print(f"   - Has 'turnstile': {'turnstile' in content}")
            print(f"   - Has 'username': {'username' in content}")

            # Take screenshot anyway
            page.screenshot(path='screenshots/real_profile_result.png', full_page=True)
            print("\nScreenshot saved to screenshots/real_profile_result.png")

            # Keep browser open for inspection
            print("\nKeeping browser open for 60 seconds for your inspection...")
            time.sleep(60)

            context.close()
            return False

        except Exception as e:
            print(f"\n✗ Error launching Chrome: {e}")
            print("\nMake sure:")
            print("  1. All Chrome windows are closed")
            print("  2. Chrome is not running in the background")
            print("  3. You have Chrome installed (not just Chromium)")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    import sys

    print("\n⚠ IMPORTANT: Make sure ALL Chrome windows were closed before running this!")
    print("Starting test now...\n")

    success = test_with_real_profile()
    sys.exit(0 if success else 1)
