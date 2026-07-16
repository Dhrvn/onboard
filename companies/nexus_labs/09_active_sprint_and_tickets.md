# Nexus Labs — Active Sprint & Ticket Examples
*Sprint 47 | April 14 – April 25, 2026 | Owner: Neha Krishnamurthy (Senior PM)*

---

## Sprint 47 Goal
"Ship Webhook v2 to staging, complete Dashboard redesign Phase 1, and resolve the top 3 lender-reported issues from Q1."

---

## SPRINT BOARD — CURRENT STATUS

### 🔴 In Progress

---

**NX-1847** | Story | High Priority
**Title:** Implement Webhook v2 — real-time decision push notifications

**Description:**
Currently, lenders poll our API every 30 seconds to check for new decisions on bulk submissions. This is inefficient and creates unnecessary load. Webhook v2 will push decision results to a lender-configured endpoint the moment a decision is made.

**Acceptance Criteria:**
- [ ] Lender can configure a webhook URL in the Dashboard (Settings → Webhooks)
- [ ] Webhook fires within 500ms of a decision being made
- [ ] Webhook payload includes full decision object (same format as v3/score response)
- [ ] Failed webhooks retry with exponential backoff (1s, 2s, 4s, 8s, max 5 retries)
- [ ] Failed webhooks after 5 retries create an alert in the lender's Dashboard
- [ ] Webhook secret signing implemented (HMAC-SHA256) so lenders can verify authenticity
- [ ] 99.9% delivery guarantee (store-and-forward if lender endpoint is temporarily down)

**Technical Notes:**
Use a Kafka topic `webhook.outbound` as the queue. Worker service picks up events and POSTs to lender URLs. Store state in Postgres table `webhook_delivery_log`. See design doc: Notion → Engineering → Design Docs → Webhook v2

**Assignee:** Aditya Sharma
**Sprint:** Sprint 47
**Story Points:** 13
**Linked tickets:** NX-1821 (design), NX-1848 (frontend config UI)

---

**NX-1848** | Story | High Priority
**Title:** Dashboard UI — Webhook configuration screen

**Description:**
Frontend work for NX-1847. Build the Settings → Webhooks screen where lenders can add, test, and remove webhook endpoints.

**Acceptance Criteria:**
- [ ] Lender can add up to 3 webhook URLs
- [ ] Each webhook has a label (e.g., "Production endpoint", "Staging endpoint")
- [ ] "Send test event" button fires a sample payload to the configured URL and shows success/failure
- [ ] Webhook signing secret is displayed once on creation and can be regenerated
- [ ] Delivery log tab shows last 100 webhook attempts with status (success/failed/retrying)
- [ ] Mobile responsive

**Assignee:** Tara Sundaram
**Sprint:** Sprint 47
**Story Points:** 8

---

**NX-1851** | Bug | Critical
**Title:** HDFC lender seeing incorrect approval rates in Dashboard — off by ~3%

**Description:**
HDFC's analytics team flagged that their Dashboard is showing 67.2% approval rate for March 2026, but their internal system shows 70.1%. Investigation needed.

**Steps to Reproduce:**
1. Log into Dashboard as HDFC_RETAIL_001
2. Navigate to Overview → Approval Rate → March 2026
3. Compare with the ground truth query:
```sql
SELECT
  COUNT(CASE WHEN decision = 'APPROVE' THEN 1 END) * 100.0 / COUNT(*) as approval_rate
FROM nexus_prod.decisions.credit_decisions
WHERE lender_id = 'HDFC_RETAIL_001'
  AND DATE_TRUNC('month', decision_time) = '2026-03-01'
```

**Root Cause Hypothesis:**
Dashboard may be including REFER decisions that were subsequently manually approved by HDFC in their count, but our system doesn't receive the final approval signal back. Or there's a timezone issue (Dashboard might be using UTC while HDFC uses IST).

**Impact:** HDFC has flagged this as a contractual issue — their SLA reporting uses our Dashboard numbers. If not fixed, it becomes a commercial dispute.

**Assignee:** Kabir Singh (investigation), Rahul Nambiar (fix)
**Sprint:** Sprint 47
**Story Points:** 5
**Priority:** Fix by April 23 — HDFC call scheduled

---

### 🟡 In Review (PR Raised, Awaiting Approval)

---

**NX-1839** | Story | Medium
**Title:** Add date range filter to Decision Explorer — default to last 7 days

**Description:**
Currently the Decision Explorer loads all-time data on page load, causing slowness. Add a date range picker defaulting to last 7 days.

**PR:** https://github.com/nexuslabs/nexus-dashboard/pull/892
**Reviewer:** Tara Sundaram
**Status:** 1/2 approvals received. Waiting on @nikhil.joshi.

