"""
Browser configuration with stealth settings for Cloudflare bypass.

This module provides browser launch configuration with anti-detection measures
including fingerprint randomization, realistic headers, and human-like behavior.
"""

import random
import time
from typing import Dict, Any, Tuple
from playwright.sync_api import Browser, BrowserContext, Page, Playwright
from playwright_stealth.stealth import Stealth


def get_viewport_size() -> Dict[str, int]:
    """
    Generate randomized viewport size to avoid fingerprinting.

    Returns:
        Dictionary with 'width' and 'height' keys for viewport dimensions.
    """
    base_width = 1920
    base_height = 1080
    width_variance = random.randint(-100, 100)
    height_variance = random.randint(-100, 100)

    return {
        'width': base_width + width_variance,
        'height': base_height + height_variance
    }


def get_user_agent() -> str:
    """
    Get a realistic Chrome user agent string for macOS.

    Returns:
        User agent string matching current Chrome version.
    """
    # Current Chrome user agent for macOS (update periodically)
    return (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/130.0.0.0 Safari/537.36'
    )


def get_extra_headers() -> Dict[str, str]:
    """
    Generate realistic browser headers to match real Chrome traffic.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        'Accept-Language': 'en-AU,en-US;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }


def launch_stealth_browser(playwright: Playwright) -> Tuple[Browser, BrowserContext]:
    """
    Launch Chromium browser with stealth configuration to bypass bot detection.

    Args:
        playwright: Playwright instance for browser automation.

    Returns:
        Tuple of (Browser, BrowserContext) with stealth settings applied.
    """
    viewport = get_viewport_size()
    user_agent = get_user_agent()

    # Launch browser in headed mode for debugging
    # Keep args minimal - some flags can trigger detection
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
        ],
        # Use persistent context with channel for more realistic browser
        channel='chrome'  # Use real Chrome instead of Chromium if available
    )

    # Create context with realistic fingerprint
    context = browser.new_context(
        viewport=viewport,
        user_agent=user_agent,
        locale='en-AU',
        timezone_id='Australia/Melbourne',
        extra_http_headers=get_extra_headers(),
        permissions=['geolocation'],
        geolocation={'latitude': -37.8136, 'longitude': 144.9631},  # Melbourne, Australia
        color_scheme='light',
        device_scale_factor=1,
        has_touch=False,
        is_mobile=False,
    )

    return browser, context


def apply_stealth_to_page(page: Page) -> None:
    """
    Apply stealth JavaScript patches to mask automation signals.

    Args:
        page: Playwright page to apply stealth settings to.
    """
    # Apply playwright-stealth with full configuration
    stealth = Stealth(
        navigator_languages=True,
        navigator_plugins=True,
        navigator_permissions=True,
        navigator_webdriver=True,
        navigator_vendor=True,
        webgl_vendor=True,
        chrome_runtime=True,
        iframe_content_window=True,
        media_codecs=True,
        navigator_hardware_concurrency=True,
        navigator_platform=True,
        navigator_user_agent=True,
    )
    stealth.apply_stealth_sync(page)

    # Additional stealth patches - comprehensive anti-detection
    page.add_init_script("""
        // Override the navigator.webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // Override automation detection
        delete Object.getPrototypeOf(navigator).webdriver;

        // Override the navigator.plugins to appear realistic
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}
            ]
        });

        // Override chrome detection with realistic properties
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };

        // Fix the language and languages arrays
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-AU', 'en-US', 'en']
        });

        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Hide automation-specific properties
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.call(this, parameter);
        };

        // Override battery API
        Object.defineProperty(navigator, 'getBattery', {
            get: () => undefined
        });

        // Add realistic connection info
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 100,
                downlink: 10,
                saveData: false
            })
        });

        // Override the Notification permission
        Object.defineProperty(Notification, 'permission', {
            get: () => 'default'
        });

        // Remove headless-specific detection points
        if (navigator.platform) {
            Object.defineProperty(navigator, 'platform', {
                get: () => 'MacIntel'
            });
        }

        // Override OuterHeight/Width check (headless detection)
        if (window.outerWidth === 0) {
            Object.defineProperty(window, 'outerWidth', {get: () => 1920});
        }
        if (window.outerHeight === 0) {
            Object.defineProperty(window, 'outerHeight', {get: () => 1080});
        }
    """)


def human_delay(min_ms: int = 800, max_ms: int = 2000) -> None:
    """
    Add random delay to simulate human-like behavior.

    Args:
        min_ms: Minimum delay in milliseconds (default: 800)
        max_ms: Maximum delay in milliseconds (default: 2000)
    """
    delay_seconds = random.randint(min_ms, max_ms) / 1000.0
    time.sleep(delay_seconds)


def human_type_delay() -> int:
    """
    Get random typing delay to simulate realistic keystrokes.

    Returns:
        Delay in milliseconds between keystrokes.
    """
    return random.randint(50, 150)


def simulate_mouse_movement(page: Page) -> None:
    """
    Simulate realistic mouse movement on the page.

    Args:
        page: Playwright page to perform mouse movements on.
    """
    # Move mouse in a smooth curve pattern
    viewport_size = page.viewport_size
    if viewport_size:
        width = viewport_size['width']
        height = viewport_size['height']

        # Random start and end points
        start_x = random.randint(100, width - 100)
        start_y = random.randint(100, height - 100)
        end_x = random.randint(100, width - 100)
        end_y = random.randint(100, height - 100)

        # Move in steps to create smooth movement
        steps = random.randint(10, 20)
        for i in range(steps):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            page.mouse.move(x, y)
            time.sleep(random.randint(10, 30) / 1000.0)


def simulate_page_scroll(page: Page) -> None:
    """
    Simulate realistic page scrolling behavior.

    Args:
        page: Playwright page to scroll.
    """
    # Scroll in random pattern
    scroll_distance = random.randint(100, 500)
    page.evaluate(f"window.scrollBy(0, {scroll_distance})")
    time.sleep(random.randint(300, 800) / 1000.0)

    # Scroll back up slightly
    scroll_back = random.randint(50, 200)
    page.evaluate(f"window.scrollBy(0, -{scroll_back})")
