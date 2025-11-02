"""Test using undetected-playwright for Cloudflare bypass."""

import sys
import time
from undetected_playwright.sync_api import sync_playwright
from cloudflare_bypass import detect_cloudflare_challenge, is_login_form_accessible

def test_with_undetected():
    """Test bypass using undetected-playwright."""
    with sync_playwright() as p:
        # Use undetected chromium
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
        )

        page = context.new_page()

        try:
            print("=" * 60)
            print("TESTING WITH UNDETECTED-PLAYWRIGHT")
            print("=" * 60)

            print("\n1. Navigating to Myki login page...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded', timeout=30000)
            print("   ✓ Page loaded")

            print("\n2. Waiting 10 seconds...")
            time.sleep(10)

            print("\n3. Checking for Cloudflare...")
            has_cloudflare = detect_cloudflare_challenge(page)
            print(f"   Cloudflare detected: {has_cloudflare}")

            if has_cloudflare:
                print("\n4. Waiting for Cloudflare to clear (max 60s)...")
                start = time.time()
                while time.time() - start < 60:
                    time.sleep(3)
                    if not detect_cloudflare_challenge(page):
                        print(f"   ✓ Cleared after {time.time() - start:.1f}s")
                        break
                    print(f"   Waiting... ({time.time() - start:.1f}s)")
                else:
                    print("   ✗ Still blocked")

            print("\n5. Checking form...")
            form_ok = is_login_form_accessible(page)
            print(f"   Form accessible: {form_ok}")

            if form_ok:
                print("\n" + "=" * 60)
                print("SUCCESS WITH UNDETECTED-PLAYWRIGHT!")
                print("=" * 60)
                time.sleep(30)
                return True
            else:
                print("\n" + "=" * 60)
                print("FAILED")
                print("=" * 60)
                page.screenshot(path='screenshots/undetected_failed.png', full_page=True)
                time.sleep(30)
                return False

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    success = test_with_undetected()
    sys.exit(0 if success else 1)
