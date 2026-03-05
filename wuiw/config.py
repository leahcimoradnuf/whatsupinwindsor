# HTTP header info
USER_AGENT = "WUIW/0.1 (+https://app.whatsupinwindsor.com; contact: mike@whatsupinwindsor.com)"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}

# Test Data
RSS_URL="http://localhost:8000/town_council_rss.xml"

# Classification Data
MUNICIPAL_BODIES = ["Town Council", "Planning Commission", "Board of Education"]
DOCUMENT_TYPES = ["Agenda", "Minutes", "Votes"]

# State machine
STATE_FILE = "modified_state.json"
ASSIGNMENT_LIST = "assignments.json"
STATUS_PENDING = "pending"
STATUS_ASSIGNED = "assigned"
STATUS_COMPLETE = "complete"
STATUS_FAILED = "failed"