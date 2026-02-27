# module for reading and parsing RSS feeds
import feedparser
from datetime import datetime

#TODO get modified to pass into the function as a datetime.datetime type, not nonetype
def get_rss(rss_url, modified=None): #, etag=None, modified=None):
    """
    Read RSS feed.

    Returns:
        (new_entries_dict, modified)
        OR (None, modified) if 304
    """

    def parsedate(date_string):
        """helper script for reading last-modified date"""
        format_string = '%a, %d %b %Y %H:%M:%S GMT'
        last_modified = datetime.strptime(date_string, format_string)
        return last_modified

    feed = feedparser.parse(rss_url)

    # --- Nothing new ---
    if feed.status == 304:
        print("No new RSS entries")
        return None, modified

    # --- New content ---
    if feed.status == 200:
        last_modified = parsedate(feed['headers']['last-modified'])
        if not modified or modified and last_modified > modified:
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
            print(last_modified)

            return new_entries, last_modified
        # else:
            # print("No new RSS entries")

    # --- Error case ---
    print(f"No new RSS entries found. Status: {feed.status}")
    return None

def assign(url):
  """
  Scan meeting url for Agenda document.
  Return agenda summary text, zoom call-info if present, urls for other documents
  """
  pass
