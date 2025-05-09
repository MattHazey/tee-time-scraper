from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import re

app = FastAPI()

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape-tee-times")
def scrape_tee_times(date: str = Query(..., description="Format: YYYY-MM-DD")):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Load Chronogolf iframe page
        page.goto("https://www.chronogolf.com/en/club/18821/widget?medium=widget&source=club")
        page.wait_for_selector("iframe")

        # Switch to the iframe
        iframe_element = page.query_selector("iframe")
        iframe = iframe_element.content_frame()

        print("✅ Iframe loaded")

        # Click date button
        try:
            date_button = iframe.query_selector(f'[data-date="{date}"]')
            if date_button:
                date_button.click()
                iframe.wait_for_timeout(2000)
            else:
                return {"results": [], "error": "Date button not found"}
        except:
            return {"results": [], "error": "Date selection failed"}

        # Scrape tee time slots
        tee_time_elements = iframe.query_selector_all(".available-times .time-slot")
        results = []

        for el in tee_time_elements:
            try:
                time_el = el.query_selector(".hour")
                price_el = el.query_selector(".price")

                time = time_el.inner_text().strip()
                price = price_el.inner_text().strip()
                price_clean = re.sub(r"[^\d]", "", price)

                results.append({
                    "time": time,
                    "price": price_clean,
                    "players": "1-4"
                })
            except:
                continue

        return {"results": results}
