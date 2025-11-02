"""Test Cloudflare bypass using persistent browser context."""

import sys
import time
from playwright.sync_api import sync_playwright
from browser_config_v2 import launch_persistent_browser, warm_up_browser
from cloudflare_bypass import detect_cloudflare_challenge, is_login_form_accessible

def test_with_persistent_context():
    """Test bypass using persistent browser profile."""
    with sync_playwright() as p:
        context, page = launch_persistent_browser(p)

        try:
            print("=" * 60)
            print("TESTING WITH PERSISTENT BROWSER CONTEXT")
            print("=" * 60)

            # Warm up the browser first
            print("\n1. Warming up browser with normal browsing...")
            warm_up_browser(page)

            # Now navigate to target
            print("\n2. Navigating to Myki login page...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded', timeout=30000)
            print("   ✓ Page loaded")

            # Wait and check
            print("\n3. Waiting 10 seconds for any Cloudflare challenge...")
            time.sleep(10)

            print("\n4. Checking for Cloudflare...")
            has_cloudflare = detect_cloudflare_challenge(page)
            print(f"   Cloudflare detected: {has_cloudflare}")

            if has_cloudflare:
                print("\n5. Cloudflare detected - waiting up to 60s...")
                start = time.time()
                while time.time() - start < 60:
                    time.sleep(3)
                    if not detect_cloudflare_challenge(page):
                        print(f"   ✓ Cloudflare cleared after {time.time() - start:.1f}s")
                        break
                    print(f"   Still waiting... ({time.time() - start:.1f}s)")
                else:
                    print("   ✗ Cloudflare still blocking")

            # Check form
            print("\n6. Checking login form...")
            form_ok = is_login_form_accessible(page)
            print(f"   Form accessible: {form_ok}")

            if form_ok:
                print("\n" + "=" * 60)
                print("SUCCESS!")
                print("=" * 60)
                time.sleep(30)  # Keep open
                return True
            else:
                print("\n" + "=" * 60)
                print("FAILED")
                print("=" * 60)
                page.screenshot(path='screenshots/persistent_failed.png', full_page=True)
                time.sleep(30)  # Keep open
                return False

        finally:
            context.close()

if __name__ == '__main__':
    success = test_with_persistent_context()
    sys.exit(0 if success else 1)
