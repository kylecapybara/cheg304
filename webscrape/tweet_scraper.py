import asyncio
from playwright.async_api import async_playwright, TimeoutError

async def scrape_all_tweet_links(handle: str) -> list[str]:
    url = f"https://x.com/{handle}"
    links = []

    async with async_playwright() as pw:
        print("Launching browser...")
        browser = await pw.chromium.launch(headless=False)  # Set headless=False to see the browser
        context = await browser.new_context()
        page = await context.new_page()
        print(f"Navigating to {url}...")
        await page.goto(url)
        
        try:
            print("Waiting for tweets to load...")
            await page.wait_for_selector("article[data-testid='tweet']", timeout=60000)  # Increased timeout to 60 seconds
        except TimeoutError:
            print("Timeout while waiting for tweets to load.")
            await browser.close()
            return links

        last_count = 0
        while True:
            tweet_elements = page.locator("article[data-testid='tweet']")
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)
            count = await tweet_elements.count()
            print(f"Found {count} tweets...")
            if count == last_count:
                break
            last_count = count

        for i in range(last_count):
            element = tweet_elements.nth(i).locator("a[href*='/status/']")
            href = await element.get_attribute("href")
            if href and href.startswith(f"/{handle}/status/"):
                links.append(f"https://x.com{href}")

        await browser.close()

    return links

if __name__ == "__main__":
    handle_to_scrape = "MarkBlenner"
    result = asyncio.run(scrape_all_tweet_links(handle_to_scrape))
    print(result)
