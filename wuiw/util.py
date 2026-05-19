import logging
from rapidfuzz import process

logger = logging.getLogger(__name__)

def classify(title, classifications, threshold=80, doc_type_fallback=False, meeting_type_fallback=False):
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

    if meeting_type_fallback:
        title_lower = title.lower()
        if "regular" in title_lower:
            return "regular meeting"
        elif "special" in title_lower:
            return "special meeting"
        elif "hearing" in title_lower:
            return "public hearing"

    logger.warning("Could not classify from title: %s", title)
    return "unclassified"