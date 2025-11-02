"""Test with a COPY of user's Chrome profile to avoid conflicts."""

import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
import tempfile

def copy_profile_data():
    """Copy key files from user's Chrome profile to a temporary profile."""
    home = Path.home()
    chrome_profile = home / "Library" / "Application Support" / "Google" / "Chrome" / "Default"

    if not chrome_profile.exists():
        raise FileNotFoundError(f"Chrome Default profile not found at {chrome_profile}")

    # Create temporary profile directory
    temp_profile = Path(tempfile.mkdtemp(prefix="chrome_profile_"))
    temp_default = temp_profile / "Default"
    temp_default.mkdir(parents=True)

    print(f"\n  Copying profile from: {chrome_profile}")
    print(f"  To temporary location: {temp_default}")

    # Copy important files that contain trust signals
    files_to_copy = [
        "Cookies",
        "Preferences",
        "History",
        "Web Data",
        "Login Data",
        "Network/Cookies",
    ]

    for file_name in files_to_copy:
        source = chrome_profile / file_name
        if source.exists():
            dest = temp_default / file_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if source.is_file():
                    shutil.copy2(source, dest)
                    print(f"  ✓ Copied: {file_name}")
            except Exception as e:
                print(f"  ⚠ Skipped {file_name}: {e}")

    return str(temp_profile)

def test_with_profile_copy():
    """Test Cloudflare bypass using a copy of user's Chrome profile."""
    print("=" * 60)
    print("TESTING WITH COPIED CHROME PROFILE")
    print("=" * 60)

    try:
        print("\n1. Copying Chrome profile data...")
        profile_path = copy_profile_data()
        print(f"   ✓ Profile copied to: {profile_path}")
    except Exception as e:
        print(f"\n✗ Error copying profile: {e}")
        return False

    with sync_playwright() as p:
        print("\n2. Launching Chrome with copied profile...")

        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=False,
                channel='chrome',
                args=[
                    '--disable-blink-features=AutomationControlled',
                ],
                viewport={'width': 1920, 'height': 1080},
            )

            page = context.pages[0] if context.pages else context.new_page()
            print("   ✓ Chrome launched")

            # Navigate to Myki
            print("\n3. Navigating to Myki portal...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')
            print("   ✓ Page loaded")

            # Wait for Cloudflare
            print("\n4. Waiting 15 seconds for Cloudflare check...")
            time.sleep(15)

            # Check for Cloudflare
            print("\n5. Checking for Cloudflare...")
            try:
                cf_verifying = page.locator('text=Verifying').first.is_visible(timeout=2000)
                if cf_verifying:
                    print("   ⚠ Cloudflare 'Verifying' message detected")
                    print("   Waiting 30 more seconds...")
                    time.sleep(30)
                else:
                    print("   ✓ No 'Verifying' message detected")
            except:
                print("   ✓ No 'Verifying' message detected")

            # Check for login form
            print("\n6. Checking for login form...")
            time.sleep(3)

            form_found = False
            form_enabled = False

            try:
                username = page.locator('input[name="username"], input[type="text"], input[placeholder*="username" i]').first
                if username.is_visible(timeout=5000):
                    print("   ✓ Username field found!")
                    form_found = True

                    is_enabled = username.is_enabled()
                    print(f"   ✓ Username field enabled: {is_enabled}")

                    if is_enabled:
                        password = page.locator('input[name="password"], input[type="password"]').first
                        if password.is_visible(timeout=2000):
                            print("   ✓ Password field found!")
                            is_pass_enabled = password.is_enabled()
                            print(f"   ✓ Password field enabled: {is_pass_enabled}")

                            if is_pass_enabled:
                                form_enabled = True
                                print("\n" + "=" * 60)
                                print("SUCCESS! COPIED PROFILE BYPASSED CLOUDFLARE!")
                                print("=" * 60)

            except Exception as e:
                print(f"   ✗ Login form check error: {e}")

            # Analyze page content
            print("\n7. Analyzing page content...")
            content = page.content().lower()
            print(f"   - Has 'cloudflare': {'cloudflare' in content}")
            print(f"   - Has 'verifying': {'verifying' in content}")
            print(f"   - Has 'turnstile': {'turnstile' in content}")
            print(f"   - Has 'username': {'username' in content}")

            # Take screenshot
            page.screenshot(path='screenshots/profile_copy_result.png', full_page=True)
            print("\n  Screenshot saved to screenshots/profile_copy_result.png")

            # Keep browser open
            print("\nKeeping browser open for 60 seconds for inspection...")
            time.sleep(60)

            context.close()

            # Cleanup temp profile
            print("\n8. Cleaning up temporary profile...")
            shutil.rmtree(profile_path, ignore_errors=True)

            return form_enabled

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    import sys
    success = test_with_profile_copy()
    sys.exit(0 if success else 1)
