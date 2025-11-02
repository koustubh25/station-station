"""Test different approaches to see which bypasses Turnstile."""

import time
from playwright.sync_api import sync_playwright
from profile_manager import ProfileManager


def test_approach_1_minimal():
    """Approach 1: Minimal config like check_turnstile.py."""
    print("\n" + "=" * 60)
    print("APPROACH 1: MINIMAL CONFIG (like check_turnstile.py)")
    print("=" * 60)

    profile_mgr = ProfileManager()
    profile_dir = profile_mgr.copy_profile()

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1920, 'height': 1080},
                # NO locale, NO timezone - use profile's natural settings
            )

            page = context.pages[0] if context.pages else context.new_page()

            print("Navigating to Myki...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')

            print("Waiting 40 seconds to see if Turnstile succeeds...")
            time.sleep(40)

            # Check for success/failure message
            try:
                refresh_msg = page.locator('text=Please refresh').first.is_visible(timeout=2000)
                if refresh_msg:
                    print("✗ FAILED - 'Please refresh' message appeared")
                    return False
                else:
                    print("✓ SUCCESS - No error message, login form should be enabled")
                    return True
            except:
                print("✓ SUCCESS - No error message detected")
                return True
            finally:
                context.close()
    finally:
        profile_mgr.cleanup()


def test_approach_2_warmup():
    """Approach 2: Visit Google first to warm up profile."""
    print("\n" + "=" * 60)
    print("APPROACH 2: WARM UP PROFILE (visit Google first)")
    print("=" * 60)

    profile_mgr = ProfileManager()
    profile_dir = profile_mgr.copy_profile()

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1920, 'height': 1080},
            )

            page = context.pages[0] if context.pages else context.new_page()

            # Visit Google first
            print("Visiting Google.com first to warm up...")
            page.goto('https://www.google.com')
            time.sleep(5)

            # Now go to Myki
            print("Now navigating to Myki...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')

            print("Waiting 40 seconds for Turnstile...")
            time.sleep(40)

            # Check for success/failure
            try:
                refresh_msg = page.locator('text=Please refresh').first.is_visible(timeout=2000)
                if refresh_msg:
                    print("✗ FAILED - 'Please refresh' message appeared")
                    return False
                else:
                    print("✓ SUCCESS - No error message")
                    return True
            except:
                print("✓ SUCCESS - No error message detected")
                return True
            finally:
                context.close()
    finally:
        profile_mgr.cleanup()


def test_approach_3_super_slow():
    """Approach 3: Add delays and slow down everything."""
    print("\n" + "=" * 60)
    print("APPROACH 3: SUPER SLOW (human-like timing)")
    print("=" * 60)

    profile_mgr = ProfileManager()
    profile_dir = profile_mgr.copy_profile()

    try:
        with sync_playwright() as p:
            print("Launching browser...")
            time.sleep(3)  # Delay before launch

            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1920, 'height': 1080},
            )

            print("Browser launched, waiting 5 seconds...")
            time.sleep(5)

            page = context.pages[0] if context.pages else context.new_page()

            print("Navigating to Myki...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')

            print("Waiting 50 seconds for Turnstile (extra slow)...")
            time.sleep(50)

            # Check for success/failure
            try:
                refresh_msg = page.locator('text=Please refresh').first.is_visible(timeout=2000)
                if refresh_msg:
                    print("✗ FAILED - 'Please refresh' message appeared")
                    return False
                else:
                    print("✓ SUCCESS - No error message")
                    return True
            except:
                print("✓ SUCCESS - No error message detected")
                return True
            finally:
                context.close()
    finally:
        profile_mgr.cleanup()


if __name__ == '__main__':
    print("Testing different approaches to bypass Cloudflare Turnstile")
    print("Watch the browser window for each approach")

    results = {}

    # Test each approach
    results['Approach 1 (Minimal)'] = test_approach_1_minimal()
    time.sleep(10)  # Wait between tests

    results['Approach 2 (Warmup)'] = test_approach_2_warmup()
    time.sleep(10)

    results['Approach 3 (Super Slow)'] = test_approach_3_super_slow()

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for approach, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{approach}: {status}")
