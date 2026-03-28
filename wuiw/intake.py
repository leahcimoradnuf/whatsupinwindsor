# module for reading and parsing RSS feeds
import json
import os
import feedparser
import logging
import datetime
from email.utils import parsedate_to_datetime
from wuiw.config import USER_AGENT, STATE_FILE, ASSIGNMENT_LIST, STATUS_PENDING, STATUS_ASSIGNED, MUNICIPAL_BODIES, STATUS_FAILED, MEETING_TYPES
from wuiw.util import classify

logger = logging.getLogger(__name__)

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
        logger.info("STATUS: %s; No updates", feed.status)
        return {}

    if feed.status != 200:
        raise Exception("Feed error: %s", feed.status)

    # Persist new modified time
    if getattr(feed, "modified_parsed", None):
        save_modified(feed.modified_parsed)
    
    # Parse the feed
    logger.info("STATUS: %s; Parsing new data", feed.status)
    new_entries = []
    for entry in feed.entries:
        try:    
            id_parts = entry["id"].split("/")
            meeting_id = id_parts[-2]
            title = entry["title"]
            body = classify(title, MUNICIPAL_BODIES)
            body = "_".join(body.lower().split())
            meeting_type = classify(title, MEETING_TYPES)
            year = entry["published_parsed"][0]
            month = entry["published_parsed"][1]
            day = entry["published_parsed"][2]
            pub_date = datetime.date(year, month, day).isoformat()

            composite_id = f"{body}_{meeting_id}_{year}"
            url = (
                f"https://www.windsorct.gov/AgendaCenter/"
                f"ViewFile/Agenda/_{month:02d}{day:02d}{year}-{meeting_id}?html=true"
            )

            new_entries.append({
                "meeting_id": composite_id,
                "meeting_type": meeting_type,
                "body": body,
                "published_date": pub_date,
                "materials": url
                })

        except KeyError as e:
            logger.warning("bad entry: %s", e)
            continue
                    
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

    # Merge / update only if different, manage assigned tag
    for assignment_id, payload in entries.items():

        existing = data.get(assignment_id)

        payload_copy = payload.copy()

        if existing:
            existing_content = {k: v for k, v in existing.items() if k != "status"}

            if existing_content == payload:
                continue  # nothing changed

        # If we get here, either new OR changed
        payload_copy["status"] = STATUS_PENDING
        data[assignment_id] = payload_copy
        changed = True

    # Only write if something changed
    if changed:
        with open(ASSIGNMENT_LIST, "w") as f:
            json.dump(data, f, indent=4)

    return changed
    
def assign():
    """
    push unassigned url's to reporter .py and manage state in ASSIGNMENT_LIST
    """
    try:
        with open(ASSIGNMENT_LIST, 'r') as f:
            data = json.load(f)

            if not isinstance(data, dict):
                data = {}
    except FileNotFoundError:
        data = {}
    
    changed = False

    new_assignments = []

    for assignment_id, payload in data.items():
        if payload.get("status") == STATUS_PENDING:
            try:
                new_assignments.append((assignment_id, payload["materials"]))
            except KeyError as e:
                logger.warning("Material packet for %s not found.", assignment_id)
                data[assignment_id]["status"] = STATUS_FAILED
                data[assignment_id]["error_message"] = str(e)
                continue
            data[assignment_id]["status"] = STATUS_ASSIGNED
            logger.info("Assigning task: %s", assignment_id)
            changed = True
        
    if changed:
        logger.info("Changing status in ASSIGNMENT_LIST at:\n%s", ASSIGNMENT_LIST)
        with open(ASSIGNMENT_LIST, "w") as f:
            json.dump(data, f, indent=4)

    logger.info("Sending assignments to reporter.")
    return new_assignments

def update_status(assignment_id, status, error_message=None):
    """use in main() to manage assignment state"""
    try:
        with open(ASSIGNMENT_LIST, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False

    if assignment_id not in data:
        return False

    data[assignment_id]["status"] = status
    if error_message:
        data[assignment_id]["error_message"] = error_message

    with open(ASSIGNMENT_LIST, 'w') as f:
        json.dump(data, f, indent=4)

    return True