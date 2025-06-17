from playwright.sync_api import sync_playwright, Playwright
from rich import print
import json 

def scrape_quotes(playwright):
    start_url = "https://www.aldi.us/products"
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(start_url)

    while True:
        links = page.locator('a.base-link.product-tile__link').element_handles()
        for link in links:
            p = browser.new_page(base_url="https://www.aldi.us/product")
            url = link.get_attribute("href")
            
            if url is not None:
                p.goto(url)
            else:
                p.close()

            scripts = p.locator("script[type='application/ld+json']").element_handles()
            for script in scripts:
                data = script.text_content()
                try:
                    json_data = json.loads(data)
                    if isinstance(json_data, dict) and "name" in json_data:
                        print(json_data)
                    else:
                        print("[yellow]No 'name' found in JSON data[/yellow]")
                except Exception as e:
                    print(f"[red]Error parsing JSON: {e}[/red]")
                
            p.close()

        # Select the next page button by data-test attribute
        next_button = page.locator('a[data-test="next-page"]')
        if next_button.count() == 0 or not next_button.is_enabled():
            break  # No next page, exit loop

        with page.expect_navigation():
            next_button.click()

    browser.close()

with sync_playwright() as playwright:
    scrape_quotes(playwright)