"""
Ole Miss Baseball Live Data Scraper
Pulls latest headlines from The Rebel Walk RSS feed, filters for
BASEBALL-SPECIFIC roster-relevant keywords (transfer portal, draft,
commit, signing), and writes a structured JSON snapshot for the
dashboard to consume.
"""
import feedparser
import json
from datetime import datetime, timezone

FEEDS = {
    "Rebel Walk": "https://therebelwalk.com/feed/",
}

BASEBALL_TERMS = ["baseball", "diamond rebel", "diamond rebels", "bianco"]

ACTION_TERMS = [
    "transfer portal", "commit", "signs", "signing", "draft",
    "drafted", "withdraw", "return", "recruit"
]

EXCLUDE_TERMS = [
    "football", "basketball", "softball", "golf", "tennis",
    "track and field", "soccer", "volleyball"
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

def is_relevant(title):
    t = title.lower()
    if any(bad in t for bad in EXCLUDE_TERMS):
        return False
    has_baseball = any(term in t for term in BASEBALL_TERMS)
    has_action = any(term in t for term in ACTION_TERMS)
    return has_baseball and has_action

def fetch_feed(name, url):
    parsed = feedparser.parse(url)
    items = []
    for entry in parsed.entries:
        title = entry.get("title", "")
        if not is_relevant(title):
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
