# module for reading and parsing RSS feeds
import feedparser
import logging
import datetime
import requests
import time
from wuiw.config import USER_AGENT, HEADERS, MUNICIPAL_BODIES, MEETING_TYPES, REQUEST_DELAY
from wuiw.util import classify
from bs4 import BeautifulSoup
from wuiw.log import civic_log
# from datetime import datetime

logger = logging.getLogger(__name__)

def get_rss(rss_url):
   
    feed = feedparser.parse(rss_url, agent=USER_AGENT, modified=None)
    civic_log.record(datetime.datetime.now(), rss_url, feed.status)

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

def backfill(start, end, body_id):
    """ Where start and end are date strings in ISO format
    body_id is int (18 for Windsor TC)"""
    assignments = []
    base_url = "https://www.windsorct.gov/AgendaCenter/ViewFile/Agenda/_"
    start_date = datetime.date.fromisoformat(start)
    end_date = datetime.date.fromisoformat(end)
    # construct url and issue requests.get() 
    url = f"https://www.windsorct.gov/AgendaCenter/Search/?term=&CIDs={body_id},&startDate={start_date.month:02d}/{start_date.day:02d}/{start_date.year}&endDate={end_date.month:02d}/{end_date.day:02d}/{end_date.year}&dateRange=&dateSelector="
    # HTTP request
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        logger.error("Backfill request failed: %s", response.status_code)
        return []
    
    time.sleep(REQUEST_DELAY)
    soup = BeautifulSoup(response.text, 'html.parser')
    leads = soup.select('td p a[id]')
    for lead in leads:
        body = classify(lead.text, MUNICIPAL_BODIES)
        body = "_".join(body.lower().split())
        meeting_type = classify(lead.text, MEETING_TYPES)
        month = lead["id"][0:2]
        day = lead["id"][2:4]
        year = lead["id"][4:8]
        published_date = f"{year}-{month}-{day}"
        meeting_id = f"{body}_{lead['name']}_{year}"
        materials = f"{base_url}{lead['id']}?html=true"

        assignments.append({
            "meeting_id": meeting_id,
            "meeting_type": meeting_type,
            "body": body,
            "published_date": published_date,
            "materials": materials
        })
    
    return assignments