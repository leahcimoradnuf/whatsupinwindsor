#TODO update shebang once deployed to .venv on pythonanywhere

import logging
from wuiw.intake import get_rss
from wuiw.config import RSS_URL
from wuiw.editor import save_articles, save_assignments, update_status, assign
from wuiw.reporter import fetch_documents
from wuiw.writer import write_article

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]  # stdout
)

logger = logging.getLogger(__name__)

def main():
    """
    Connect to RSS feed for Town Council and summarize new meeting documents
    """
    logger.info("WUIW pipeline started")

    # Fetch RSS feed
    logger.info("Pinging RSS feed.")
    try:
        new_leads = get_rss(RSS_URL)
    except Exception as e:
        logger.error("Feed parsing failed: %s", e)
        exit(1)
    logger.info(f"RSS fetch returned {len(new_leads)} new leads")
    
    # Enter new assignments to db table: assignments
    save_assignments(new_leads)
    logger.info(f"Assignments saved")

    # Compile a list of pending assignments
    assignments = assign()
    logger.info(f"{len(assignments)} assignments pending")

    # Send assignments to reporter to transcribe docs. 
    # TODO: Parameter doc_type is set to "minutes" for v1.0, update in later versions
    for assignment in assignments:
        documents, status, error = fetch_documents(assignment["materials"], doc_type="minutes")
        if not documents:
            update_status(assignment["meeting_id"], status, error)
            logger.warning(f"fetch_documents failed for {assignment['meeting_id']}: {error}")
            continue
        logger.info(f"Fetched {len(documents)} documents for {assignment['meeting_id']}")

        # Summarize documents. 
        for doc_type, text in documents.items():
            article, status, error = write_article(assignment["meeting_id"], text, doc_type)
            if not article:
                update_status(assignment["meeting_id"], status, error)
                logger.warning(f"write_article failed for {assignment['meeting_id']}: {error}")
                continue
            save_articles([article])
            logger.info(f"Article saved: {article['meeting_id']} {doc_type}")
            update_status(article["meeting_id"], status, error)

    logger.info("WUIW pipeline complete")

if __name__ == "__main__":
    main()