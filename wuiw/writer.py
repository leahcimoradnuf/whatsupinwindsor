# Module for writing content using AI Authors
import logging
from wuiw.journalist import OpenAIProvider

logger = logging.getLogger(__name__)

# Define LLM API Provider
provider = OpenAIProvider()
# provider = AnthropicAIProvider()

def recieve_assignment(text, doc_type):
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

def write_article(text, doc_type, chunked=False):
    if chunked:
        pass

    if not chunked:
        # TODO try logic here for exception handling
        result = provider.summarize(text, doc_type)
        return result
    
def review_article(article):
    """article should be json_type. If not, store raw data somewhere and fail gracefully (flag for human admin review)"""
    pass

def submit_article(article):
    """send json object to editor for publishing"""
    pass