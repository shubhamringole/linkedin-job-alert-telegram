import os
import re
import time
import requests
from playwright.sync_api import sync_playwright

# ========= ENV =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ========= SEARCH URLS =========
SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r600",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India&f_TPR=r600"
]

# ========= TELEGRAM =========
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message[:3900],
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=20)


# ========= HELPERS =========
def extract_minutes(text):
    match = re.search(r"(\d+)\s+minute", text.lower())
    return int(match.group(1)) if match else None


def is_easy_apply(page):
    """
    REAL Easy Apply detection (DOM-level)
    """
    buttons = page.locator("span.artdeco-button__text")
    for i in range(buttons.count()):
        if "easy apply" in buttons.nth(i).inner_text().lower():
            return True
    return False


# ========= MAIN =========
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    for search_url in SEARCH_URLS:
        print("\nFetching search:", search_url)
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)

        jobs = page.locator("div.base-card")
        job_count = jobs.count()
        print("Jobs found:", job_count)

        for i in range(job_count):
            job = jobs.nth(i)

            try:
                title = job.locator("h3").inner_text().strip()
                company = job.locator("h4").inner_text().strip()
                time_text = job.locator("time").inner_text().strip()
                link = job.locator("a").get_attribute("href")

                minutes = extract_minutes(time_text)
                if minutes is None or minutes > 10:
                    continue

                if not link.startswith("http"):
                    link = "https://www.linkedin.com" + link.split("?")[0]

                # 🔥 OPEN JOB DETAIL PAGE
                job_page = context.new_page()
                job_page.goto(link, timeout=60000)
                job_page.wait_for_timeout(5000)

                apply_type = "Easy Apply" if is_easy_apply(job_page) else "Standard Apply"

                message = (
                    f"📋 Role: {title}\n\n"
                    f"🏢 Company: {company}\n\n"
                    f"⏰ Posted: {minutes} minutes ago\n"
                    f"📝 Application: {apply_type}\n\n"
                    f"🔗 Apply: {link}\n\n"
                    f"— Shubham Ingole\n"
                    f"🔗 LinkedIn: https://www.linkedin.com/in/shubhamingole/"
                )

                print("Sending:", title, "|", apply_type)
                send_telegram(message)

                job_page.close()
                time.sleep(2)  # anti-block

            except Exception as e:
                print("Skipped job due to error:", e)
                continue

    browser.close()
