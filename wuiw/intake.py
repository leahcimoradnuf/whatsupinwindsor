# module for reading and parsing RSS feeds
import json
import os
import feedparser
from email.utils import parsedate_to_datetime
from wuiw.config import USER_AGENT, STATE_FILE, ASSIGNMENT_LIST

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

    feed = feedparser.parse(rss_url, agent=USER_AGENT, modified=stored_modified)

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

def sort_assignments(entries):
    """
    Store new rss data to persistent json record
    """
    # Read existing data (handling the case where the file might not exist yet)
    try:
        with open(ASSIGNMENT_LIST, 'r') as f:
            data = json.load(f)

            if not isinstance(data, dict):
                data = {}

    except FileNotFoundError:
        data = {}
    
    changed = False

    # Merge / update only if different
    for assignment_id, payload in entries.items():
        if data.get(assignment_id) != payload:
            data[assignment_id] = payload
            changed = True

    # Only write if something changed
    if changed:
        with open(ASSIGNMENT_LIST, "w") as f:
            json.dump(data, f, indent=4)

    return changed
    

def assign(url):
  """
  Scan meeting url for Agenda document.
  Return agenda summary text, zoom call-info if present, urls for other documents
  """
  pass
