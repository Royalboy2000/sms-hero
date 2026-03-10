from playwright.sync_api import sync_playwright
import time
import re

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        page.goto("http://localhost:8000/")

        # 1. Capture Auth Modal (auto-opens)
        page.wait_for_selector("text=Login / Ingia")
        page.screenshot(path="verification/auth_modal_bilingual.png")
        print("Captured Auth Modal screenshot.")

        # 2. Login with the user created in previous failed run or register anew
        test_user = f"final_test_{int(time.time())}"
        page.get_by_role("button", name="✨ Register / Jisajili").click()
        page.locator("input[placeholder='Your username']").fill(test_user)
        page.locator("input[placeholder='••••••••']").fill("password123")
        page.get_by_role("button", name="Jisajili / Register →").click()

        page.wait_for_selector("text=Registration successful", timeout=10000)
        page.get_by_role("button", name="🔑 Login / Ingia").click()
        page.locator("input[placeholder='Your username']").fill(test_user)
        page.locator("input[placeholder='••••••••']").fill("password123")
        page.get_by_role("button", name="Ingia / Login →").click()

        # 3. Wait for Dashboard or go there
        page.wait_for_url("**/dashboard", timeout=10000)
        page.wait_for_selector("text=User Dashboard")
        print("At Dashboard.")

        # 4. Generate order
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
        page.reload()
        page.wait_for_selector("text=❌ Cancel", timeout=10000)

        # 5. Take screenshots
        page.screenshot(path="verification/dashboard_final.png", full_page=True)
        print("Captured Dashboard Final screenshot.")

        browser.close()

if __name__ == "__main__":
    run()
