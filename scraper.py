"""
Ole Miss Dashboard Scraper
Outputs data.json with ALL keys the dashboard expects:
  baseball[], football[], oxford[],
  football_schedule[], season_results_2026[],
  recruiting_fb[], portal_bsb[], oxford_events[]
"""
import feedparser
import json
from datetime import datetime, timezone

# ── RSS Feed sources ──────────────────────────────────────────────────────────
FEEDS = {
    "HottyToddy": "https://www.hottytoddy.com/feed/",
    "Rebel Walk":  "https://therebelwalk.com/feed/",
}

# ── Keyword classifiers ───────────────────────────────────────────────────────
BASEBALL_TERMS   = ["baseball", "diamond rebel", "bianco", "swayze"]
FOOTBALL_TERMS   = ["football", "golding", "rebel offense", "lacy", "egg bowl",
                    "sec media", "kickoff", "quarterback", "offensive line"]
OXFORD_TERMS     = ["oxford", "square", "grove", "ole miss campus",
                    "lafayette", "dining", "restaurant"]

EXCLUDE_BASEBALL = ["football", "basketball", "softball", "golf", "tennis",
                    "soccer", "volleyball", "track"]
EXCLUDE_FOOTBALL = ["baseball", "basketball", "softball", "golf", "tennis",
                    "soccer", "volleyball", "track"]

STATUS_MAP = {
    "drafted": "leaving", "draft": "leaving",
    "withdraw": "return",  "return": "return",
    "commit": "pending",   "signs": "pending",
    "transfer": "pending", "portal": "pending",
}

CAT_MAP = {
    "recruit": "Recruiting", "commit": "Recruiting", "signing": "Recruiting",
    "portal": "Portal",     "transfer": "Portal",
    "draft": "NFL Draft",   "nfl": "NFL Draft",
    "rank": "Rankings",     "ranking": "Rankings",
    "roster": "Roster",     "schedule": "Schedule",
    "preview": "Analysis",  "analysis": "Analysis",
    "dining": "Dining",     "restaurant": "Dining",
}

def classify_status(title):
    t = title.lower()
    for kw, st in STATUS_MAP.items():
        if kw in t:
            return st
    return "news"

def classify_category(title):
    t = title.lower()
    for kw, cat in CAT_MAP.items():
        if kw in t:
            return cat
    return "News"

def entry_to_item(entry, source, extra=None):
    item = {
        "source":       source,
        "title":        entry.get("title", ""),
        "link":         entry.get("link", ""),
        "published":    entry.get("published", datetime.now(timezone.utc).isoformat()),
        "status_guess": classify_status(entry.get("title", "")),
        "category":     classify_category(entry.get("title", "")),
    }
    if extra:
        item.update(extra)
    return item

def is_baseball(title):
    t = title.lower()
    if any(bad in t for bad in EXCLUDE_BASEBALL):
        return False
    return any(term in t for term in BASEBALL_TERMS)

def is_football(title):
    t = title.lower()
    if any(bad in t for bad in EXCLUDE_FOOTBALL):
        return False
    return any(term in t for term in FOOTBALL_TERMS)

def is_oxford(title):
    t = title.lower()
    return any(term in t for term in OXFORD_TERMS)

def dedupe(items):
    seen, unique = set(), []
    for item in items:
        key = item["title"].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

# ── Static structured data (seeded; updated manually or via future scraper) ───

FOOTBALL_SCHEDULE = [
    {"date":"Sep 6",  "opponent":"Louisville",      "location":"at","venue":"Papa John's Cardinal Stadium","time":"TBD",  "tv":"TBD",        "notes":"Season opener"},
    {"date":"Sep 12", "opponent":"Charlotte",       "location":"vs","venue":"Vaught-Hemingway",           "time":"6:45 PM","tv":"ESPN+",      "notes":"Home opener"},
    {"date":"Sep 19", "opponent":"LSU",             "location":"vs","venue":"Vaught-Hemingway",           "time":"6:30 PM","tv":"ESPN",       "notes":"SEC opener"},
    {"date":"Sep 27", "opponent":"Kentucky",        "location":"at","venue":"Kroger Field",               "time":"TBD",  "tv":"TBD",        "notes":"SEC road"},
    {"date":"Oct 4",  "opponent":"South Carolina",  "location":"at","venue":"Williams-Brice",             "time":"TBD",  "tv":"TBD",        "notes":"SEC road"},
    {"date":"Oct 17", "opponent":"Missouri",        "location":"vs","venue":"Vaught-Hemingway",           "time":"2:30 PM","tv":"SEC Network","notes":"Homecoming"},
    {"date":"Oct 25", "opponent":"Arkansas",        "location":"at","venue":"Donald W. Reynolds",         "time":"TBD",  "tv":"TBD",        "notes":"SEC road"},
    {"date":"Oct 31", "opponent":"Auburn",          "location":"vs","venue":"Vaught-Hemingway",           "time":"11:00 AM","tv":"ESPN/ABC",  "notes":"Halloween game"},
    {"date":"Nov 7",  "opponent":"Georgia",         "location":"vs","venue":"Vaught-Hemingway",           "time":"TBD",  "tv":"Flex",       "notes":"Top-5 matchup"},
    {"date":"Nov 15", "opponent":"Texas A&M",       "location":"at","venue":"Kyle Field",                 "time":"TBD",  "tv":"TBD",        "notes":"SEC road"},
    {"date":"Nov 21", "opponent":"Wofford",         "location":"vs","venue":"Vaught-Hemingway",           "time":"11:00 AM","tv":"SEC Network","notes":"Senior Day"},
    {"date":"Nov 27", "opponent":"Mississippi State","location":"vs","venue":"Vaught-Hemingway",           "time":"11:00 AM","tv":"ESPN",       "notes":"Egg Bowl — Rivalry"},
]

