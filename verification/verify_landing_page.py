from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to localhost:3000
        page.goto("http://localhost:3000/")

        # Wait for some content to ensure load
        page.wait_for_selector("h1")

        # Verify Headline
        expect(page.get_by_role("heading", name="Open a US WhatsApp Account")).to_be_visible()

        # Verify CTA
        expect(page.get_by_role("link", name="Get My International Number")).to_be_visible()

        # Verify Pill text
        expect(page.get_by_text("Proudly Kenyan • Based in Mombasa")).to_be_visible()

        # Verify Visual Proof text
        expect(page.get_by_text("Your verification code is:")).to_be_visible()
        expect(page.get_by_text("123-456")).to_be_visible()

        # Take full page screenshot
        page.screenshot(path="verification/landing_page.png", full_page=True)

        # Take viewport screenshot to focus on Hero
        page.screenshot(path="verification/landing_page_hero.png")

        print("Verification successful!")
        browser.close()

if __name__ == "__main__":
    run()
