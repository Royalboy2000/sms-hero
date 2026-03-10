from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        page.goto("http://localhost:8000/")

        # 1. Login
        page.wait_for_selector("text=Login / Ingia")
        test_user = f"v3_user_{int(time.time())}"

        # Register first
        page.get_by_role("button", name="✨ Register / Jisajili").click()
        page.locator("input[placeholder='Your username']").fill(test_user)
        page.locator("input[placeholder='••••••••']").fill("password123")
        page.get_by_role("button", name="Jisajili / Register →").click()

        page.wait_for_selector("text=Registration successful", timeout=10000)

        # Login
        page.get_by_role("button", name="🔑 Login / Ingia").click()
        page.locator("input[placeholder='Your username']").fill(test_user)
        page.locator("input[placeholder='••••••••']").fill("password123")
        page.get_by_role("button", name="Ingia / Login →").click()

        # 2. Go to dashboard
        page.goto("http://localhost:8000/dashboard")
        page.wait_for_selector("text=User Dashboard")
        print("Logged in and at dashboard.")

        # 3. Create an order via API
        page.evaluate("""
            async () => {
                const token = localStorage.getItem('smskenya_token');
                await fetch('/api/generate-number', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                    body: JSON.stringify({ service_id: 'wa', country_id: 'KE' })
                });
            }
        """)

        time.sleep(1)
        page.reload()

        # 4. Wait for the "Wait Xs" button (2-minute delay)
        page.wait_for_selector("text=Wait", timeout=5000)
        print("Detected countdown button.")

        page.screenshot(path="verification/cancel_delay_countdown.png", full_page=True)
        print("Captured countdown screenshot.")

        browser.close()

if __name__ == "__main__":
    run()
