import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    })
    print("Telegram response:", r.status_code)

for url in URLS:
    print("\nFetching:", url)
    response = requests.get(url, headers=HEADERS, timeout=30)
    print("Status code:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = soup.select("div.base-card")
    print("Jobs found:", len(jobs))

    for job in jobs[:3]:
        title = job.select_one("h3")
        company = job.select_one("h4")
        link = job.select_one("a")

        if not title or not company or not link:
            print("Skipping incomplete job")
            continue

        message = (
            f"📊 {title.text.strip()}\n"
            f"🏢 {company.text.strip()}\n"
            f"🔗 {link['href']}"
        )

        print("Sending job:", title.text.strip())
        send_telegram(message)
