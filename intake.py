# module for reading and parsing RSS feeds
import feedparser

#TODO there is no etag or last modified header, make this handle it with published parsed
def get_rss(rss_url, etag=None, modified=None):
    """
    Read RSS feed.

    Returns:
        (new_entries_dict, etag, modified)
        OR (None, etag, modified) if 304
    """

    feed = feedparser.parse(
        rss_url,
        etag=etag,
        modified=modified
    )

    # --- Nothing new ---
    if feed.status == 304:
        print("No new RSS entries")
        return None, etag, modified

    # --- New content ---
    if feed.status == 200:
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

        return new_entries, feed.etag, feed.modified

    # --- Error case ---
    print(f"No RSS feed found. Status: {feed.status}")
    return None, etag, modified

def assign(url):
  """
  Scan meeting url for Agenda document.
  Return agenda summary text, zoom call-info if present, urls for other documents
  """
  pass
