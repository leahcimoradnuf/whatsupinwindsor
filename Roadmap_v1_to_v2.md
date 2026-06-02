# WUIW Roadmap: v1.0 → v2.0

## Overview
The v1.0 → v2.0 arc has one centerpiece: the **weekly email digest**. The digest launches early in a simplified form and evolves into the full Sunday mailer — "what happened / what's coming" — once same-day Zoom summaries are online. Everything else is additive.

---

## v1.1 — Agenda Summaries (Town Council)
**Goal:** Extend the AI summary pipeline to cover Town Council agendas as well as minutes.

**Deliverables:**
- New document type: `agenda`
- Agenda-specific prompt and few shots in database
- Summary schema extended to handle forward-looking content
- Agenda summaries rendered in Flask frontend

**Notes:**
- Agendas are sparse and forward-looking — prompt engineering will differ meaningfully from minutes summaries
- This milestone is the content dependency for the simplified digest

**Definition of Done:**
- Town Council agenda summaries publishing reliably alongside minutes summaries

---

## v1.2 — `broadcast.py` + Simplified Digest Launch
**Goal:** Launch the weekly email digest in simplified form — Town Council agenda previews only.

**Deliverables:**
- `broadcast.py` module — Buttondown adapter for digest drafting and scheduling sends
- Weekly digest template: "What's coming this week / What was published last week"
- Digest send logic integrated with cron schedule
- Email signup UI updated to reflect live newsletter
- Unsubscribe and list management delegated to Buttondown
- Email drafting function wired up to handle sponsor content, even if there aren't sponsors yet.

**Notes:**
- "It's Sunday, June 7th. Here's what's up in Windsor"
- This is a real, useful product — most residents don't know meetings are happening, let alone what's on the agenda
- Sponsors can come in at this milestone
- `broadcast.py` is a Buttondown adapter, not a full email engine — keep that boundary clean

**Definition of Done:**
- First digest sent to live subscriber list
- Buttondown handling list management and unsubscribes
- At least one weekly send proven stable

---

## v1.3 — Agenda & Minutes Summaries: All AgendaCenter Bodies
**Goal:** Expand summary coverage beyond Town Council to all bodies on AgendaCenter.

**Deliverables:**
- Identify all active AgendaCenter bodies (~20 total)
- Intake pipeline extended to ingest all bodies
- Agenda and Minutes summaries generating and publishing for all bodies
- Frontend updated to support multi-body browsing
- Backfill all bodies at least YTD
- Frontend updated to show agenda previews across all bodies
- Digest updated to include higher-priority bodies beyond Town Council

**Notes:**
- Some bodies meet rarely (twice a year) — pipeline should handle sparse activity gracefully
- Minutes and agenda pipelines are combined in this milestone since most of the Agenda work is covered in 1.1

**Definition of Done:**
- All AgendaCenter bodies producing agenda and minutes summaries
- No regressions in Town Council pipeline

---

## v1.4 — Intake Adapter Infrastructure
**Goal:** Build "Adapter by Hosting Platform" infrastructure

**Deliverables:**
- Refactor `intake.py` into an adapter architecture — each source gets its own adapter normalizing output into a shared schema
- All existing bodies migrated to new adapter architecture

**Notes**
- "Adapter by hosting platform" is the guiding architectural principle — one adapter covers many municipalities on the same platform
- Not a refactor to CivicPlus API yet, this lays the foundation for BOE content first.

**Definition of Done:**
- All existing bodies working via adapter structure

---

## v1.5 — BOE Adapter
**Goal:** Add Windsor Board of Education as a new intake source.

**Deliverables:**
- BOE adapter for Windsor Board of Education (BoardBook, scrape source code like backfill() does)

**Notes:**
- BOE platform: BoardBook — research required before scoping BOE adapter work. Will be similar to backfill()

**Definition of Done:**
- BOE intake working via its own adapter
- All existing tests passing

---

## v1.6 CivicPlus API Refactor
**Goal:** Replace RSS/HTML scraping with the CivicPlus API

**Deliverables:**
- Evaluate CivicPlus API access requirements (authentication, developer agreement)
- CivicPlus adapter as primary intake mechanism replacing current scraper

**Notes:**
- CivicPlus is used by thousands of municipalities nationally — this adapter has scaling implications beyond Windsor
- See GitHub issue for open questions on CivicPlus API access

**Definition of Done:**
- CivicPlus API adapter live and stable

---

## v1.7 — Zoom Bot / Same-Day Summaries
**Goal:** Add real-time meeting coverage via automated Zoom attendance and same-day transcript summarization.

**Deliverables:**
- `reporter.py` full implementation — interface with third-party Zoom recording bot (recall.ai)
- Transcript ingestion and summarization pipeline
- Same-day summary schema and storage
- Frontend updated to surface same-day summaries
- Admin oversight layer extended to cover same-day summaries

**Notes:**
- This is the most technically complex milestone in the roadmap
- Same-day summaries are the "what happened" content that powers the full digest vision
- Intentionally given breathing room before the full digest depends on it

**Definition of Done:**
- Same-day summaries publishing reliably for Town Council meetings
- Pipeline stable enough to extend to additional bodies

---

## v1.8 — Human in the Loop
**Goal:** Operator is able to tweak AI prompts without any coding

**Deliverables:**
- GUI in /admin route for viewing and editing system prompts and few shots
- "Add as example" button on editing panel to include good responses in the few-shot pool
- Rough display of input tokens for each prompt

**Notes:**
- Knowing the token count of each prompt will be very useful especially since Franchisees will be operating within a limit

**Definition of Done**
- Operator can add a few-shot example to the pool in minutes via GUI
- Operator can see how much of their input token alotment has been used.

---

## v1.9 — Full Digest Soft Launch
**Goal:** Prove the full digest format — "what happened / what's coming" — before public announcement.

**Deliverables:**
- Digest template updated: "What happened last week" (same-day summaries) + "What's coming this week" (agenda previews) + "Minutes archived last week" (detailed minutes summaries)
- Town Council and Board of Ed included
- Run for 4–6 weeks
- Stability confirmed, UX issues resolved

**Notes:**
- Mirrors v0.9 — proven stability before public announcement
- Sponsor placement reviewed and refined for full digest format

**Definition of Done:**
- Full digest sending weekly without gaps
- Trusted by operator
- Ready for public announcement

---

## v2.0 — Full Digest Public Launch
**Scope:**
- Town Council + Board of Education
- Weekly Sunday digest: "What happened / What's coming"
- Same-day Zoom summaries live
- Agenda and minutes summaries for all AgendaCenter bodies
- CivicPlus API powering intake
- All adapters stable

**Launch Actions:**
- Public announcement
- Sponsor outreach with full digest as the product
- Evaluate scaling model: hyperlocal media network vs. SaaS platform

**Definition of Done:**
- Full digest publicly announced and stable
- Scaling model decision made based on Windsor traction

---

## Guardrails (Not in v2.0)
- Per-body or per-topic notification preferences (post v2.0)
- Other CT towns
- State-level digest
- Search
- Comments
- JavaScript interactivity

---

**v2.0 is a product milestone. The digest is the product.**
