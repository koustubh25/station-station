"""
Hybrid Cloudflare bypass: cloudscraper + Playwright

Strategy:
1. Use cloudscraper to bypass Cloudflare and obtain valid cookies
2. Transfer cookies to Playwright browser session
3. Use Playwright to interact with JavaScript-rendered login form
"""

import cloudscraper
from playwright.sync_api import sync_playwright
import time

def get_cloudflare_cookies():
    """
    Use cloudscraper to bypass Cloudflare and get valid cookies.

    Returns:
        dict: Cookies from cloudscraper session
    """
    print("Step 1: Using cloudscraper to bypass Cloudflare...")

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'desktop': True
        }
    )

    url = 'https://transport.vic.gov.au/manage-myki'
    response = scraper.get(url, timeout=30)

    print(f"  ✓ Got response: {response.status_code}")

    cookies = scraper.cookies.get_dict()
    print(f"  ✓ Obtained {len(cookies)} cookies from cloudscraper")
    for name in cookies.keys():
        print(f"    - {name}")

    return cookies, scraper.cookies


def test_hybrid_approach():
    """Test the hybrid cloudscraper + Playwright approach."""
    print("=" * 60)
    print("HYBRID APPROACH: Cloudscraper + Playwright")
    print("=" * 60)
    print()

    # Step 1: Get Cloudflare cookies using cloudscraper
    cookie_dict, cookie_jar = get_cloudflare_cookies()

    # Step 2: Launch Playwright and inject cookies
    print("\nStep 2: Launching Playwright with cloudscraper cookies...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        )

        # Convert cloudscraper cookies to Playwright format
        playwright_cookies = []
        for cookie in cookie_jar:
            playwright_cookies.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires if cookie.expires else -1,
                'httpOnly': cookie.has_nonstandard_attr('HttpOnly') or False,
                'secure': cookie.secure or False,
                'sameSite': 'Lax'  # Default sameSite value
            })

        # Add cookies to context
        context.add_cookies(playwright_cookies)
        print(f"  ✓ Injected {len(playwright_cookies)} cookies into Playwright")

        page = context.new_page()

        try:
            # Step 3: Navigate to page (should bypass Cloudflare with cookies)
            print("\nStep 3: Navigating to Myki page with Cloudflare cookies...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded', timeout=30000)
            print("  ✓ Page loaded")

            # Wait for JavaScript to render
            print("\nStep 4: Waiting for page to render...")
            time.sleep(5)

            # Check for Cloudflare challenge
            print("\nStep 5: Checking for Cloudflare challenge...")
            try:
                cf_check = page.locator('text=Verifying').first
                if cf_check.is_visible(timeout=2000):
                    print("  ✗ Cloudflare challenge still present!")
                    return False
            except:
                pass

            print("  ✓ No Cloudflare challenge detected!")

            # Check for login form
            print("\nStep 6: Looking for login form...")
            try:
                username_field = page.locator('input[name="username"], input[type="text"]').first
                if username_field.is_visible(timeout=5000):
                    print("  ✓ Username field found and visible!")

                    password_field = page.locator('input[name="password"], input[type="password"]').first
                    if password_field.is_visible(timeout=2000):
                        print("  ✓ Password field found and visible!")

                        print("\n" + "=" * 60)
                        print("SUCCESS! HYBRID APPROACH WORKS!")
                        print("=" * 60)
                        print("\nCloudflare bypassed using cloudscraper cookies!")
                        print("Login form is accessible and ready for interaction!")

                        # Keep browser open for inspection
                        print("\nKeeping browser open for 30 seconds...")
                        time.sleep(30)

                        return True
                    else:
                        print("  ✗ Password field not found")
                else:
                    print("  ✗ Username field not found")

            except Exception as e:
                print(f"  ✗ Error finding form: {e}")

            # Take screenshot for debugging
            page.screenshot(path='screenshots/hybrid_result.png', full_page=True)
            print("\nScreenshot saved: screenshots/hybrid_result.png")

            # Keep browser open
            time.sleep(30)
            return False

        finally:
            context.close()
            browser.close()


if __name__ == '__main__':
    import sys
    success = test_hybrid_approach()
    sys.exit(0 if success else 1)
