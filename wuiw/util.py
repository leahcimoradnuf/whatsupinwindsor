import logging
from rapidfuzz import process

logger = logging.getLogger(__name__)

def classify(title, classifications, threshold=80):
    match, score, _ = process.extractOne(title.lower(), [c.lower() for c in classifications])
    if score >= threshold:
        return match
    logger.warning("Could not classify body from title: %s", title)
    return "unclassified"