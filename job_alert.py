import requests
from bs4 import BeautifulSoup
import os
import hashlib

BOT_TOKEN = os.environ["8449183300:AAECtDfPgKPRVtW9ABSW3yFltmCA6eV22Z0"]
CHAT_ID = os.environ["4811275809"]

URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India&f_TPR=r86400"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

sent_jobs = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

for url in URLS:
    response = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = soup.select("div.base-card")

    for job in jobs[:5]:  # limit to avoid spam
        title = job.select_one("h3")
        company = job.select_one("h4")
        location = job.select_one(".job-search-card__location")
        link = job.select_one("a")

        if not title or not company or not link:
            continue

        job_text = title.text.strip() + company.text.strip()
        job_hash = hashlib.md5(job_text.encode()).hexdigest()

        if job_hash in sent_jobs:
            continue

        sent_jobs.add(job_hash)

        message = (
            f"📊 {title.text.strip()}\n\n"
            f"🏢 {company.text.strip()}\n"
            f"📍 {location.text.strip() if location else 'India'}\n\n"
            f"🔗 Apply: {link['href']}"
        )

        send_telegram(message)

