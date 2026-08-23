import logging
from datetime import datetime
from wuiw.intake import get_rss
from wuiw.config import RSS_URL, STATUS_COMPLETE, STATUS_WARNING, STATUS_FAILED, STATUS_PARTIAL, STATUS_DONE
from wuiw.editor import save_articles, save_assignments, update_status, assign, open_intake, close_intake, save_ai_log, save_civic_log, send_alert, record_document_count
from wuiw.reporter import fetch_documents
from wuiw.writer import write_article
from wuiw.log import ai_log, civic_log

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]  # stdout
)

logger = logging.getLogger(__name__)

def main():
    """
    Main Pipeline Source Code
    """
    # Initialize run conditions
    run_id = None
    new_assignments = 0
    failed_assignments = 0
    run_status = STATUS_FAILED
    error = None
    ai_log.reset()
    civic_log.reset()

    try:
        run_id = open_intake(datetime.now())
        ai_log.set_run_id(run_id)
        civic_log.set_run_id(run_id)
        logger.info("WUIW pipeline started")

        # Fetch RSS feed
        logger.info("Pinging RSS feed.")
        try:
            new_leads = get_rss(RSS_URL)
        except Exception as e:
            logger.error("Feed parsing failed: %s", e)
            status = STATUS_FAILED
            error = "Feed parsing failed, see logs for details"
            raise
        logger.info(f"RSS fetch returned {len(new_leads)} new leads")
        
        # Enter new assignments to db table: assignments
        save_assignments(new_leads, run_id=run_id)
        logger.info(f"Assignments saved")

        # Compile a list of pending assignments
        assignments = assign() 
        new_assignments = len(assignments)
        logger.info(f"{len(assignments)} assignments pending")

        # Send assignments to reporter to transcribe docs. 
        for assignment in assignments:
            summarized = 0
            failed = False
            documents, status, error, count = fetch_documents(assignment["materials"])
            if not documents:
                update_status(assignment["meeting_id"], status, error)
                logger.warning(f"fetch_documents failed for {assignment['meeting_id']}: {error}")
                failed = True
                continue
            logger.info(f"Fetched {len(documents)} documents for {assignment['meeting_id']}") 
            record_document_count(assignment["meeting_id"], available=count) #TODO needs unit test

            # Summarize documents. 
            articles = []
            for doc in documents:
                doc_type = doc["doc_type"]
                text = doc["text"]

                # Initial document save (set all status to REPORTING)
                save_articles(initial_save=True, id=assignment["meeting_id"], doc_type=doc_type)

                article, status, error = write_article(assignment["meeting_id"], text, doc_type)

                if not article:
                    logger.warning(f"write_article failed for {assignment['meeting_id']} {doc_type}: {error}")

                articles.append((article, status, error))

                if status == STATUS_DONE:
                    summarized += 1

            save_articles(articles=articles) #TODO save_articles() needs a refactor to handle new signature/schema
            # This gets moved into save_articles() -> logger.info(f"Article saved: {article['meeting_id']} {doc_type}")

            # Document count vs. available status logic
            record_document_count(assignment["meeting_id"], summarized=summarized)

            #TODO this logic is fine for now but will need to be updated to deploy retry() and handle STATUS_WARNING and STATUS FAILED
            if summarized >= 0 and summarized < count:
                status = STATUS_PARTIAL
            elif summarized == count:
                status = STATUS_COMPLETE

            update_status(article["meeting_id"], status, error)
            
            # count failure
            if failed:
                failed_assignments += 1
        
        if failed_assignments == new_assignments and new_assignments > 0:
            run_status = STATUS_FAILED
            error = "all assignments failed"
        elif failed_assignments > 0 and failed_assignments < new_assignments:
            run_status = STATUS_WARNING
            error = f"{failed_assignments} assignments failed"
        else:
            run_status = STATUS_COMPLETE
            error = None

        logger.info("WUIW pipeline complete")
    except Exception as e:
        run_status = STATUS_FAILED
        error = "WUIW pipeline failed, see logs for details"
        logger.error("WUIW pipeline failed. Error: %s", e)
    finally:
        # log http/api requests
        save_civic_log(civic_log.info)
        save_ai_log(ai_log.info)

        if not run_id:
            logger.warning("WUIW pipeline not captured in intake_records. It may not have succeeded. Check logs for details.")
        else:
            close_intake(run_id, datetime.now(), run_status, new_assignments, failed_assignments, error=error)
        
        if run_status == STATUS_FAILED:
            send_alert(error)
        

if __name__ == "__main__":
    main()
