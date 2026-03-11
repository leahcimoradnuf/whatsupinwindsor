Summary 
=======

A simple-as-can be flask app for tracking, summarizing, and reporting on official government proceedings in Windsor CT

Architecture 
============
```text
wuiw/
├── main.py          # Orchestration — runs the pipeline, calls everything else
├── intake.py        # Outside → system — RSS ingestion, assignment state management
# Management
├── editor.py        # System → system — audits assignments, routes updates, admin data ops
# Data Ops
├── reporter.py      # System → outside — fetches document content when assigned
├── writer.py        # Content → summaries + extracted metadata (AI API)
├── app.py           # HTTP interface — Flask routes only, no business logic
└── config.py        # Constants, environment variables, shared configuration
```
