# module for reading and parsing RSS feeds
import json
import os
import feedparser
import logging
import datetime
from email.utils import parsedate_to_datetime
from wuiw.config import USER_AGENT, STATUS_PENDING, STATUS_ASSIGNED, MUNICIPAL_BODIES, STATUS_FAILED, MEETING_TYPES
from wuiw.util import classify

logger = logging.getLogger(__name__)

def get_rss(rss_url):
   
    feed = feedparser.parse(rss_url, agent=USER_AGENT, modified=None)

    if feed.status == 304:
        logger.info("STATUS: %s; No updates", feed.status)
        return {}

    if feed.status != 200:
        raise Exception("Feed error: %s", feed.status)
  
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