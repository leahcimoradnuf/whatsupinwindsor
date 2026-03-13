# Module for writing content using AI Authors
import logging
from datetime import datetime
from wuiw.config import PROVIDER, STATUS_FAILED, STATUS_COMPLETE

logger = logging.getLogger(__name__)

# Read LLM API Provider from config
provider = PROVIDER

REQUIRED_KEYS = ["meeting_date", "headline", "bullets", "blurb"]

def receive_assignment(text, doc_type):
    """Review text and doc type, validate input before sending to AI Provider
    - correct format?
    - chunking needed?
    """
    pass

def chunk_packet(text, doc_type):
    """split long text up
    - modify prompts (tell LLM it's working in chunks)
    - return list of text chunks to be fed to AI one at a time
    """
    pass
    
def review_article(draft):
    """article should be json_type. If not, store raw data somewhere and fail gracefully (flag for human admin review)
    Review draft, return article
    make changes if necessary, add metadata
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
def write_article(meeting_id, text, doc_type, chunked=False):
    # TODO recieve_assignment and chunking goes here
    # TODO try logic here for exception handling
    draft = provider.summarize(text, doc_type)
    article, status, error = review_article(draft)
    
    if status == STATUS_FAILED:
        return None, STATUS_FAILED, error
    
    article["meeting_id"] = meeting_id
    article["byline"] = provider.model
    return article, STATUS_COMPLETE, None
