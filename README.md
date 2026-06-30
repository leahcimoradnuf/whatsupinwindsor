*A simple-as-can be flask app for tracking, summarizing, and reporting on official government proceedings in Windsor CT*

## What it Does 
A backend routine runs on a cron schedule daily. It identifies new items in the town's RSS feed, downloads the meeting minute text, summarizes with an AI provider, and stores the summary in a PostgreSQL database.

The frontend flask app presents the summaries in a blog-like format.

[See it in action.](https://whatsupinwindsor.com)

## Why it Exists
To serve busy residents that still want to be informed of local government decisions but can't carve out 3 hours on a Monday night to attend the meetings.

## How it Works
A summary of the architecture is below. For more details read [whatsupinwindsor.com/docs](https://whatsupinwindsor.com/docs)

### Architecture
```text
wuiw/
├── main.py          # Orchestration — runs the pipeline, calls everything else
├── intake.py        # Outside → system — RSS ingestion, assignment state management
# Management
├── editor.py        # System → system — audits assignments, routes updates, admin data ops
# Data Ops
├── reporter.py      # System → outside — fetches document content when assigned
├── writer.py        # Content → manages summaries + extracted metadata
├── journalist.py    # Content → generates summaries + extracted metadata (AI API)
├── log.py           # System → logs outgoing HTTP requests and AI API requests
├── app.py           # HTTP interface — Flask routes only, no business logic
└── config.py        # Constants, environment variables, shared configuration
```
### Pipeline
```text
main.py
  → intake.get_rss()                 # returns list of assignment packets
  → editor.save_assignments()        # persists assignment data to storage
  → editor.assign()                  # queries assignment table and returns list of unassigned packets
  → writer.write_article()           # for each assignment, returns article dict
  → editor.save_article()            # persists to storage
```

## Getting Started
There are two pathways to set up an app like this in your town.

### 1. Self Deploy
If you're comfortable coding feel free to clone and deploy however you wish. Below is an overview of how WUiW is deployed.

**Prerequisites**
- A Railway account with Hobby Tier or higher
- This code cloned into a separate GitHub repo

**Environment Variables**
Set these in the Railway environment

Variable|Description
--------|-----------
DATABASE_URL|url to postgre db
PROVIDER|Name of AI provider class to use from journalist.py
ANTHROPIC_API_KEY|API key for AI provider, add keys for other providers if preferred
RSS_URL|url for the RSS feed to collect town data from (Configured for towns using CivicPlus hosting service only)
BACKFILL_START|Set this for manual backfill runs YYYY-MM-DD format
BACKFILL_END|Set this for manual backfill runs YYYY-MM-DD format
BACKFILL_BODY_ID|Set this for manual backfill runs (Configured for towns using CivicPlus hosting service only)
ALERT_EMAIL|Optionally add an email address to recieve alerts if the app fails.
ALERT_EMAIL_PASSWORD|Optionally add an email address to recieve alerts if the app fails.
ADMIN-PASSWORD|Password to enter editor mode in the front end flask app
SECRET_KEY|Flask secret key for managing admin sessions

**To deploy on Railway**

Configure your dashboard with three services:
- GitHub repo for backend cronjob
- GitHub repo for frontend flask app
- PostgreSQL db linked to both the front and back end services

### 2. Franchise Network
Interested in bringing this to your municipality without the technical setup? Reach out to inquire about a franchise agreement.

Email: mike@whatsupinwindsor.com

## Contributing
MIT licensed, PRs welcome, [read the docs](https://whatsupinwindsor.com/docs).

## License
[MIT](LICENSE)