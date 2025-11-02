"""Ultra-human behavior simulation to bypass Cloudflare."""

import random
import time
from playwright.sync_api import sync_playwright

def random_mouse_movements(page, count=10):
    """Move mouse randomly like a human would."""
    viewport = page.viewport_size
    width, height = viewport['width'], viewport['height']

    for _ in range(count):
        # Random destination
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)

        # Move in small steps for smooth movement
        current_pos = page.evaluate("() => ({x: window.mouseX || 0, y: window.mouseY || 0})")
        start_x = current_pos.get('x', width // 2)
        start_y = current_pos.get('y', height // 2)

        steps = random.randint(20, 40)
        for i in range(steps):
            progress = i / steps
            curr_x = start_x + (x - start_x) * progress
            curr_y = start_y + (y - start_y) * progress

            # Add slight random jitter
            jitter_x = random.uniform(-5, 5)
            jitter_y = random.uniform(-5, 5)

            page.mouse.move(curr_x + jitter_x, curr_y + jitter_y)
            time.sleep(random.uniform(0.002, 0.01))

        # Store position
        page.evaluate(f"window.mouseX = {x}; window.mouseY = {y}")

        # Sometimes pause
        if random.random() < 0.3:
            time.sleep(random.uniform(0.1, 0.5))

def random_scrolling(page, count=5):
    """Scroll randomly like a human reading."""
    for _ in range(count):
        # Scroll down
        scroll_amount = random.randint(100, 400)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(random.uniform(0.3, 0.8))

        # Sometimes scroll back up a bit
        if random.random() < 0.4:
            scroll_back = random.randint(50, 150)
            page.evaluate(f"window.scrollBy(0, -{scroll_back})")
            time.sleep(random.uniform(0.2, 0.5))

def random_keystrokes(page):
    """Type some random keys like a human might."""
    # Common keys people might press while browsing
    keys = ['ArrowDown', 'ArrowUp', 'PageDown', 'Tab', 'Escape']

    for _ in range(random.randint(2, 5)):
        key = random.choice(keys)
        page.keyboard.press(key)
        time.sleep(random.uniform(0.1, 0.4))

def human_pause():
    """Pause like a human would."""
    time.sleep(random.uniform(1.5, 4.0))

def test_ultra_human_behavior():
    """Test Cloudflare bypass with ultra-realistic human behavior."""
    print("=" * 60)
    print("ULTRA-HUMAN BEHAVIOR SIMULATION")
    print("=" * 60)

    with sync_playwright() as p:
        # Launch browser with minimal flags
        browser = p.chromium.launch(
            headless=False,
            channel='chrome',  # Use real Chrome
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )

        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-AU',
            timezone_id='Australia/Melbourne',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        )

        page = context.new_page()

        # Inject stealth scripts
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            delete Object.getPrototypeOf(navigator).webdriver;

            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin'},
                    {name: 'Chrome PDF Viewer'},
                    {name: 'Native Client'}
                ]
            });
        """)

        try:
            print("\n1. Navigating to page...")
            page.goto('https://transport.vic.gov.au/manage-myki', wait_until='domcontentloaded')
            print("   ✓ Page loaded")

            print("\n2. Simulating human behavior before Cloudflare...")

            # Initial pause - human reads page
            print("   - Human pause (reading)...")
            time.sleep(random.uniform(2, 4))

            # Mouse movements
            print("   - Random mouse movements...")
            random_mouse_movements(page, count=15)

            # Scroll a bit
            print("   - Scrolling...")
            random_scrolling(page, count=3)

            # More mouse movement
            print("   - More mouse movements...")
            random_mouse_movements(page, count=10)

            # Random keys
            print("   - Random keystrokes...")
            random_keystrokes(page)

            # Long human pause
            print("   - Long human pause...")
            human_pause()

            # Check for Cloudflare
            print("\n3. Checking for Cloudflare (60s wait)...")
            start = time.time()
            max_wait = 60

            while time.time() - start < max_wait:
                # Check if Cloudflare present
                try:
                    cf_present = page.locator('text=Verifying').first.is_visible(timeout=1000)
                except:
                    cf_present = False

                if cf_present:
                    elapsed = time.time() - start
                    print(f"   Cloudflare still verifying... ({elapsed:.1f}s)")

                    # More human behavior while waiting
                    if random.random() < 0.5:
                        random_mouse_movements(page, count=5)

                    time.sleep(2)
                else:
                    # Cloudflare gone - check for form
                    print(f"   ✓ Cloudflare cleared after {time.time() - start:.1f}s!")
                    break

            # Check for login form
            print("\n4. Checking for login form...")
            time.sleep(3)  # Let JavaScript render

            try:
                username = page.locator('input[name="username"], input[type="text"], input[placeholder*="username" i]').first
                if username.is_visible(timeout=5000):
                    print("   ✓ Username field found!")

                    password = page.locator('input[name="password"], input[type="password"], input[placeholder*="password" i]').first
                    if password.is_visible(timeout=2000):
                        print("   ✓ Password field found!")

                        print("\n" + "=" * 60)
                        print("SUCCESS! ULTRA-HUMAN BEHAVIOR WORKED!")
                        print("=" * 60)

                        # Keep browser open
                        print("\nKeeping browser open for 30 seconds...")
                        time.sleep(30)
                        return True

            except Exception as e:
                print(f"   ✗ Form not found: {e}")

            # Take screenshot
            page.screenshot(path='screenshots/ultra_human_result.png', full_page=True)
            print("\nScreenshot saved")

            # Keep browser open
            print("\nKeeping browser open for 30 seconds...")
            time.sleep(30)

            return False

        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    import sys
    success = test_ultra_human_behavior()
    sys.exit(0 if success else 1)
