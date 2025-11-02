"""Check for Cloudflare Turnstile widget on the Myki login page."""

import time
from playwright.sync_api import sync_playwright
from profile_manager import ProfileManager


def check_for_turnstile():
    """Check for Cloudflare Turnstile elements on login page."""
    profile_mgr = ProfileManager()

    try:
        profile_dir = profile_mgr.copy_profile()
        print(f"Profile ready: {profile_dir}\n")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1920, 'height': 1080},
            )

            page = context.pages[0] if context.pages else context.new_page()

            print("Navigating to Myki...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')

            print("Waiting for page to load...")
            time.sleep(15)

            print("\n" + "=" * 60)
            print("CHECKING FOR CLOUDFLARE TURNSTILE ELEMENTS")
            print("=" * 60)

            # Check for Turnstile iframes
            print("\n1. Checking for Turnstile iframes...")
            iframes = page.query_selector_all('iframe')
            print(f"   Found {len(iframes)} iframes total")

            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute('src')
                    title = iframe.get_attribute('title')
                    id_attr = iframe.get_attribute('id')
                    print(f"   iframe {i+1}:")
                    print(f"     - src: {src}")
                    print(f"     - title: {title}")
                    print(f"     - id: {id_attr}")

                    if src and 'turnstile' in src.lower():
                        print(f"     *** TURNSTILE IFRAME FOUND ***")
                except Exception as e:
                    print(f"     Error reading iframe: {e}")

            # Check for Turnstile divs
            print("\n2. Checking for Turnstile div containers...")
            turnstile_divs = page.query_selector_all('[class*="turnstile"], [id*="turnstile"], [class*="cf-"], [id*="cf-"]')
            print(f"   Found {len(turnstile_divs)} potential Cloudflare elements")

            for i, div in enumerate(turnstile_divs[:5]):  # Show first 5
                try:
                    class_name = div.get_attribute('class')
                    id_attr = div.get_attribute('id')
                    print(f"   Element {i+1}:")
                    print(f"     - class: {class_name}")
                    print(f"     - id: {id_attr}")
                except Exception as e:
                    print(f"     Error: {e}")

            # Check page HTML for Turnstile references
            print("\n3. Checking page HTML for 'turnstile' references...")
            html = page.content()
            if 'turnstile' in html.lower():
                print("   ✓ 'turnstile' found in page HTML")
                # Count occurrences
                count = html.lower().count('turnstile')
                print(f"   Found {count} occurrences")
            else:
                print("   No 'turnstile' found in HTML")

            # Check for Cloudflare challenge scripts
            print("\n4. Checking for Cloudflare scripts...")
            scripts = page.query_selector_all('script[src*="cloudflare"], script[src*="challenges"]')
            print(f"   Found {len(scripts)} Cloudflare-related scripts")

            for i, script in enumerate(scripts[:5]):
                src = script.get_attribute('src')
                print(f"   Script {i+1}: {src}")

            # Get all script sources
            print("\n5. All external scripts:")
            all_scripts = page.query_selector_all('script[src]')
            for i, script in enumerate(all_scripts):
                src = script.get_attribute('src')
                if 'cloudflare' in src.lower() or 'turnstile' in src.lower() or 'challenge' in src.lower():
                    print(f"   *** {src}")

            print("\n" + "=" * 60)
            print("Keeping browser open for 30 seconds for inspection...")
            print("=" * 60)
            time.sleep(30)

            context.close()

    finally:
        profile_mgr.cleanup()


if __name__ == '__main__':
    check_for_turnstile()
