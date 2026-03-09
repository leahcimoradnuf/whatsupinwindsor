#TODO update shebang once deployed to .venv on pythonanywhere

import logging
from wuiw.intake import get_rss, sort_assignments, assign
from wuiw.config import RSS_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    filename="wuiw_main.log"
)

logger = logging.getLogger(__name__)

def main():
    """
    Do the thing: TODO description here
    """
    logger.info("Pinging RSS feed.")
    try:
        new_feed_entries = get_rss(RSS_URL)
    except Exception as e:
        logger.error("Feed parsing failed: %s", e)
        exit(1)

    logger.info("Found %s new entries! Sorting.", len(new_feed_entries))
    if sort_assignments(new_feed_entries):
        logger.info("Assigning stories.")
        assign()
    else:
        logger.info("Nothing to assign.")

if __name__ == "__main__":
    main()