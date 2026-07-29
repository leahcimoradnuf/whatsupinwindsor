import logging
from rapidfuzz import process
from wuiw.config import CLASSIFICATIONS # TODO build alias map in config.py

logger = logging.getLogger(__name__)

def classify(title, town_id=None, class_type=None, threshold=80, fallback=True):
    match, score, _ = process.extractOne(title.lower(), [c.lower() for c in list(CLASSIFICATIONS[town_id][class_type].keys())])
    if score >= threshold:
        return CLASSIFICATIONS[town_id][class_type][match]

    def doc_type_fallback(title_lower):
        if "minutes" in title_lower:
            return "minutes"
        elif "agenda" in title_lower:
            return "agenda"
        elif "voting" in title_lower:
            return "voting_grid"
        elif "grid" in title_lower:
            return "voting_grid"
        elif "action" in title_lower:
            return "voting_grid"
        elif title_lower.endswith("-vg"):
            return "voting_grid"

    def meeting_type_fallback(title_lower):
        if "regular" in title_lower:
            return "regular meeting"
        elif "special" in title_lower:
            return "special meeting"
        elif "hearing" in title_lower:
            return "public hearing"
        
    def body_type_fallback(title_lower):
        pass
   

    dispatch_fallback = {
        "doc_type": doc_type_fallback,
        "municipal_body": body_type_fallback,
        "meeting_type": meeting_type_fallback
    }

    if fallback:
        classification = dispatch_fallback[class_type](title.lower())
        if classification:
            return classification

    logger.warning("Could not classify from title: %s", title)
    return "unclassified"