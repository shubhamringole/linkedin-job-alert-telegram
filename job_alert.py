import requests
from bs4 import BeautifulSoup
import os
import re

# ===== ENV VARIABLES =====
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ===== LINKEDIN SEARCH (LAST 10 MINUTES) =====
URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r600",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India&f_TPR=r600"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

# ===== HELPERS =====
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": str(CHAT_ID),
        "text": message[:3900],  # Telegram safety limit
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    print("Telegram:", response.status_code)


def clean_text(text: str) -> str:
    """Remove asterisks and extra whitespace"""
    if not text:
        return ""
    return (
        text.replace("*", "")
            .replace("\n", " ")
            .strip()
    )


def extract_minutes(posted_text: str):
    """Extract minutes from 'X minutes ago'"""
    match = re.search(r"(\d+)\s+minute", posted_text.lower())
    if match:
        return int(match.group(1))
    return None


# ===== MAIN LOGIC =====
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

        posted_text = time_tag.text.strip()
        minutes = extract_minutes(posted_text)

        # ONLY jobs posted in last 10 minutes
        if minutes is None or minutes > 10:
            continue

        job_link = link["href"].split("?")[0].strip()

        message = (
            f"📋 Role: {clean_text(title.text)}\n\n"
            f"🏢 Company: {clean_text(company.text)}\n"
            f"📍 Location: {clean_text(location.text if location else 'India')}\n\n"
            f"⏰ Posted: {minutes} minutes ago\n"
            f"📝 Application: Standard Apply\n\n"
            f"🔗 Apply: {job_link}\n\n"
            f"— Shubham Ingole\n"
            f"🔗 LinkedIn: https://www.linkedin.com/in/shubham-ingole"
        )

        print("Sending:", clean_text(title.text))
        send_telegram(message)
