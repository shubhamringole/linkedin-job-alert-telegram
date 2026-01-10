import requests
from bs4 import BeautifulSoup
import os
import re
import time

# ========= ENV =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ========= CONFIG =========
MAX_MINUTES = 30
MAX_JOBS_PER_URL = 3      # 🔴 LIMIT aggressively
JOB_DELAY = 2             # seconds between jobs
URL_DELAY = 5             # seconds between URLs

# ========= SEARCH =========
URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r1800",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India&f_TPR=r1800",
    "https://www.linkedin.com/jobs/search/?keywords=data%20engineer&location=India&f_TPR=r1800"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

# ========= TELEGRAM =========
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": str(CHAT_ID),
        "text": message[:3900],
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=20)

# ========= HELPERS =========
def extract_minutes(text):
    match = re.search(r"(\d+)\s+minute", text.lower())
    return int(match.group(1)) if match else None

# ========= MAIN =========
for url in URLS:
    res = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    # 🔴 Only take first N jobs
    jobs = soup.select("div.base-card")[:MAX_JOBS_PER_URL]

    for job in jobs:
        title_el = job.select_one("h3")
        company_el = job.select_one("h4")
        location_el = job.select_one(".job-search-card__location")
        time_el = job.select_one("time")
        link_el = job.select_one("a")

        if not title_el or not company_el or not time_el or not link_el:
            continue

        minutes = extract_minutes(time_el.text.strip())
        if minutes is None or minutes > MAX_MINUTES:
            continue

        job_link = link_el.get("href", "").split("?")[0]
        if not job_link.startswith("http"):
            job_link = "https://www.linkedin.com" + job_link

        title = title_el.text.strip()
        company = company_el.text.strip()
        location = location_el.text.strip() if location_el else "India"

        message = (
            f"📋 Role: {title}\n\n"
            f"🏢 Company: {company}\n"
            f"📍 Location: {location}\n\n"
            f"⏰ Posted: {minutes} minutes ago\n"
            f"📝 Application: Check on LinkedIn\n\n"
            f"🔗 Apply: {job_link}\n\n"
            f"— Shubham Ingole\n"
            f"🔗 LinkedIn: https://www.linkedin.com/in/shubhamingole/"
        )

        send_telegram(message)

        # 🕒 Slow down per job
        time.sleep(JOB_DELAY)

    # 🕒 Slow down per URL
    time.sleep(URL_DELAY)
