"""Test using cloudscraper to bypass Cloudflare."""

import cloudscraper
from bs4 import BeautifulSoup

def test_cloudscraper():
    """Test if cloudscraper can bypass Cloudflare on the Myki site."""
    print("=" * 60)
    print("TESTING WITH CLOUDSCRAPER")
    print("=" * 60)

    # Create scraper instance
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'desktop': True
        }
    )

    try:
        print("\n1. Attempting to access Myki login page with cloudscraper...")
        url = 'https://transport.vic.gov.au/manage-myki'

        response = scraper.get(url, timeout=30)

        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.text)} bytes")

        # Check if we got past Cloudflare
        if 'cloudflare' in response.text.lower() and 'verifying' in response.text.lower():
            print("   ✗ Still blocked by Cloudflare")
            print("\n" + "=" * 60)
            print("FAILED - Cloudflare still blocking")
            print("=" * 60)
            return False

        # Check for login form elements
        if 'username' in response.text.lower() and 'password' in response.text.lower():
            print("   ✓ Login form detected!")

            # Parse and check for specific elements
            soup = BeautifulSoup(response.text, 'html.parser')
            username_field = soup.find('input', {'name': 'username'}) or soup.find('input', {'type': 'text'})
            password_field = soup.find('input', {'name': 'password'}) or soup.find('input', {'type': 'password'})

            if username_field and password_field:
                print(f"   ✓ Username field found: {username_field.get('name', 'unknown')}")
                print(f"   ✓ Password field found: {password_field.get('name', 'unknown')}")

                # Get cookies
                cookies = scraper.cookies.get_dict()
                print(f"\n2. Cookies received ({len(cookies)} total):")
                for name, value in cookies.items():
                    print(f"   - {name}: {value[:20]}...")

                print("\n" + "=" * 60)
                print("SUCCESS WITH CLOUDSCRAPER!")
                print("=" * 60)
                print("\nCloudscraper successfully bypassed Cloudflare!")
                print("We can now proceed with authentication using requests library.")
                return True
            else:
                print("   ✗ Login form fields not found")
        else:
            print("   ✗ No login form detected")
            print(f"\n   Response preview (first 500 chars):\n{response.text[:500]}")

        print("\n" + "=" * 60)
        print("PARTIAL SUCCESS - Got response but no login form")
        print("=" * 60)
        return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\n" + "=" * 60)
        print("FAILED WITH ERROR")
        print("=" * 60)
        return False

if __name__ == '__main__':
    # Install beautifulsoup4 if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        import subprocess
        print("Installing beautifulsoup4...")
        subprocess.run(['pip', 'install', 'beautifulsoup4'], check=True)
        from bs4 import BeautifulSoup

    import sys
    success = test_cloudscraper()
    sys.exit(0 if success else 1)
