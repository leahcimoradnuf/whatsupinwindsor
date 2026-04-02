import logging
from rapidfuzz import process

logger = logging.getLogger(__name__)

def classify(title, classifications, threshold=80, doc_type_fallback=False):
    match, score, _ = process.extractOne(title.lower(), [c.lower() for c in classifications])
    if score >= threshold:
        return match

    if doc_type_fallback:
        title_lower = title.lower()
        if "minutes" in title_lower:
            return "minutes"
        elif "agenda" in title_lower:
            return "agenda"
        elif "voting" in title_lower:
            return "voting_grid"

    logger.warning("Could not classify from title: %s", title)
    return "unclassified"