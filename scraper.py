"""
Ole Miss Baseball Live Data Scraper
Pulls latest headlines from The Rebel Walk RSS feed, filters for
roster-relevant keywords (transfer portal, draft, commit, signing),
and writes a structured JSON snapshot for the dashboard to consume.
"""
import feedparser
import json
import re
from datetime import datetime, timezone

FEEDS = {
    "Rebel Walk": "https://therebelwalk.com/feed/",
}

KEYWORDS = [
    "transfer portal", "commit", "signs", "signing", "draft",
    "drafted", "withdraw", "return", "baseball", "recruit"
]

STATUS_MAP = {
    "drafted": "leaving",
    "withdraw": "return",
    "return": "return",
    "commit": "pending",
    "signs": "pending",
}

def classify(title):
    t = title.lower()
    for key, status in STATUS_MAP.items():
        if key in t:
            return status
    return "news"

def fetch_feed(name, url):
    parsed = feedparser.parse(url)
    items = []
    for entry in parsed.entries:
        title = entry.get("title", "")
        if not any(k in title.lower() for k in KEYWORDS):
            continue
        items.append({
            "source": name,
            "title": title,
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "status_guess": classify(title)
        })
    return items

def main():
    all_items = []
    for name, url in FEEDS.items():
        try:
            all_items.extend(fetch_feed(name, url))
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)

    output = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "item_count": len(all_items),
        "items": all_items
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(all_items)} items to data.json")

if __name__ == "__main__":
    main()