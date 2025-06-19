from playwright.sync_api import sync_playwright, TimeoutError
from rich import print
import json

def scrape_products(playwright):
    start_url = "https://www.dollargeneral.com/c/food-beverage?sort=0&q="
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    visited_urls = set()

    try:
        page.goto(start_url)
        
        while True:
            try:
                page.wait_for_selector("div#container-c0f2807a64 a.product-card__navigation", timeout=10000)
            except TimeoutError:
                print("[red]No product links found[/red]")
                break

            links = page.locator("div#container-c0f2807a64 a.product-card__navigation").element_handles()
            for link in links:
                url = link.get_attribute("href")
                if url is None or url in visited_urls:
                    continue
                visited_urls.add(url)

                p = browser.new_page(base_url="https://www.dollargeneral.com")
                p.goto(url, wait_until="domcontentloaded")

                data_div = p.locator("div#product-detail-json-response")
                data_attr = data_div.get_attribute("data-product-detail-json-response")

                if data_attr:
                    try:
                        json_data = json.loads(data_attr)
                        print(json_data)
                    except Exception as e:
                        print(f"[red]Error parsing JSON: {e}[/red]")
                else:
                    print(f"[yellow]No data attribute found at {url}[/yellow]")
                p.close()

            load_more = page.locator('button.view-more-button')
            if load_more.count() > 0 and load_more.is_enabled():
                load_more.click()
                try:
                    page.wait_for_selector("div#container-c0f2807a64 a.product-card__navigation", timeout=10000)
                except TimeoutError:
                    print("[yellow]New products did not load after clicking Load More[/yellow]")
                    break
            else:
                print("[green]No more pages to load[/green]")
                break
    finally:
        browser.close()

with sync_playwright() as playwright:
    scrape_products(playwright)
