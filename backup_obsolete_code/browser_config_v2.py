"""
Alternative browser configuration using persistent context for better stealth.

This version uses a persistent browser profile to appear more like a real user.
"""

import random
import time
from typing import Tuple
from pathlib import Path
from playwright.sync_api import BrowserContext, Page, Playwright


def get_user_data_dir() -> str:
    """Get path to persistent user data directory."""
    user_data_path = Path(__file__).parent.parent / 'browser_profile'
    user_data_path.mkdir(exist_ok=True)
    return str(user_data_path)


def launch_persistent_browser(playwright: Playwright) -> Tuple[BrowserContext, Page]:
    """
    Launch browser with persistent context for maximum realism.

    Args:
        playwright: Playwright instance.

    Returns:
        Tuple of (BrowserContext, Page) with persistent profile.
    """
    user_data_dir = get_user_data_dir()

    # Use persistent context with real Chrome if available
    try:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel='chrome',  # Use real Chrome
            args=[
                '--disable-blink-features=AutomationControlled',
            ],
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
            permissions=['geolocation'],
            geolocation={'latitude': -37.8136, 'longitude': 144.9631},
        )
    except Exception:
        # Fallback to Chromium if Chrome not available
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
            ],
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
            permissions=['geolocation'],
            geolocation={'latitude': -37.8136, 'longitude': 144.9631},
        )

    # Get or create page
    if len(context.pages) > 0:
        page = context.pages[0]
    else:
        page = context.new_page()

    # Apply stealth patches
    apply_stealth_patches(page)

    return context, page


def apply_stealth_patches(page: Page) -> None:
    """
    Apply comprehensive stealth JavaScript patches.

    Args:
        page: Playwright page to patch.
    """
    page.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Remove automation flags
        delete Object.getPrototypeOf(navigator).webdriver;

        // Fix plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', filename: 'internal-nacl-plugin'}
            ]
        });

        // Fix languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-AU', 'en-US', 'en']
        });

        // Add chrome object
        if (!window.chrome) {
            window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};
        }

        // Fix permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
        );

        // Hide automation in error stack traces
        Error.stackTraceLimit = 10;
    """)


def warm_up_browser(page: Page) -> None:
    """
    Warm up the browser by visiting a few pages first.

    This builds browsing history and makes the session look more natural.

    Args:
        page: Playwright page to warm up.
    """
    warmup_sites = [
        'https://www.google.com.au',
        'https://www.vic.gov.au',
    ]

    for site in warmup_sites:
        try:
            print(f"Warming up: visiting {site}")
            page.goto(site, wait_until='domcontentloaded', timeout=10000)
            time.sleep(random.uniform(2, 4))

            # Scroll a bit
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(random.uniform(1, 2))

        except Exception as e:
            print(f"Warmup site {site} failed (continuing anyway): {e}")

    print("Browser warmup complete")
