import requests
from bs4 import BeautifulSoup
import os
import re
import time

# ========= ENV =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ========= CONFIG =========
MAX_MINUTES = 60          # 1 hour window (realistic)
MAX_JOBS_PER_URL = 10     # increase safely
JOB_DELAY = 3             # seconds between jobs
URL_DELAY = 8             # seconds between URLs

# ========= SEARCH (GUEST API) =========
BASE_URLS = [
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=data%20analyst&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=data%20scientist&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=data%20engineer&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=business%20analyst&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=product%20analyst&location=India&f_TPR=r86400",
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
    text = text.lower()

    if "just now" in text:
        return 0

    if "hour" in text:
        match = re.search(r"(\d+)\s+hour", text)
        return int(match.group(1)) * 60 if match else 60

    if "minute" in text:
        match = re.search(r"(\d+)\s+minute", text)
        return int(match.group(1)) if match else None

    return None

# ========= MAIN =========
for base_url in BASE_URLS:

    # Pagination (0,25,50,75)
    for start in range(0, 100, 25):
        url = f"{base_url}&start={start}"

        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
        except Exception as e:
            print("Request failed:", e)
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        jobs = soup.select("li")[:MAX_JOBS_PER_URL]

        for job in jobs:
            try:
                title_el = job.select_one("h3")
                company_el = job.select_one("h4")
                location_el = job.select_one(".job-search-card__location")
                time_el = job.select_one("time")
                link_el = job.select_one("a")

                if not title_el or not company_el or not time_el or not link_el:
                    continue

                time_text = time_el.text.strip()
                minutes = extract_minutes(time_text)

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
                    f"⏰ Posted: {time_text}\n"
                    f"📝 Application: Check on LinkedIn\n\n"
                    f"🔗 Apply: {job_link}\n\n"
                    f"— Shubham Ingole\n"
                    f"🔗 LinkedIn: https://www.linkedin.com/in/shubhamingole/"
                )

                send_telegram(message)

                time.sleep(JOB_DELAY)

            except Exception as e:
                print("Job parse error:", e)
                continue

        time.sleep(URL_DELAY)