**Assignee:** Nikhil Joshi → PR reviewed by Tara
**Story Points:** 3

---

**NX-1842** | Task | Medium
**Title:** Update SAP ingestor Lambda to handle HDFC's new file format (v3.1)

**Description:**
HDFC updated their SAP export format on April 1. New format adds 3 new columns and changes the date format from `DD/MM/YYYY` to ISO 8601 `YYYY-MM-DD`. Our Lambda validator is rejecting their files.

**Temporary Fix Applied:** Karan manually patched the Lambda on April 1 to accept both formats.
**Permanent Fix:** Update the schema validation config and add tests for both old and new format.

**PR:** https://github.com/nexuslabs/nexus-core/pull/1204
**Status:** Awaiting review from @priya.nair (data schema sign-off required)

**Assignee:** Sanya Malhotra
**Story Points:** 3

---

### ✅ Done This Sprint

---

**NX-1831** | Story | High
**Title:** SBI pilot — onboarding API configuration and rate limiting

**Completed:** April 15, 2026
**Summary:** Configured SBI's lender account with 50k decisions/month cap, set up their API key, customized their decision thresholds (SBI requested APPROVE only above 720), and added their IP range to the allowlist. Deployed and tested in staging on April 14, production on April 15. SBI made their first successful API call at 14:32 IST on April 15.

---

**NX-1833** | Bug | High
**Title:** Consent token expiry not returning clear error message

**Completed:** April 16, 2026
**Summary:** API was returning generic 422 error when consent token expired. Updated to return `NX_ERR_006` with clear message: "Consent token expired. Please re-obtain consent from the applicant." Updated error code documentation in API docs.

---

**NX-1836** | Task | Low
**Title:** Add p99 latency to Datadog dashboard

**Completed:** April 14, 2026
**Summary:** Added p99 latency metric alongside existing p50 and p95 metrics on the Production API Health dashboard. Also added a alert rule: PagerDuty page if p99 > 2000ms for 3 consecutive minutes.

---

## BACKLOG TICKETS (Next Sprint Candidates)

**NX-1855** | Story | Medium
**Title:** Bulk scoring API — score up to 10,000 applicants in a single request
**Description:** Lenders want to run portfolio monitoring (score their entire existing customer base periodically). Currently they'd have to make 10,000 individual API calls. Build an async batch endpoint: `POST /v3/score/batch` accepts array of applicants, returns a `job_id`, lender polls `GET /v3/score/batch/{job_id}` for results.
**Estimated Points:** 21 (large)
**Dependencies:** NX-1847 (Webhook v2) should be done first — batch results can be pushed via webhook

---

**NX-1857** | Story | High
**Title:** Explainability Report — auto-generate PDF for declined applicants
**Description:** RBI draft guidelines (expected Q3 2026) will require lenders to provide applicants with a written explanation of why they were declined. Build a PDF generator that takes a decision ID and produces a human-readable explanation using the risk factors from our model output.
**Estimated Points:** 13
**Stakeholder:** Meera Krishnan (compliance), Neha Krishnamurthy (product)

---

**NX-1860** | Bug | Medium
**Title:** Dashboard slow when querying >90 days of data
**Description:** Decision Explorer takes 8–12 seconds to load for 90+ day queries. Root cause: missing composite index on `(lender_id, decision_time)` in the decisions table. Fix: add the index and update the ORM query to use it.
**Estimated Points:** 3
**Note:** Quick win — grab this if you're looking for a starter ticket

---

**NX-1862** | Spike | Medium
**Title:** Research: WhatsApp usage as credit signal
**Description:** Dr. Vikram Bose wants to assess whether WhatsApp usage patterns (frequency, group participation, media sharing — all anonymized) could improve model Gini by the projected 8%. This spike should: review existing literature, assess data availability from our telco partners, and produce a 1-page recommendation on feasibility and privacy implications.
**Estimated Points:** 5 (research only)
**Assignee:** To be assigned (good first ticket for new ML team members)

---

## HOW TO PICK UP A TICKET

1. Find a ticket in the backlog that matches your skill level (ask your manager if unsure)
2. Comment on the Jira ticket: *"Picking this up"* and assign it to yourself
3. Create a branch: `git checkout -b feature/NX-XXXX-short-description`
4. When ready for review, open a PR and link it to the Jira ticket in the PR description
5. Move the Jira ticket to "In Review" when you raise the PR
6. Move to "Done" only after the PR is merged to main

**Good starter tickets for new joiners:**
- **NX-1860** (Dashboard slow query — quick, well-defined, 3 points)
- **NX-1862** (WhatsApp signal spike — research, good for ML new joiners)
- Any **P3/P4 bug** in the backlog — ask @aditya.sharma to point you to the current list
