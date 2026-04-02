import os
import logging
from wuiw.intake import backfill
from wuiw.editor import save_assignments

logger = logging.getLogger(__name__)

def main():
    """Run intake.backfill on date range and govt body set in env"""
    start = os.getenv("BACKFILL_START")
    end = os.getenv("BACKFILL_END")
    body_id = os.getenv("BACKFILL_BODY_ID")
    
    if not all([start, end, body_id]):
        logger.error("Missing required env vars: BACKFILL_START, BACKFILL_END, BACKFILL_BODY_ID")
        return
    
    logger.info("WUIW BACKFILL pipeline started")
    assignments = backfill(start, end, body_id)
    logger.info(f"Backfill fetch returned {len(assignments)} assignments")
    save_assignments(assignments)
    logger.info("WUIW BACKFILL complete")

if __name__ == "__main__":
    main()