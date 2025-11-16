import os
import time
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# === ENV VARIABLES ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
URL = os.getenv("URL", "https://investinglive.com/live-feed/")
REFRESH_RATE = int(os.getenv("REFRESH_RATE", 10))

translator = Translator()
sent_posts = set()  # runtime memory to avoid duplicates

def send_to_telegram(text):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(api_url, data=data)

def scrape_posts():
    html = requests.get(URL, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    # Select each post container
    posts = soup.select(".entry-content")  # adjust if site structure changes

    results = []
    for post in posts:
        # Get the title (usually bold)
        title_elem = post.select_one("strong")
        if not title_elem:
            continue
        title = title_elem.get_text(strip=True)

        # Get the first sentence/paragraph under the title
        p_elem = post.find("p")
        snippet = p_elem.get_text(strip=True) if p_elem else ""

        combined = f"{title}\n\n{snippet}"
        results.append((combined, None))  # link not needed
    return results

def main():
    print("Bot is running on Railway...")

    while True:
        try:
            posts = scrape_posts()
            for combined_text, _ in posts:  # we ignore the link
                if combined_text not in sent_posts:
                    # Translate title + first sentence together
                    arabic = translator.translate(combined_text, dest="ar").text

                    msg = f"🔔 *خبر جديد*\n\n{arabic}"
                    send_to_telegram(msg)

                    print("Posted:", combined_text)
                    sent_posts.add(combined_text)

        except Exception as e:
            print("❌ ERROR:", e)

        time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    main()
