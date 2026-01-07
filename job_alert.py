import requests
from bs4 import BeautifulSoup
import os
import re

# ========= ENV =========
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ========= SEARCH (LAST 10 MINUTES) =========
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
    r = requests.post(url, json=payload, timeout=20)
    print("Telegram:", r.status_code)


# ========= HELPERS =========
def clean(text):
    if not text:
        return ""
    return (
        text.replace("*", "")
        .replace("\n", " ")
        .replace("\u2022", "")
        .strip()
    )


def get_text(el):
    if not el:
        return ""
    if el.text and el.text.strip():
        return clean(el.text)
    if el.get("aria-label"):
        return clean(el.get("aria-label"))
    if el.get("title"):
        return clean(el.get("title"))
    return ""


def extract_minutes(text):
    match = re.search(r"(\d+)\s+minute", text.lower())
    if match:
        return int(match.group(1))
    return None


# ========= APPLY TYPE DETECTION =========
def get_apply_type(job_card):
    """
    Accurate Easy Apply detection for LinkedIn public jobs page
    """

    # 1️⃣ Easy Apply button text (PRIMARY)
    for span in job_card.select("span.artdeco-button__text"):
        if "easy apply" in span.get_text(strip=True).lower():
            return "Easy Apply"

    # 2️⃣ Legacy Easy Apply label
    if job_card.select_one("span.job-search-card__easy-apply-label"):
        return "Easy Apply"

    # 3️⃣ aria-label / title fallback
    for tag in job_card.find_all(["a", "button"]):
        aria = (tag.get("aria-label") or "").lower()
        title = (tag.get("title") or "").lower()
        if "easy apply" in aria or "easy apply" in title:
            return "Easy Apply"

    return "Standard Apply"


# ========= MAIN =========
for url in URLS:
    print("\nFetching:", url)
    res = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    jobs = soup.select("div.base-card")
    print("Jobs found:", len(jobs))

    for job in jobs:
        title_el = job.select_one("h3")
        company_el = job.select_one("h4")
        location_el = job.select_one(".job-search-card__location")
        time_el = job.select_one("time")
        link_el = job.select_one("a")

        title = get_text(title_el)
        company = get_text(company_el)
        location = get_text(location_el) or "India"

        if not title or not company or not link_el or not time_el:
            continue

        minutes = extract_minutes(time_el.text.strip())
        if minutes is None or minutes > 10:
            continue

        job_link = link_el.get("href", "").split("?")[0].strip()
        if not job_link.startswith("http"):
            job_link = "https://www.linkedin.com" + job_link

        apply_type = get_apply_type(job)

        message = (
            f"📋 Role: {title}\n\n"
            f"🏢 Company: {company}\n"
            f"📍 Location: {location}\n\n"
            f"⏰ Posted: {minutes} minutes ago\n"
            f"📝 Application: {apply_type}\n\n"
            f"🔗 Apply: {job_link}\n\n"
            f"— Shubham Ingole\n"
            f"🔗 LinkedIn: https://www.linkedin.com/in/shubhamingole/"
        )

        print("Sending:", title, "|", apply_type)
        send_telegram(message)
