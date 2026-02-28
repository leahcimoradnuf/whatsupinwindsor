# module for reading and parsing RSS feeds
import json
import os
import feedparser
from email.utils import parsedate_to_datetime

STATE_FILE = "modified_state.json"

def load_modified():
    if not os.path.exists(STATE_FILE):
        return None
    
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        return parsedate_to_datetime(data["modified"]).timetuple()
    
def save_modified(modified_struct):
    from email.utils import format_datetime
    from datetime import datetime

    dt = datetime(*modified_struct[:6])
    formatted = format_datetime(dt)

    with open(STATE_FILE, "w") as f:
        json.dump({"modified": formatted}, f)

def get_rss(rss_url):
    stored_modified = load_modified()

    feed = feedparser.parse(rss_url, agent="Me.", modified=stored_modified)

    if feed.status == 304:
        print("No updates")
        return {}

    if feed.status != 200:
        raise Exception(f"Feed error: {feed.status}")

    # Persist new modified time
    if feed.modified_parsed:
        save_modified(feed.modified_parsed)
    
    # Parse the feed
    print(f"Parsing new data")
    new_entries = {}

    for entry in feed.entries:
        id_parts = entry["id"].split("/")
        id = id_parts[-2]
        year = entry["published_parsed"][0]
        month = entry["published_parsed"][1]
        day = entry["published_parsed"][2]

        url = (
            f"https://www.windsorct.gov/AgendaCenter/"
            f"ViewFile/Agenda/_{month:02d}{day:02d}{year}-{id}?html=true"
        )

        new_entries[id] = {
            "year": year,
            "month": month,
            "day": day,
            "hour": entry["published_parsed"][3],
            "minute": entry["published_parsed"][4],
            "url": url
        }
            
    return new_entries

def assign(url):
  """
  Scan meeting url for Agenda document.
  Return agenda summary text, zoom call-info if present, urls for other documents
  """
  pass
