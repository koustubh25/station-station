"""Test cloudscraper and save the HTML response for inspection."""

import cloudscraper
from pathlib import Path

def test_and_save_html():
    """Test cloudscraper and save the HTML for inspection."""
    print("=" * 60)
    print("TESTING CLOUDSCRAPER - SAVING HTML")
    print("=" * 60)

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'desktop': True
        }
    )

    try:
        print("\n1. Accessing Myki page with cloudscraper...")
        url = 'https://transport.vic.gov.au/manage-myki'
        response = scraper.get(url, timeout=30)

        print(f"   Status: {response.status_code}")
        print(f"   Length: {len(response.text)} bytes")

        # Save HTML to file
        html_file = Path('screenshots/cloudscraper_response.html')
        html_file.parent.mkdir(exist_ok=True)
        html_file.write_text(response.text)
        print(f"   ✓ HTML saved to: {html_file}")

        # Save cookies
        cookies = scraper.cookies.get_dict()
        print(f"\n2. Cookies ({len(cookies)} total):")
        for name, value in cookies.items():
            print(f"   - {name}: {value[:40]}...")

        # Check response headers
        print(f"\n3. Response headers:")
        for header, value in response.headers.items():
            print(f"   - {header}: {value}")

        # Search for key indicators
        html_lower = response.text.lower()
        print(f"\n4. Content analysis:")
        print(f"   - Contains 'cloudflare': {('cloudflare' in html_lower)}")
        print(f"   - Contains 'verifying': {('verifying' in html_lower)}")
        print(f"   - Contains 'username': {('username' in html_lower)}")
        print(f"   - Contains 'password': {('password' in html_lower)}")
        print(f"   - Contains 'turnstile': {('turnstile' in html_lower)}")
        print(f"   - Contains 'myki': {('myki' in html_lower)}")

        # Print first 2000 characters
        print(f"\n5. HTML Preview (first 2000 chars):")
        print("-" * 60)
        print(response.text[:2000])
        print("-" * 60)

        if response.status_code == 200 and 'cloudflare' not in html_lower or 'verifying' not in html_lower:
            print("\n" + "=" * 60)
            print("SUCCESS! Cloudflare bypassed with cloudscraper!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("Got response but may still have Cloudflare challenge")
            print("=" * 60)
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = test_and_save_html()
    sys.exit(0 if success else 1)
