from playwright.sync_api import sync_playwright, expect
import time
import os

def verify_quota_zero(page):
    # Register a new user
    username = f"testuser_{int(time.time())}"
    password = "password123"

    page.goto("http://localhost:8000")

    # Auth Modal opens automatically for unauthenticated users
    # Wait for the Register tab button
    page.wait_for_selector("text=Register / Jisajili", timeout=10000)

    # Switch to Register
    page.click("text=Register / Jisajili")

    # Fill form
    page.fill("input[placeholder='Your username']", username)
    page.fill("input[placeholder='••••••••']", password)

    # Submit registration
    page.click("button:has-text('Jisajili / Register →')")

    # Wait for success message
    page.wait_for_selector("text=Registration successful! Please login.", timeout=10000)

    # Modal should have switched to Login automatically or we click it
    # Based on server.py logic: setError('Registration successful! Please login.'); setIsLogin(true);
    # So we should be in Login mode now.

    # Login
    page.fill("input[placeholder='Your username']", username)
    page.fill("input[placeholder='••••••••']", password)
    page.click("button:has-text('Ingia / Login →')")

    # Wait for AuthModal to close (it closes on login)
    # Check if we are on /dashboard or can navigate there
    page.wait_for_timeout(2000) # Wait for state update
    page.goto("http://localhost:8000/dashboard")

    # Verify Quota Left: 0
    # In Dashboard.tsx: <p className="text-2xl font-mono font-bold text-emerald-500">{(quota?.allowed || 0) - (quota?.used || 0)}</p>
    quota_left_element = page.locator("p.text-emerald-500")
    expect(quota_left_element).to_have_text("0", timeout=10000)

    page.screenshot(path="/home/jules/verification/quota_zero_verified.png")
    print(f"Successfully verified quota is 0 for new user {username}")

if __name__ == "__main__":
    # Ensure server is running
    os.system("pkill -f 'python server.py 8000'")
    time.sleep(1)
    os.system("PORT=8000 python server.py 8000 > server_verify.log 2>&1 &")
    time.sleep(3)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_quota_zero(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="/home/jules/verification/failure_v3.png")
        finally:
            browser.close()
            os.system("pkill -f 'python server.py 8000'")