SEASON_RESULTS_2026 = [
    {"date":"Feb 14","opponent":"Austin Peay",       "location":"Home","result":"W","score":"10-2"},
    {"date":"Feb 15","opponent":"Austin Peay",       "location":"Home","result":"W","score":"7-1"},
    {"date":"Feb 16","opponent":"Austin Peay",       "location":"Home","result":"W","score":"12-3"},
    {"date":"Feb 21","opponent":"Lipscomb",          "location":"Home","result":"W","score":"8-0"},
    {"date":"Feb 22","opponent":"Lipscomb",          "location":"Home","result":"W","score":"5-2"},
    {"date":"Feb 23","opponent":"Lipscomb",          "location":"Home","result":"L","score":"3-4"},
    {"date":"Mar 7", "opponent":"@ Vanderbilt",      "location":"Away","result":"W","score":"6-3"},
    {"date":"Mar 8", "opponent":"@ Vanderbilt",      "location":"Away","result":"L","score":"2-5"},
    {"date":"Mar 9", "opponent":"@ Vanderbilt",      "location":"Away","result":"W","score":"9-4"},
    {"date":"Mar 14","opponent":"Alabama",           "location":"Home","result":"W","score":"7-2"},
    {"date":"Mar 15","opponent":"Alabama",           "location":"Home","result":"L","score":"1-4"},
    {"date":"Mar 16","opponent":"Alabama",           "location":"Home","result":"W","score":"8-3"},
    {"date":"Mar 21","opponent":"@ Tennessee",       "location":"Away","result":"L","score":"3-8"},
    {"date":"Mar 22","opponent":"@ Tennessee",       "location":"Away","result":"W","score":"5-4"},
    {"date":"Mar 23","opponent":"@ Tennessee",       "location":"Away","result":"L","score":"2-6"},
    {"date":"Apr 4", "opponent":"LSU",               "location":"Home","result":"W","score":"4-3"},
    {"date":"Apr 5", "opponent":"LSU",               "location":"Home","result":"W","score":"6-2"},
    {"date":"Apr 6", "opponent":"LSU",               "location":"Home","result":"L","score":"5-7"},
    {"date":"Apr 11","opponent":"@ Arkansas",        "location":"Away","result":"L","score":"3-5"},
    {"date":"Apr 12","opponent":"@ Arkansas",        "location":"Away","result":"W","score":"7-3"},
    {"date":"Apr 13","opponent":"@ Arkansas",        "location":"Away","result":"W","score":"4-2"},
    {"date":"Apr 18","opponent":"Mississippi State", "location":"Home","result":"W","score":"9-1"},
    {"date":"Apr 19","opponent":"Mississippi State", "location":"Home","result":"W","score":"6-4"},
    {"date":"Apr 20","opponent":"Mississippi State", "location":"Home","result":"L","score":"4-6"},
    {"date":"May 9", "opponent":"@ Georgia",         "location":"Away","result":"W","score":"5-2"},
    {"date":"May 10","opponent":"@ Georgia",         "location":"Away","result":"W","score":"8-3"},
    {"date":"May 11","opponent":"@ Georgia",         "location":"Away","result":"L","score":"3-5"},
    {"date":"May 16","opponent":"Texas A&M",         "location":"Home","result":"W","score":"10-4"},
    {"date":"May 17","opponent":"Texas A&M",         "location":"Home","result":"L","score":"2-3"},
    {"date":"May 18","opponent":"Texas A&M",         "location":"Home","result":"W","score":"7-5"},
    {"date":"May 23","opponent":"SEC Tournament",    "location":"Neutral","result":"W","score":"6-3"},
    {"date":"May 24","opponent":"SEC Tournament",    "location":"Neutral","result":"W","score":"4-2"},
    {"date":"May 25","opponent":"SEC Tournament",    "location":"Neutral","result":"L","score":"3-5"},
    {"date":"May 30","opponent":"NCAA Regional (host)","location":"Home","result":"W","score":"11-2"},
    {"date":"May 31","opponent":"NCAA Regional",     "location":"Home","result":"W","score":"8-1"},
    {"date":"Jun 1", "opponent":"NCAA Regional Final","location":"Home","result":"W","score":"5-3"},
    {"date":"Jun 6", "opponent":"Super Regional vs #5 Auburn","location":"Home","result":"W","score":"7-4"},
    {"date":"Jun 7", "opponent":"Super Regional vs #5 Auburn","location":"Home","result":"W","score":"6-5"},
    {"date":"Jun 14","opponent":"CWS vs Florida",    "location":"Neutral","result":"W","score":"4-3"},
    {"date":"Jun 15","opponent":"CWS vs NC State",   "location":"Neutral","result":"W","score":"9-2"},
    {"date":"Jun 17","opponent":"CWS — Troy (elim)","location":"Neutral","result":"L","score":"8-12"},
]

