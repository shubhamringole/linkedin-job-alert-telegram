import requests
from bs4 import BeautifulSoup
import os
import re

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r600",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India&f_TPR=r600"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": str(CHAT_ID),
        "text": msg[:3900],
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload)
    print("Telegram:", r.status_code)

def extract_minutes(text):
    """Extract minutes from 'X minutes ago'"""
    match = re.search(r"(\d+)\s+minute", text)
    if match:
        return int(match.group(1))
    return None

for url in URLS:
    print("\nFetching:", url)
    response = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = soup.select("div.base-card")
    print("Jobs found:", len(jobs))

    for job in jobs:
        title = job.select_one("h3")
        company = job.select_one("h4")
        location = job.select_one(".job-search-card__location")
        time_tag = job.select_one("time")
        link = job.select_one("a")

        if not title or not company or not link or not time_tag:
            continue

        posted_text = time_tag.text.strip().lower()
        minutes = extract_minutes(posted_text)

        # ONLY last 10 minutes
        if minutes is None or minutes > 10:
            continue

        job_link = link["href"].split("?")[0]

        message = (
            f"📋 Role: {title.text.strip()}\n\n"
            f"🏢 Company: {company.text.strip()}\n"
            f"📍 Location: {location.text.strip() if location else 'India'}\n\n"
            f"⏰ Posted: {minutes} minutes ago\n"
            f"📝 Application: Standard Apply\n\n"
            f"🔗 Apply: {job_link}"
            f"— Shubham Ingole"
            f"🔗 LinkedIn: https://www.linkedin.com/in/shubham-ingole"
        )

        print("Sending:", title.text.strip())
        send_telegram(message)
