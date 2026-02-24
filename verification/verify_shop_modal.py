from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to localhost:3000
        page.goto("http://localhost:3000/")

        # Wait for some content to ensure load
        page.wait_for_selector("nav")

        # 1. Verify "Shop" link in Navigation
        shop_link = page.get_by_role("link", name="Shop")
        expect(shop_link.first).to_be_visible()

        # 2. Click "Shop" to open modal
        shop_link.first.click()

        # 3. Verify Modal Title and simplified text (Step 1)
        expect(page.get_by_role("heading", name="Pick an App")).to_be_visible()
        expect(page.get_by_text("Which app do you want to open?")).to_be_visible()
        expect(page.get_by_placeholder("Type app name (WhatsApp, etc)...")).to_be_visible()

        # 4. Select WhatsApp to go to Step 2
        page.get_by_role("button", name="WhatsApp").click()

        # 5. Verify Step 2 simplified text
        expect(page.get_by_role("heading", name="Get Code for WhatsApp")).to_be_visible()
        expect(page.get_by_text("Which country do you want?")).to_be_visible()
        expect(page.get_by_role("heading", name="Choose Country")).to_be_visible()
        expect(page.get_by_placeholder("Search country...")).to_be_visible()

        # 6. Select a country (e.g., United States)
        page.get_by_role("button", name="United States").click()

        # 7. Verify Order Button and Price text
        expect(page.get_by_text("Price to Pay")).to_be_visible()
        expect(page.get_by_role("button", name="Send Order to WhatsApp")).to_be_visible()

        # Take screenshot of the modal
        page.screenshot(path="verification/shop_modal.png")

        print("Modal verification successful!")
        browser.close()

if __name__ == "__main__":
    run()
