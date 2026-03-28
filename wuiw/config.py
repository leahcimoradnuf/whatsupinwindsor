

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
RSS_URL="https://www.windsorct.gov/RSSFeed.aspx?ModID=65&CID=All-0"

# Database Configuration
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Test Data
RSS_CURL="http://localhost:8000/town_council_rss.xml"
ARTICLES_FILE="/home/mike/myprojects/whatsupinwindsor/test_data/articles.json"

# Classification Data
DOCUMENT_TYPES = ["Agenda", "Minutes", "Votes"]
MUNICIPAL_BODIES = ["Town Council", "Planning Commission", "Board of Education"] #TODO expand this to cover all bodies of govt
DOCUMENT_TYPES = ["Agenda", "Minutes", "Vote"]
MEETING_TYPES = ["Regular Meeting", "Public Hearing", "Special Meeting"]

# State machine
STATE_FILE = "modified_state.json"
ASSIGNMENT_LIST = "assignments.json"
STATUS_PENDING = "pending"
STATUS_ASSIGNED = "assigned"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"

# Journalists
PROVIDER = "Anthropic" # or "OpenAI", etc...
_provider = None
def get_provider():
    global _provider
    if _provider is None:
        from wuiw.journalist import providers
        if PROVIDER not in providers:
            raise ValueError(f"Unknown provider: {PROVIDER}")
        
        _provider = providers[PROVIDER]()
        
    return _provider