RECRUITING_FB = [
    {"player":"David Gabriel-Georges","pos":"RB",  "stars":"5","status":"Deciding",  "class":"2027","date":"Pending","link":"https://247sports.com/college/mississippi/","source":"247Sports"},
    {"player":"Commit #1 (July 8 streak)",         "pos":"WR",  "stars":"4","status":"Committed","class":"2027","date":"Jul 2026","link":"https://hottytoddy.com","source":"HottyToddy"},
    {"player":"Commit #2 (July 8 streak)",         "pos":"OL",  "stars":"4","status":"Committed","class":"2027","date":"Jul 2026","link":"https://hottytoddy.com","source":"HottyToddy"},
    {"player":"Commit #3 (July 8 streak)",         "pos":"DB",  "stars":"4","status":"Committed","class":"2027","date":"Jul 2026","link":"https://hottytoddy.com","source":"HottyToddy"},
    {"player":"Commit #4 (July 8 streak)",         "pos":"LB",  "stars":"3","status":"Committed","class":"2027","date":"Jul 2026","link":"https://hottytoddy.com","source":"HottyToddy"},
    {"player":"Commit #5 (July 8 streak)",         "pos":"DE",  "stars":"4","status":"Committed","class":"2027","date":"Jul 2026","link":"https://hottytoddy.com","source":"HottyToddy"},
    {"player":"Commit #6 (July 8 streak)",         "pos":"TE",  "stars":"3","status":"Committed","class":"2027","date":"Jul 2026","link":"https://hottytoddy.com","source":"HottyToddy"},
]

PORTAL_BSB = [
    {"player":"Trey Hawsey",     "pos":"1B",  "from":"Louisiana Tech",   "direction":"in","status":"Enrolled","notes":"All-CUSA, .335 AVG, 15 HR"},
    {"player":"Mavrick Rizy",    "pos":"RHP", "from":"LSU",             "direction":"in","status":"Enrolled","notes":"6'9\" SEC exp, Top-115 PG"},
    {"player":"Brent Stukes",    "pos":"RHP", "from":"USC Upstate",     "direction":"in","status":"Enrolled","notes":"8-3, starter experience"},
    {"player":"Sean Carey",      "pos":"LHP", "from":"Sacramento State","direction":"in","status":"Enrolled","notes":"High K-rate bullpen arm"},
    {"player":"Jason Fultz",     "pos":"INF", "from":"Clemson",         "direction":"in","status":"Enrolled","notes":"Versatile, high OBP"},
    {"player":"Kendall Hoffman", "pos":"RHP", "from":"Houston",         "direction":"in","status":"Enrolled","notes":"6'6\" weekend starter"},
    {"player":"Andrew Rogovic",  "pos":"RHP", "from":"Northeastern",    "direction":"in","status":"Enrolled","notes":"Reliable reliever"},
    {"player":"Brady Dallimore", "pos":"C",   "from":"TCU",             "direction":"in","status":"Enrolled","notes":"Big 12 All-Freshman, power bat"},
    {"player":"Blake Fields",    "pos":"OF",  "from":"Houston",         "direction":"in","status":"Enrolled","notes":"Disciplined hitter"},
    {"player":"Eli Pillsbury",   "pos":"LHP", "from":"Jacksonville State","direction":"in","status":"Enrolled","notes":"All-CUSA, durable"},
    {"player":"Charlie Wilcox",  "pos":"RHP", "from":"Georgia Tech",    "direction":"in","status":"Enrolled","notes":"Former Top-100 prospect"},
    {"player":"Charlie Foster",  "pos":"LHP", "from":"Mississippi State","direction":"in","status":"Enrolled","notes":"SEC experience"},
    {"player":"Brayden Randle",  "pos":"IF/OF","from":"Ole Miss",       "direction":"out","status":"Transferred","notes":"Left via portal"},
    {"player":"Blake Ilitch",    "pos":"OF",  "from":"Ole Miss",        "direction":"out","status":"Transferred","notes":"Left via portal"},
    {"player":"Brett Moseley",   "pos":"OF",  "from":"Ole Miss",        "direction":"out","status":"Transferred","notes":"Left via portal"},
]

