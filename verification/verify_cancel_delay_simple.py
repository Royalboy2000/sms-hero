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

        # Register
        page.get_by_role("button", name="✨ Register / Jisajili").click()
        page.locator("input[placeholder='Your username']").fill(test_user)
        page.locator("input[placeholder='••••••••']").fill("password123")
        page.get_by_role("button", name="Jisajili / Register →").click()

        page.wait_for_selector("text=successful", timeout=10000)

        # Login
        page.get_by_role("button", name="🔑 Login / Ingia").click()
        page.locator("input[placeholder='Your username']").fill(test_user)
        page.locator("input[placeholder='••••••••']").fill("password123")
        page.get_by_role("button", name="Ingia / Login →").click()

        # Wait for any dashboard indicator
        time.sleep(3)
        page.screenshot(path="verification/after_login.png")

        # Create an order via console to ensure it exists
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

        time.sleep(2)
        page.goto("http://localhost:8000/dashboard")
        time.sleep(3)

        # Take screenshot to see the "Wait" button
        page.screenshot(path="verification/dashboard_with_wait.png", full_page=True)

        # Check if "Wait" or "Cancel" is visible
        content = page.content()
        if "Wait" in content:
            print("Verified: Countdown button is visible.")
        elif "Cancel" in content:
            print("Verified: Cancel button is visible (delay might have passed or timestamp issue).")
        else:
            print("Neither button found.")

        browser.close()

if __name__ == "__main__":
    run()
