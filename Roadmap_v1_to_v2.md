# WUIW Roadmap: v1.0 → v2.0

## Overview
The v1.0 → v2.0 arc has one centerpiece: the **weekly email digest**. The digest launches early in a simplified form and evolves into the full Sunday mailer — "what happened / what's coming" — once same-day Zoom summaries are online. Everything else is additive.

---

## v1.1 — Agenda Summaries (Town Council)
**Goal:** Extend the AI summary pipeline to cover Town Council agendas as well as minutes.

**Deliverables:**
- New document type: `agenda`
- Agenda-specific prompt template in `config_prompts.py`
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
- `broadcast.py` module — Buttondown adapter for digest sending and list management
- Weekly digest template: "What's coming this week" (TC agendas only)
- Digest send logic integrated with cron schedule
- Email signup UI updated to reflect live newsletter
- Unsubscribe and list management delegated to Buttondown

**Notes:**
- "What happened" section is intentionally absent until Zoom summaries are online
- This is a real, useful product — most residents don't know meetings are happening, let alone what's on the agenda
- Sponsors can come in at this milestone
- `broadcast.py` is a Buttondown adapter, not a full email engine — keep that boundary clean

**Definition of Done:**
- First digest sent to live subscriber list
- Buttondown handling list management and unsubscribes
- At least one weekly send proven stable

---

## v1.3 — Minutes Summaries: All AgendaCenter Bodies
**Goal:** Expand minutes summary coverage beyond Town Council to all bodies on AgendaCenter.

**Deliverables:**
- Identify all active AgendaCenter bodies (~20 total)
- Intake pipeline extended to ingest all bodies
- Minutes summaries generating and publishing for all bodies
- Frontend updated to support multi-body browsing

**Notes:**
- Some bodies meet rarely (twice a year) — pipeline should handle sparse activity gracefully
- Minutes and agenda pipelines are kept as separate milestones intentionally

**Definition of Done:**
- All AgendaCenter bodies producing minutes summaries
- No regressions in Town Council pipeline

---

## v1.4 — Agenda Summaries: All AgendaCenter Bodies
**Goal:** Extend agenda summary coverage to all AgendaCenter bodies.

**Deliverables:**
- Agenda summaries generating for all active bodies
- Frontend updated to show agenda previews across all bodies
- Digest updated to include higher-priority bodies beyond Town Council

**Definition of Done:**
- All AgendaCenter bodies producing both agenda and minutes summaries

---

## v1.5 — CivicPlus API Refactor + BOE Adapter
**Goal:** Replace RSS/HTML scraping with the CivicPlus API and add Windsor Board of Education as a new intake source.

**Deliverables:**
- Evaluate CivicPlus API access requirements (authentication, developer agreement)
- Refactor `intake.py` into an adapter architecture — each source gets its own adapter normalizing output into a shared schema
- CivicPlus adapter as primary intake mechanism replacing current scraper
- BOE adapter for Windsor Board of Education (separate platform, TBD)
- All existing bodies migrated to new adapter architecture

**Notes:**
- "Adapter by hosting platform" is the guiding architectural principle — one adapter covers many municipalities on the same platform
- CivicPlus is used by thousands of municipalities nationally — this adapter has scaling implications beyond Windsor
- BOE platform TBD — research required before scoping BOE adapter work
- See GitHub issue for open questions on CivicPlus API access

**Definition of Done:**
- CivicPlus API adapter live and stable
- BOE intake working via its own adapter
- No JSON file dependencies remaining
- All existing tests passing

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

## v1.9 — Full Digest Soft Launch
**Goal:** Prove the full digest format — "what happened / what's coming" — before public announcement.

**Deliverables:**
- Digest template updated: "What happened last week" (same-day summaries) + "What's coming this week" (agenda previews)
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
