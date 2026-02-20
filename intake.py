# module for reading and parsing RSS feeds
import feedparser

def get_rss(rss_url, headers, etag=None, modified=None):
    """
    Read RSS feed.

    Returns:
        (new_entries_dict, etag, modified)
        OR (None, etag, modified) if 304
    """

    feed = feedparser.parse(
        rss_url,
        headers=headers,
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

            new_entries[id_parts[-2]] = {
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

def assign():
  pass
