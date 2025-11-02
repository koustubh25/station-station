"""Capture the authentication response to get the authorization Bearer token.

This script performs authentication and captures the response from the /authenticate endpoint.
"""

import os
import time
import random
import json
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from profile_manager import ProfileManager


def capture_auth_response():
    """Capture authentication response containing Bearer token."""

    load_dotenv()
    username = os.getenv("MYKI_USERNAME")
    password = os.getenv("MYKI_PASSWORD")

    if not username or not password:
        raise ValueError("MYKI_USERNAME and MYKI_PASSWORD must be set")

    profile_manager = ProfileManager()
    auth_response_data = {}

    print("=" * 60)
    print("CAPTURING AUTHENTICATION RESPONSE")
    print("=" * 60)

    try:
        # Copy Chrome profile
        print("\n1. Copying Chrome profile...")
        profile_dir = profile_manager.copy_profile()

        with sync_playwright() as p:
            # Launch browser
            print("\n2. Launching browser...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1920, 'height': 1080},
            )
            page = context.pages[0] if context.pages else context.new_page()

            # Capture authentication response
            def handle_response(response):
                if '/authenticate' in response.url and response.request.method == 'POST':
                    print(f"\n→ Captured authenticate response: {response.url}")
                    print(f"   Status: {response.status}")

                    try:
                        # Get response body
                        body = response.text()
                        auth_response_data['url'] = response.url
                        auth_response_data['status'] = response.status
                        auth_response_data['headers'] = dict(response.headers)
                        auth_response_data['body'] = body

                        # Try to parse as JSON
                        try:
                            json_body = json.loads(body)
                            auth_response_data['json'] = json_body
                            print(f"   Response body (JSON):")
                            print(json.dumps(json_body, indent=4))
                        except:
                            print(f"   Response body (text): {body}")

                    except Exception as e:
                        print(f"   Error reading response: {e}")

            page.on('response', handle_response)

            try:
                # Navigate to Myki
                print("\n3. Navigating to Myki portal...")
                page.goto("https://transport.vic.gov.au/manage-myki", wait_until='domcontentloaded')

                # Wait for Cloudflare
                print("\n4. Waiting for Cloudflare...")
                time.sleep(35)

                # Fill and submit login
                print("\n5. Logging in...")
                time.sleep(3)

                username_field = page.locator('input[name="username"], input[type="text"]').first
                username_field.click()
                time.sleep(0.5)
                username_field.type(username, delay=100)

                password_field = page.locator('input[name="password"], input[type="password"]').first
                password_field.click()
                time.sleep(0.5)
                password_field.type(password, delay=100)

                time.sleep(2)

                login_button = page.locator('button.login-form__button[type="submit"]').first
                login_button.click(timeout=10000)

                # Wait for response
                print("\n6. Waiting for authentication response...")
                time.sleep(10)

                # Save the response
                if auth_response_data:
                    print("\n7. Saving authentication response...")

                    auth_data_dir = Path('auth_data')
                    auth_data_dir.mkdir(exist_ok=True)

                    response_file = auth_data_dir / 'auth_response.json'
                    with open(response_file, 'w') as f:
                        json.dump(auth_response_data, f, indent=2)
                    print(f"   ✓ Response saved to: {response_file}")

                    # Extract Bearer token if present in response
                    if 'json' in auth_response_data:
                        json_response = auth_response_data['json']
                        # Look for common token field names
                        token_fields = ['token', 'access_token', 'accessToken', 'bearer_token', 'bearerToken', 'authToken']
                        for field in token_fields:
                            if field in json_response:
                                print(f"\n   ✓ Found token in field '{field}':")
                                print(f"     {json_response[field][:50]}...")
                                break

                    print("\n" + "=" * 60)
                    print("AUTHENTICATION RESPONSE CAPTURED")
                    print("=" * 60)
                else:
                    print("\n   ✗ No authentication response captured")

                # Keep browser open
                print("\nKeeping browser open for 10 seconds...")
                time.sleep(10)

            finally:
                context.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        profile_manager.cleanup()

    return auth_response_data


if __name__ == '__main__':
    capture_auth_response()
