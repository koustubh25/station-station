"""Discover Myki API endpoints by monitoring network traffic after authentication.

This script logs in and monitors all network requests to identify actual API endpoints.
"""

import os
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Route
from profile_manager import ProfileManager


class APIEndpointDiscovery:
    """Discovers API endpoints by monitoring network traffic."""

    MYKI_URL = "https://transport.vic.gov.au/manage-myki"

    def __init__(self):
        """Initialize endpoint discovery."""
        load_dotenv()
        self.username = os.getenv("MYKI_USERNAME")
        self.password = os.getenv("MYKI_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "MYKI_USERNAME and MYKI_PASSWORD must be set in .env file"
            )

        self.profile_manager = ProfileManager()
        self.api_requests = []
        self.xhr_requests = []

    def capture_request(self, request):
        """Capture and log network request.

        Args:
            request: Playwright Request object
        """
        url = request.url
        method = request.method

        # Filter for API requests (mykiapi domain)
        if 'mykiapi' in url:
            request_info = {
                'url': url,
                'method': method,
                'headers': dict(request.headers),
                'resource_type': request.resource_type,
                'post_data': request.post_data if method in ['POST', 'PUT'] else None
            }
            self.api_requests.append(request_info)
            print(f"\n→ API Request captured: {method} {url}")

        # Also capture XHR/Fetch requests
        elif request.resource_type in ['xhr', 'fetch']:
            request_info = {
                'url': url,
                'method': method,
                'headers': dict(request.headers),
                'resource_type': request.resource_type,
                'post_data': request.post_data if method in ['POST', 'PUT'] else None
            }
            self.xhr_requests.append(request_info)
            print(f"\n→ XHR Request captured: {method} {url}")

    def capture_response(self, response):
        """Capture and log network response.

        Args:
            response: Playwright Response object
        """
        url = response.url

        # Log API responses
        if 'mykiapi' in url:
            status = response.status
            print(f"← API Response: {status} for {url}")

            # Try to get response body
            try:
                if status < 400:
                    # Only try to read body for successful responses
                    body = response.text()
                    print(f"   Response preview: {body[:200]}...")
            except Exception as e:
                print(f"   Could not read response body: {e}")

    def discover_endpoints(self):
        """Discover API endpoints by navigating and interacting with the site.

        Returns:
            List of discovered API endpoint requests
        """
        print("=" * 60)
        print("DISCOVERING MYKI API ENDPOINTS")
        print("=" * 60)

        try:
            # Copy Chrome profile
            print("\n1. Copying Chrome profile...")
            profile_dir = self.profile_manager.copy_profile()

            with sync_playwright() as p:
                # Launch browser with profile
                print("\n2. Launching browser...")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=False,
                    channel='chrome',
                    args=['--disable-blink-features=AutomationControlled'],
                    viewport={'width': 1920, 'height': 1080},
                )
                page = context.pages[0] if context.pages else context.new_page()

                # Set up network monitoring
                print("\n3. Setting up network monitoring...")
                page.on('request', self.capture_request)
                page.on('response', self.capture_response)
                print("  ✓ Network monitoring active")

                try:
                    # Navigate to Myki
                    print("\n4. Navigating to Myki portal...")
                    page.goto(self.MYKI_URL, wait_until='domcontentloaded')

                    # Wait for Cloudflare
                    print("\n5. Waiting for Cloudflare...")
                    time.sleep(35)

                    # Fill login form
                    print("\n6. Logging in...")
                    time.sleep(3)

                    username_field = page.locator(
                        'input[name="username"], input[type="text"]'
                    ).first
                    username_field.click()
                    time.sleep(0.5)
                    username_field.type(self.username, delay=100)

                    password_field = page.locator(
                        'input[name="password"], input[type="password"]'
                    ).first
                    password_field.click()
                    time.sleep(0.5)
                    password_field.type(self.password, delay=100)

                    time.sleep(2)

                    login_button = page.locator(
                        'button.login-form__button[type="submit"]'
                    ).first
                    login_button.click(timeout=10000)

                    # Wait for dashboard and API calls
                    print("\n7. Waiting for dashboard and API calls...")
                    time.sleep(10)

                    print("\n8. Interacting with dashboard to trigger more API calls...")

                    # Try to click on different tabs/sections to trigger API calls
                    try:
                        # Look for myki tabs
                        tabs = page.locator('button.myki-tabs__tab-item')
                        count = tabs.count()
                        print(f"  Found {count} tabs to click")

                        for i in range(min(count, 5)):  # Click first 5 tabs
                            try:
                                tab = tabs.nth(i)
                                tab_text = tab.text_content()
                                print(f"\n  → Clicking tab: {tab_text}")
                                tab.click()
                                time.sleep(3)  # Wait for API calls
                            except Exception as e:
                                print(f"  ✗ Could not click tab {i}: {e}")

                    except Exception as e:
                        print(f"  ✗ Could not find/click tabs: {e}")

                    # Try to find and click card items
                    try:
                        cards = page.locator('.myki-card, .card-item, [class*="card"]')
                        card_count = cards.count()
                        print(f"\n  Found {card_count} potential card elements")

                        for i in range(min(card_count, 3)):  # Click first 3 cards
                            try:
                                card = cards.nth(i)
                                print(f"  → Clicking card {i}")
                                card.click()
                                time.sleep(3)  # Wait for API calls
                            except Exception as e:
                                print(f"  ✗ Could not click card {i}: {e}")

                    except Exception as e:
                        print(f"  ✗ Could not find/click cards: {e}")

                    # Wait a bit more for any delayed API calls
                    print("\n9. Waiting for additional API calls...")
                    time.sleep(5)

                    # Save results
                    print("\n10. Saving discovered endpoints...")
                    self.save_endpoints()

                    # Display summary
                    print("\n" + "=" * 60)
                    print("ENDPOINT DISCOVERY COMPLETE")
                    print("=" * 60)
                    print(f"\nDiscovered {len(self.api_requests)} API requests")
                    print(f"Discovered {len(self.xhr_requests)} XHR/Fetch requests")

                    if self.api_requests:
                        print("\nAPI Endpoints found:")
                        unique_endpoints = set()
                        for req in self.api_requests:
                            endpoint = f"{req['method']} {req['url']}"
                            if endpoint not in unique_endpoints:
                                unique_endpoints.add(endpoint)
                                print(f"  • {endpoint}")

                    # Keep browser open for inspection
                    print("\n\nKeeping browser open for 30 seconds for inspection...")
                    print("Check the saved files in api_discovery/ for details")
                    time.sleep(30)

                finally:
                    context.close()

            return self.api_requests

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return []

        finally:
            self.profile_manager.cleanup()

    def save_endpoints(self):
        """Save discovered endpoints to files."""
        # Create directory
        discovery_dir = Path('api_discovery')
        discovery_dir.mkdir(exist_ok=True)

        # Save API requests
        if self.api_requests:
            api_file = discovery_dir / 'api_requests.json'
            with open(api_file, 'w') as f:
                json.dump(self.api_requests, f, indent=2)
            print(f"  ✓ API requests saved to: {api_file}")

        # Save XHR requests
        if self.xhr_requests:
            xhr_file = discovery_dir / 'xhr_requests.json'
            with open(xhr_file, 'w') as f:
                json.dump(self.xhr_requests, f, indent=2)
            print(f"  ✓ XHR requests saved to: {xhr_file}")

        # Save summary
        summary = {
            'total_api_requests': len(self.api_requests),
            'total_xhr_requests': len(self.xhr_requests),
            'unique_api_endpoints': list(set([
                f"{req['method']} {req['url']}" for req in self.api_requests
            ])),
            'unique_xhr_endpoints': list(set([
                f"{req['method']} {req['url']}" for req in self.xhr_requests
            ]))
        }
        summary_file = discovery_dir / 'summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  ✓ Summary saved to: {summary_file}")


def main():
    """Main entry point."""
    try:
        discovery = APIEndpointDiscovery()
        endpoints = discovery.discover_endpoints()
        return 0 if endpoints else 1

    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
