# WUIW Roadmap: v0.1 → v1.0 (Launch-Ready MVP)

## MVP Definition
- Only Town Council
- Only published meeting minute summaries
- No agenda parsing
- No same-day Zoom summaries
- Minimal HTML/CSS (static site, no JavaScript)
- PostgreSQL database (no JSON database)
- Town IT aware (not formal alignment)
- Deployed to .com domain

---

## v0.1 — Stabilize Scraper
**Goal:** Reliable ingestion of Town Council meeting minutes.

**Deliverables:**
- Fix or rewrite scraper
- Hardcode Town Council source URL
- Extract:
  - Meeting date
  - Title
  - URL to official minutes
  - Publish date (if available)
- Store in JSON (temporary)
- Add logging and basic error handling
- Idempotent ingestion (no duplicates)

**Definition of Done:**
- Cron runs daily without crashing
- Running twice does not duplicate entries
- Can backfill last 12 months successfully

---

## v0.2 — Clean Summary Layer
**Goal:** Establish AI summary output format.

**Deliverables:**
- Create standardized summary schema:
  - id
  - meeting_date
  - published_date
  - official_url
  - summary_text
- Write 3–5 test summaries (AI-generated)
- Store summary text in JSON
- Add simple HTML rendering in Flask

**Definition of Done:**
- Site shows chronological list of meetings
- Each meeting displays:
  - Date
  - Link to official minutes
  - Generated summary

---

## v0.3 — PostgreSQL Migration
**Goal:** Replace JSON file with database.

**Deliverables:**
- Install PostgreSQL locally
- Create table:

meetings (
  id SERIAL PRIMARY KEY,
  meeting_date DATE NOT NULL,
  published_date DATE,
  official_url TEXT UNIQUE NOT NULL,
  summary_text TEXT,
  is_published BOOLEAN DEFAULT false,
  ai_generated BOOLEAN DEFAULT true,
  manually_edited BOOLEAN DEFAULT false,
  last_reviewed_at TIMESTAMP,
  correction_note TEXT,
  created_at TIMESTAMP DEFAULT NOW()
)

- Replace JSON reads/writes with DB queries
- Add UNIQUE constraint on official_url
- Update ingestion script to write to DB

**Definition of Done:**
- Full ingestion works using PostgreSQL
- No JSON dependency
- DB-backed version runs locally

---

## v0.4 — Production Deployment
**Goal:** Live database-backed version running on domain.

**Deliverables:**
- Provision PostgreSQL in production
- Configure environment variables
- Deploy updated Flask app
- Confirm:
  - Cron runs in production
  - DB writes successfully
  - Website reflects new entries

**Definition of Done:**
- Domain shows live Town Council summaries
- Scraper runs automatically
- Zero manual intervention required

---

## v0.5 — Minimalist Public UI Pass
**Goal:** Civic, calm interface.

**Deliverables:**
- Single column layout
- Chronological list view
- Individual meeting page
- About page explaining:
  - Scope (Town Council only)
  - Automated nature of summaries
  - Link to official minutes
- Simple typography
- Mobile responsive via CSS only

**Definition of Done:**
- Clean on phone
- Loads fast
- No visual clutter
- Feels trustworthy

---

## v0.6 — Data Integrity + Audit Confidence
**Goal:** Operational credibility.

**Deliverables:**
- Create scraper_runs table:

scraper_runs (
  id SERIAL PRIMARY KEY,
  run_started_at TIMESTAMP,
  run_completed_at TIMESTAMP,
  status TEXT,
  new_records_found INT,
  error_message TEXT
)

- Log all scraper runs
- Implement exponential backoff on errors
- Basic failure alert (email)
- Log outgoing requests

**Definition of Done:**
- System does not silently fail
- Scraper activity is auditable

---

## v0.6.5 — Responsible Development Signaling
**Goal:** Be transparent during active development.

**Deliverables:**
- Custom User-Agent header:
  - WUIW Civic Summary Bot (DEV) +yourdomain.com/contact
- Respect robots.txt
- Space requests conservatively
- Implement local HTML caching for parser testing
- Send brief courtesy notice to Town IT explaining:
  - Development phase testing
  - Temporary higher request frequency
  - Production plan (once daily)

**Definition of Done:**
- IT aware of development activity
- Scraper clearly identifiable
- Development traffic controlled and documented

---

## v0.7 — Administrative Oversight Layer
**Goal:** Supervised automation (not full manual editorial workflow).

**Deliverables:**
- Admin login route
- Meeting list view (admin)
- Edit summary interface (textarea)
- Publish toggle
- Manual edit tracking (manually_edited flag)
- Weekly spot-audit process defined
- "Report an error" submission mechanism (email or DB table)

**Definition of Done:**
- Any summary can be corrected in under 2 minutes
- Public can report factual errors
- No need for full manual review of every meeting

---

## v0.8 — Documentation & Civic Transparency Package
**Goal:** Documentation that builds trust and transparency 

**Deliverables:**
- technical documentation of system behavior
- civic one-pager explaining the app in plain English, to be shared with town officials.


**Definition of Done:**
- technical docs live and hosted
- civic one-pager saved as printable pdf doc

---

# v0.9 — Soft Launch (Quiet)

## Goal
Prove stability while preparing for public launch.

---

## Deliverables
- Run system for 4–6 weeks
- Publish summaries consistently
- Zero downtime
- Fix small UX issues
- Tighten About language
- Send "Letter from the Editor" to subscriber list
- Draft franchise playbook document
- Send courtesy notice to town clerk (with Windsor IT cc'd) announcing intent to make public comment at upcoming Town Council meeting

---

## Notes
- v0.9 is intentionally a waiting and watching milestone — the system runs, you observe, you fix small things
- The subscriber email and franchise playbook are parallel work that productively fill the stability watching period
- The town clerk notice is time sensitive — it must go out during v0.9 so there is no surprise at the v1.0 announcement
- "Letter from the Editor" warms the subscriber base before the public announcement — by v1.0 they are informed insiders, not cold audience members

---

## Definition of Done
- System stable and consistent for 4–6 weeks
- Trusted by operator
- Subscribers have heard from you personally via Letter from the Editor
- Town clerk is aware of upcoming public announcement
- Franchise playbook first draft exists

---

## v1.0 — Public MVP Launch
**Scope:**
- Town Council only
- Published minutes only
- Clean AI summaries
- PostgreSQL-backed
- Minimal HTML/CSS
- IT aware

**Launch Requirements:**
- Remove (DEV) from User-Agent
- Production User-Agent:
  - WUIW Civic Summary Bot +yourdomain.com/contact
- Scraper runs once daily
- robots.txt honored
- Courtesy follow-up note to IT: now live, daily schedule

**Launch Actions:**
- Announce publicly
- Share with local weekly paper
- Share with civic groups
- Add voluntary support link (carefully framed)

**Definition of Done:**
- Publicly accessible
- Stable
- Clear scope
- Unmistakably well-behaved scraper
- No feature creep

---

## Guardrails (Not in v1)
- Other bodies
- Agenda parsing
- Real-time summaries
- Search
- Comments
- Email list
- Metrics dashboards
- JavaScript interactivity
- Ads

---

**v1.0 is a credibility milestone, not a feature milestone.**

