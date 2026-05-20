# Module for writing content using AI Authors
import logging
from datetime import datetime
from wuiw.config import get_provider, STATUS_FAILED, STATUS_COMPLETE
from wuiw.log import ai_log

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["meeting_date", "headline", "bullets", "blurb"]

def receive_assignment(text, doc_type):
    pass

def chunk_packet(text, doc_type):
    pass
    
def review_article(draft):
    """Run checks on data coming back from AI provider
   
    Args:
        draft (dict): article information created by writer.write_article()
    """
    # check returned object is dictionary
    if not isinstance(draft, dict):
        return None, STATUS_FAILED, "draft is not a dict"
    
    # check all keys exist
    missing = REQUIRED_KEYS - draft.keys()
    if missing:
        return None, STATUS_FAILED, f"missing keys: {missing}"
    
    # check date format validation
    try:
        datetime.fromisoformat(draft["meeting_date"])
    except ValueError:
        logger.warning("date value: %s is not ISO format", draft["meeting_date"])
        return None, STATUS_FAILED, f"date: {draft['meeting_date']} not in format YYYY-MM-DD"
    
    # check bullets is a list etc
    if not isinstance(draft["bullets"], list):
        return None, STATUS_FAILED, "bullets is not a list"
    
    return draft, STATUS_COMPLETE, None

# Main routine of writer.py
def write_article(meeting_id, text, doc_type):
    """Send document text to journalist for summarization.
    
    Args:
        meeting_id (str): composite meeting id
        text (str): document text
        doc_type (str): document type for prompt construction
    
    Returns:
        article (tup): (article dictionary item, status, error message)
    """
    try:
        provider = get_provider()
        draft, client_status, input_tokens, output_tokens = provider.summarize(text, doc_type)
        ai_log.record(datetime.now(), provider.model, client_status, input_tokens, output_tokens)
    except Exception as e:
        ai_log.record(datetime.now(), provider.model, "FAIL", None, None)
        return None, STATUS_FAILED, f"summarize failed: {e}"
    
    article, status, error = review_article(draft)
    
    if status == STATUS_FAILED:
        return None, STATUS_FAILED, error
    
    return {
        "meeting_id": meeting_id,
        "meeting_date": article.get("meeting_date"),
        "byline": provider.model,
        "doc_type": doc_type,
        "summary": article
    }, STATUS_COMPLETE, None
