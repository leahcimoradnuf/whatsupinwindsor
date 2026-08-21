

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# HTTP behavior
USER_AGENT = "WUIW/0.1 (+https://app.whatsupinwindsor.com; contact: mike@whatsupinwindsor.com)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}
REQUEST_DELAY = 20

# Scraper Target
RSS_URL=os.getenv("RSS_URL")

# Database Configuration

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# Classification Data
CLASSIFICATIONS = {
    "windsorct": {
        "doc_type": {"voting grid": "voting_grid", "minutes": "minutes", "agenda": "agenda", "action grid": "voting_grid", "unapproved minutes": "minutes", "meeting minutes": "minutes", "draft minutes": "minutes", "grid": "voting_grid"},
        "municipal_body": {"town council": "town_council", "planning commission": "planning_commission", "board of education": "board_of_education"},
        "meeting_type": {"regular meeting": "regular_meeting", "public hearing": "public_hearing", "special meeting": "special_meeting"}
    }
}
DOCUMENT_TYPES = ["Agenda", "Minutes", "Votes"]
MUNICIPAL_BODIES = ["Town Council", "Planning Commission", "Board of Education"] #TODO expand this to cover all bodies of govt
MEETING_TYPES = ["Regular Meeting", "Public Hearing", "Special Meeting"]

# State machine
## Assignment Level
STATUS_PENDING = "pending"
STATUS_ASSIGNED = "assigned"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"
STATUS_WARNING = "warning"
STATUS_PARTIAL = "partial"

## Document Level
STATUS_ZERO = "zero"
STATUS_DEAD_LEAD = "dead_lead"
STATUS_DRAFT = "draft"
STATUS_FOLLOW_UP = "follow_up"
STATUS_REPORTING = "reporting"
STATUS_SOURCED = "sourced"
STATUS_DONE = "done"


# Journalists
PROVIDER = os.getenv("PROVIDER") 
_provider = None
def get_provider():
    global _provider
    if _provider is None:
        from wuiw.journalist import providers
        if PROVIDER not in providers:
            raise ValueError(f"Unknown provider: {PROVIDER}")
        
        _provider = providers[PROVIDER]()
        
    return _provider

