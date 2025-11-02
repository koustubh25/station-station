"""Advanced Cloudflare bypass using Chrome DevTools Protocol (CDP)."""

import sys
import time
from playwright.sync_api import sync_playwright
from cloudflare_bypass import detect_cloudflare_challenge, is_login_form_accessible

def test_with_cdp():
    """Test using CDP for maximum stealth."""
    with sync_playwright() as p:
        # Launch with remote debugging
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
            ],
            channel='chrome'  # Use real Chrome if available
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        )

        page = context.new_page()

        # Use CDP to add scripts at the earliest possible moment
        cdp = page.context.new_cdp_session(page)

        # Enable Page domain
        cdp.send('Page.enable')

        # Add script to evaluate on new document (earliest injection point)
        cdp.send('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // Ultra-aggressive stealth patches via CDP
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete Object.getPrototypeOf(navigator).webdriver;

                // Override all automation signals
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name: 'Native Client', filename: 'internal-nacl-plugin'}
                    ]
                });

                Object.defineProperty(navigator, 'languages', {get: () => ['en-AU', 'en-US', 'en']});

                // Chrome object
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {},
                    webstore: {}
                };

                // WebGL masking
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.call(this, parameter);
                };

                // Connection API
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({effectiveType: '4g', rtt: 50, downlink: 10, saveData: false})
                });

                // Battery API - remove
                delete navigator.getBattery;

                // Permissions
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = (parameters) =>
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: 'default'}) :
                        originalQuery(parameters);

                // Platform
                Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'});

                // Fix window dimensions for headless detection
                if (window.outerWidth === 0) {
                    Object.defineProperty(window, 'outerWidth', {get: () => 1920});
                }
                if (window.outerHeight === 0) {
                    Object.defineProperty(window, 'outerHeight', {get: () => 1080});
                }

                // Notification permission
                Object.defineProperty(Notification, 'permission', {get: () => 'default'});

                console.log('[STEALTH] All patches applied via CDP');
            '''
        })

        try:
            print("=" * 60)
            print("TESTING WITH CDP INJECTION")
            print("=" * 60)

            print("\n1. Navigating to Myki (with early CDP scripts)...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded', timeout=30000)
            print("   ✓ Page loaded")

            print("\n2. Waiting 10 seconds...")
            time.sleep(10)

            print("\n3. Checking for Cloudflare...")
            has_cloudflare = detect_cloudflare_challenge(page)
            print(f"   Cloudflare detected: {has_cloudflare}")

            if has_cloudflare:
                print("\n4. Waiting for Cloudflare (max 60s)...")
                start = time.time()
                while time.time() - start < 60:
                    time.sleep(3)
                    if not detect_cloudflare_challenge(page):
                        print(f"   ✓ Cleared after {time.time() - start:.1f}s!")
                        break
                    print(f"   Waiting... ({time.time() - start:.1f}s)")
                else:
                    print("   ✗ Still blocked")

            print("\n5. Checking form...")
            form_ok = is_login_form_accessible(page)
            print(f"   Form accessible: {form_ok}")

            if form_ok:
                print("\n" + "=" * 60)
                print("SUCCESS WITH CDP!")
                print("=" * 60)
                time.sleep(30)
                return True
            else:
                print("\n" + "=" * 60)
                print("FAILED")
                print("=" * 60)
                page.screenshot(path='screenshots/cdp_failed.png', full_page=True)
                time.sleep(30)
                return False

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    success = test_with_cdp()
    sys.exit(0 if success else 1)
