from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import re

app = FastAPI()

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
        page.goto("https://www.chronogolf.com/en/club/18821/widget?medium=widget&source=club")
        page.wait_for_timeout(3000)

        try:
            date_button = page.query_selector(f'[data-date="{date}"]')
            if date_button:
                date_button.click()
                page.wait_for_timeout(2000)
        except:
            return {"results": [], "error": "Date selection failed"}

        tee_time_elements = page.query_selector_all(".available-times .time-slot")

        results = []
        for el in tee_time_elements:
            try:
                time_text = el.query_selector(".hour").inner_text().strip()
                price_text = el.query_selector(".price").inner_text().strip()
                players = "1-4"
                price_clean = re.sub(r"[^\d]", "", price_text)
                results.append({
                    "time": time_text,
                    "price": price_clean,
                    "players": players,
                })
            except:
                continue

        browser.close()
        return {"results": results}
