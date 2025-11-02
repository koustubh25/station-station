"""Quick test script for iterating on Cloudflare bypass techniques."""

import sys
from playwright.sync_api import sync_playwright
from browser_config import launch_stealth_browser, apply_stealth_to_page, human_delay
from cloudflare_bypass import detect_cloudflare_challenge, is_login_form_accessible
import time

def test_cloudflare_bypass():
    """Test Cloudflare bypass with current configuration."""
    with sync_playwright() as p:
        browser, context = launch_stealth_browser(p)
        page = context.new_page()

        # Apply stealth
        apply_stealth_to_page(page)

        try:
            print("=" * 60)
            print("TESTING CLOUDFLARE BYPASS")
            print("=" * 60)

            # Navigate to login page
            print("\n1. Navigating to Myki login page...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded', timeout=30000)
            print("   ✓ Page loaded")

            # Wait for any challenges to appear
            print("\n2. Waiting 5 seconds for Cloudflare challenge...")
            time.sleep(5)

            # Check for Cloudflare
            print("\n3. Checking for Cloudflare challenge...")
            has_cloudflare = detect_cloudflare_challenge(page)
            print(f"   Cloudflare detected: {has_cloudflare}")

            if has_cloudflare:
                print("\n4. Cloudflare challenge found - waiting up to 60 seconds...")
                start = time.time()
                max_wait = 60

                while time.time() - start < max_wait:
                    time.sleep(2)
                    elapsed = time.time() - start

                    if not detect_cloudflare_challenge(page):
                        print(f"   ✓ Cloudflare challenge disappeared after {elapsed:.1f}s")
                        break
                    else:
                        print(f"   Still waiting... ({elapsed:.1f}s elapsed)")
                else:
                    print(f"   ✗ Cloudflare challenge still present after {max_wait}s")

            # Check login form accessibility
            print("\n5. Checking login form accessibility...")
            form_accessible = is_login_form_accessible(page)
            print(f"   Login form accessible: {form_accessible}")

            if form_accessible:
                print("\n" + "=" * 60)
                print("SUCCESS! Cloudflare bypass worked!")
                print("=" * 60)
                return True
            else:
                print("\n" + "=" * 60)
                print("FAILED - Login form not accessible")
                print("=" * 60)
                # Save screenshot
                page.screenshot(path='screenshots/cf_test_failed.png', full_page=True)
                print("Screenshot saved to: screenshots/cf_test_failed.png")
                return False

        finally:
            # Keep browser open for manual inspection
            print("\nBrowser will stay open for 30 seconds for manual inspection...")
            time.sleep(30)
            context.close()
            browser.close()

if __name__ == '__main__':
    success = test_cloudflare_bypass()
    sys.exit(0 if success else 1)