OXFORD_EVENTS = [
    {"date":"Sep 6",  "event":"Football @ Louisville",               "location":"Louisville, KY",    "type":"Football","notes":"Season opener","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Sep 12", "event":"Football vs Charlotte — Home Opener",  "location":"Vaught-Hemingway",  "type":"Football","notes":"6:45 PM kickoff","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Sep 19", "event":"Football vs LSU — SEC Opener",         "location":"Vaught-Hemingway",  "type":"Football","notes":"6:30 PM • ESPN","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Oct 17", "event":"Football vs Missouri — Homecoming",    "location":"Vaught-Hemingway",  "type":"Football","notes":"2:30 PM • SEC Network","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Oct 31", "event":"Football vs Auburn — Halloween",       "location":"Vaught-Hemingway",  "type":"Football","notes":"11 AM • ESPN/ABC","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Nov 7",  "event":"Football vs Georgia",                  "location":"Vaught-Hemingway",  "type":"Football","notes":"Time TBD • Flex","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Nov 21", "event":"Football vs Wofford — Senior Day",     "location":"Vaught-Hemingway",  "type":"Football","notes":"11 AM","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Nov 27", "event":"Egg Bowl vs Mississippi State",        "location":"Vaught-Hemingway",  "type":"Football","notes":"11 AM • ESPN — Rivalry Week","link":"https://olemisssports.com/sports/football/schedule/"},
    {"date":"Feb 2027","event":"Baseball 2027 Season Opener",         "location":"Swayze Field",       "type":"Baseball","notes":"Date TBD","link":"https://olemisssports.com/sports/baseball/schedule/"},
    {"date":"Aug 2026","event":"Oxford Restaurant Week",              "location":"Oxford Square",      "type":"Oxford",  "notes":"Annual summer event","link":"https://www.visitoxfordms.com"},
    {"date":"Sep 2026","event":"Double Decker Arts Festival (Fall)",  "location":"Oxford Square",      "type":"Oxford",  "notes":"Annual arts & music festival","link":"https://www.visitoxfordms.com"},
    {"date":"Oct 2026", "event":"Ole Miss Homecoming Weekend",        "location":"The Grove & Campus","type":"Oxford",  "notes":"Homecoming parade & festivities","link":"https://olemisssports.com"},
]

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    baseball_items  = []
    football_items  = []
    oxford_items    = []

    for source_name, feed_url in FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                title = entry.get("title", "")
                if is_baseball(title):
                    baseball_items.append(entry_to_item(entry, source_name))
                elif is_football(title):
                    football_items.append(entry_to_item(entry, source_name))
                elif is_oxford(title):
                    oxford_items.append(entry_to_item(entry, source_name))
            print(f"Fetched {source_name}: {len(parsed.entries)} entries")
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")

    baseball_items = dedupe(baseball_items)
    football_items = dedupe(football_items)
    oxford_items   = dedupe(oxford_items)

    # Sort by published date descending
    for lst in [baseball_items, football_items, oxford_items]:
        lst.sort(key=lambda x: x.get("published", ""), reverse=True)

    total_live = len(baseball_items) + len(football_items) + len(oxford_items)

    output = {
        "last_updated_utc":    datetime.now(timezone.utc).isoformat(),
        "item_count":          total_live,
        "sources":             list(FEEDS.keys()),
        # Live RSS sections
        "baseball":            baseball_items,
        "football":            football_items,
        "oxford":              oxford_items,
        # Static structured sections (updated in-code; future scraper targets)
        "football_schedule":   FOOTBALL_SCHEDULE,
        "season_results_2026": SEASON_RESULTS_2026,
        "recruiting_fb":       RECRUITING_FB,
        "portal_bsb":          PORTAL_BSB,
        "oxford_events":       OXFORD_EVENTS,
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nWrote data.json — {total_live} live items + all structured sections")
    print(f"  Baseball: {len(baseball_items)} | Football: {len(football_items)} | Oxford: {len(oxford_items)}")
    print(f"  Schedule: {len(FOOTBALL_SCHEDULE)} games | Season: {len(SEASON_RESULTS_2026)} results")
    print(f"  Recruiting: {len(RECRUITING_FB)} | Portal: {len(PORTAL_BSB)} | Events: {len(OXFORD_EVENTS)}")

if __name__ == "__main__":
    main()
