import requests
from bs4 import BeautifulSoup
import os
import re
import time

# ========= ENV =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ========= SEARCH =========
URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&location=India&f_TPR=r600",
    "https://www.linkedin.com/jobs/search/?keywords=business%20analyst&location=India&f_TPR=r600"
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
    m = re.search(r"(\d+)\s+minute", text.lower())
    return int(m.group(1)) if m else None


def is_easy_apply(job_url):
    """
    REAL Easy Apply detection – opens job page
    """
    try:
        res = requests.get(job_url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")

        for span in soup.select("span.artdeco-button__text"):
            if "easy apply" in span.get_text(strip=True).lower():
                return True

        return False
    except:
        return False


# ========= MAIN =========
for url in URLS:
    print("\nFetching:", url)
    res = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    jobs = soup.select("div.base-card")
    print("Jobs found:", len(jobs))

    for job in jobs:
        title = job.select_one("h3")
        company = job.select_one("h4")
        time_el = job.select_one("time")
        link_el = job.select_one("a")

        if not title or not company or not time_el or not link_el:
            continue

        minutes = extract_minutes(time_el.text.strip())
        if minutes is None or minutes > 10:
            continue

        job_link = link_el["href"].split("?")[0]
        if not job_link.startswith("http"):
            job_link = "https://www.linkedin.com" + job_link

        # ⚠️ CRITICAL FIX HERE
        apply_type = "Easy Apply" if is_easy_apply(job_link) else "Standard Apply"

        message = (
            f"📋 Role: {title.text.strip()}\n\n"
            f"🏢 Company: {company.text.strip()}\n\n"
            f"⏰ Posted: {minutes} minutes ago\n"
            f"📝 Application: {apply_type}\n\n"
            f"🔗 Apply: {job_link}\n\n"
            f"— Shubham Ingole\n"
            f"🔗 LinkedIn: https://www.linkedin.com/in/shubhamingole/"
        )

        print("Sending:", title.text.strip(), "|", apply_type)
        send_telegram(message)

        time.sleep(1.5)  # anti-block
