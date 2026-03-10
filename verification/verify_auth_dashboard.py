from playwright.sync_api import sync_playwright, expect
import time
import re

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # 1. Open Landing Page
        print("Navigating to homepage...")
        page.goto("http://localhost:8000/")

        # Auth Modal should open automatically per Layout.tsx logic
        print("Waiting for Auth Modal...")
        try:
            page.wait_for_selector("text=Login / Ingia", timeout=5000)
            print("Auth Modal detected (auto-opened).")
        except:
            print("Auth Modal did not auto-open, clicking CTA...")
            page.get_by_role("link", name="Get My International Number").click()
            page.wait_for_selector("text=Login / Ingia")

        # Take screenshot of the Bilingual Auth Modal
        page.screenshot(path="verification/auth_modal_bilingual.png")
        print("Captured Auth Modal screenshot.")

        # 2. Register a test user
        print("Registering test user...")
        page.get_by_role("button", name="✨ Register / Jisajili").click()

        # Using locators that are more robust
        username_field = page.locator("input[placeholder='Your username']")
        password_field = page.locator("input[placeholder='••••••••']")

        test_username = f"testuser_{int(time.time())}"
        username_field.fill(test_username)
        password_field.fill("password123")

        # Check for tip text
        expect(page.get_by_text("📌 Kumbuka password yako")).to_be_visible()

        page.get_by_role("button", name="Jisajili / Register →").click()

        # Wait for success message
        page.wait_for_selector("text=Registration successful", timeout=10000)
        print("Registration successful.")

        # 3. Login
        print("Logging in...")
        page.get_by_role("button", name="🔑 Login / Ingia").click()
        username_field.fill(test_username)
        password_field.fill("password123")
        page.get_by_role("button", name="Ingia / Login →").click()

        # 4. Dashboard Verification
        print("Verifying Dashboard...")
        # Wait for redirect to /dashboard or /app
        page.wait_for_selector("text=User Dashboard", timeout=10000)

        # Take screenshot of empty Dashboard
        page.screenshot(path="verification/dashboard_empty.png")
        print("Captured Empty Dashboard screenshot.")

        # 5. Generate a number to see buttons (Simulation mode)
        # Click "Shop" in Nav or use the link in content
        try:
            page.get_by_role("link", name="Buy a new number →").click()
        except:
            page.get_by_role("link", name="Shop").first.click()

        print("In Shop/Catalog...")
        page.wait_for_selector("text=Pick an App")

        # Pick WhatsApp
        page.get_by_text("WhatsApp").first.click()
        # Pick Kenya
        page.wait_for_selector("text=Choose Country")
        page.get_by_text("Kenya").first.click()

        # Click Generate
        print("Generating number...")
        page.get_by_role("button", name="Generate Number Now").click()

        # Should redirect back to dashboard
        page.wait_for_selector("text=Current Active Numbers", timeout=10000)

        # Verify Cancel button existence
        expect(page.get_by_role("button", name="❌ Cancel")).to_be_visible()
        print("Cancel button is visible.")

        # Take screenshot of Dashboard with Active Order
        page.screenshot(path="verification/dashboard_active_order.png")
        print("Captured Dashboard with active order screenshot.")

        browser.close()
        print("Verification complete.")

if __name__ == "__main__":
    run()
