# Nexus Labs — Product Specification
*Version 3.2 | Last updated: April 2026 | Owner: Aryan Mehrotra (CPO)*

---

## Overview

Nexus Labs has two customer-facing products:

1. **Nexus Score API** — a REST API that banks and lenders call to get a real-time credit score for any applicant
2. **Nexus Dashboard** — a web application where lender partners monitor their decision volumes, model performance, and portfolio health

This document is the canonical reference for both products. Every PM, BA, engineer, and analyst should read this in Week 1.

---

# PRODUCT 1: NEXUS SCORE API

## What It Does

A lender (e.g., HDFC Bank) has an applicant who wants a loan. Instead of waiting 3–5 days for a traditional bureau check, the lender calls our API with basic applicant identifiers. Within 800ms, we return:

- A **Nexus Score** (0–1000, higher is better)
- A **Decision** (APPROVE / DECLINE / REFER)
- A **Reason code** explaining the decision
- A **Confidence interval** (how confident the model is)
- **Top 3 risk factors** (what drove the score up or down)

## API Endpoint

```
POST https://api.nexuslabs.com/v3/score
```

### Request Format

```json
{
  "request_id": "lender_req_20260422_001",
  "applicant": {
    "mobile": "+919876543210",
    "pan": "ABCDE1234F",
    "dob": "1992-07-15",
    "consent_token": "eyJhbGciOiJIUzI1NiJ9..."
  },
  "loan_context": {
    "loan_type": "personal_loan",
    "requested_amount_inr": 250000,
    "tenure_months": 24,
    "purpose": "home_improvement"
  },
  "lender_id": "HDFC_RETAIL_001"
}
```

### Response Format

```json
{
  "request_id": "lender_req_20260422_001",
  "nexus_score": 742,
  "score_band": "B",
  "decision": "APPROVE",
  "confidence": 0.89,
  "reason_code": "NX_AP_001",
  "reason_description": "Strong transaction consistency and positive repayment signals",
  "risk_factors": [
    {
      "factor": "transaction_velocity_30d",
      "direction": "positive",
      "contribution": 0.34,
      "description": "Above-average transaction frequency in last 30 days"
    },
    {
      "factor": "utility_payment_streak",
      "direction": "positive",
      "contribution": 0.28,
      "description": "12 consecutive months of on-time utility payments"
    },
    {
      "factor": "sap_balance_volatility",
      "direction": "negative",
      "contribution": -0.12,
      "description": "High variance in account balance over 90 days"
    }
  ],
  "model_version": "nexus_credit_v4.2",
  "processing_time_ms": 634,
  "timestamp": "2026-04-22T09:14:32.441Z",
  "data_sources_used": ["sap_transactions", "telco_usage", "utility_payments"],
  "consent_verified": true
}
```

### Score Bands and Default Decision Rules

| Score Range | Band | Default Decision | Description |
|---|---|---|---|
| 800–1000 | A | APPROVE | Excellent credit signals |
| 700–799 | B | APPROVE | Good credit signals |
| 600–699 | C | REFER | Mixed signals — lender manual review |
| 500–599 | D | REFER | Weak signals — lender manual review |
| 400–499 | E | DECLINE | Poor credit signals |
| 0–399 | F | DECLINE | Very poor or insufficient data |

*Note: Lenders can override default decision thresholds via their configuration settings in the Dashboard.*

### Error Codes

| Code | HTTP Status | Meaning | What To Do |
|---|---|---|---|
| `NX_ERR_001` | 400 | Invalid mobile number format | Check country code format |
| `NX_ERR_002` | 400 | PAN validation failed | Verify PAN format and checksum |
| `NX_ERR_003` | 401 | Invalid API key | Check `Authorization` header |
| `NX_ERR_004` | 402 | Insufficient credits | Lender needs to top up their credit balance |
| `NX_ERR_005` | 404 | Applicant not found | No data exists for this applicant in our system |
| `NX_ERR_006` | 422 | Consent token invalid or expired | Applicant must re-consent |
| `NX_ERR_007` | 429 | Rate limit exceeded | Max 100 requests/second per lender |
| `NX_ERR_500` | 500 | Internal server error | Page on-call immediately; SLA breach if not resolved in 15 min |
| `NX_ERR_503` | 503 | Service temporarily unavailable | Check status.nexuslabs.com |

### Authentication

All API calls require an `Authorization` header:
```
Authorization: Bearer <lender_api_key>
```

API keys are issued to lenders via the Dashboard. Keys are rotated every 90 days — lenders get a 14-day warning before expiry.

### Rate Limits

| Tier | Requests/Second | Requests/Day | Monthly Cost |
|---|---|---|---|
| Starter | 10 | 10,000 | ₹15,000 |
| Growth | 50 | 100,000 | ₹80,000 |
| Enterprise | 200 | 1,000,000 | Custom |
| Unlimited | Unlimited | Unlimited | Custom |

### SLA Commitments

| Metric | Commitment |
|---|---|
| API uptime | 99.95% monthly |
| p50 response time | < 400ms |
| p95 response time | < 800ms |
| p99 response time | < 1500ms |
| Incident response (P1) | 15 minutes |
| Data freshness | SAP data ≤ 24 hours old |

---

## Consent Framework

**This is critical for compliance.** We process sensitive financial and behavioral data. Every API call must include a valid `consent_token`.

### How consent works:
1. Before calling our API, the lender must show the applicant a consent screen (we provide the copy — see Compliance doc)
2. The applicant agrees → lender calls our Consent API
3. We return a `consent_token` (valid for 30 minutes)
4. Lender includes this token in the scoring request
5. We log the consent event with timestamp, IP, and applicant ID — this is our legal audit trail

### Consent API:
```
POST https://api.nexuslabs.com/v3/consent
{
  "mobile": "+919876543210",
  "lender_id": "HDFC_RETAIL_001",
  "consent_text_version": "v2.3",
  "applicant_ip": "203.0.113.45",
  "timestamp": "2026-04-22T09:14:00.000Z"
}
```

Response: `{ "consent_token": "eyJhbGc...", "expires_at": "2026-04-22T09:44:00.000Z" }`

---

# PRODUCT 2: NEXUS DASHBOARD

## What It Does

The Nexus Dashboard is a web app (React + TypeScript, hosted at dashboard.nexuslabs.com) where lender partners can:

- Monitor their daily/weekly/monthly decision volumes
- See approval rates, decline rates, and referral rates in real time
- Drill into individual decisions and see the score breakdown
- Configure their decision thresholds (override our defaults)
- Manage API keys and team access
- View their credit balance and top up
- Download compliance reports (required by RBI)
- See model performance metrics (PSI, Gini coefficient, KS statistic)

## Key Dashboard Screens

### 1. Overview / Home
- Today's decision count vs yesterday vs 7-day average
- Approval rate trend (last 30 days)
- Average score trend
- Top reason codes this week
- API health status (green/yellow/red)
- Credit balance remaining (with warning at 20% remaining)

### 2. Decision Explorer
- Searchable/filterable table of all decisions
- Filters: date range, decision type, score band, loan type
- Click any row to see full score breakdown (all risk factors, data sources used, processing time)
- Export to CSV

### 3. Model Performance
- **PSI (Population Stability Index):** Measures if the applicant population is shifting. Alert if PSI > 0.2
- **Gini Coefficient:** Model discrimination power. Our current model: 0.74 (industry benchmark: 0.65+)
- **KS Statistic:** Separation between good/bad borrowers. Current: 0.52
- **Score Distribution:** Histogram of scores by band, updated daily
- **Vintage Analysis:** How well our scores predicted actual repayment behavior over time

### 4. Configuration
- **Decision Thresholds:** Lender can set custom APPROVE/REFER/DECLINE cutoffs
  - Example: Conservative lender might set APPROVE only above 750 instead of our default 700
- **Loan Type Rules:** Different thresholds for different loan types (personal loan vs home loan vs credit card)
- **Webhook Settings:** Get notified via webhook when a decision is made
- **API Key Management:** Issue, rotate, or revoke API keys

### 5. Compliance Reports
- **Monthly Scorecard Report:** Required by RBI for all lenders using alternative data
- **Decision Audit Log:** Full audit trail for any regulatory enquiry
- **Consent Log:** Proof of consent for every decision made
- **Fairness Report:** Score distribution across demographic groups (gender, age band, geography) — ensures no discriminatory patterns

---

## Current Lender Partners

| Partner | Segment | Monthly Volume | Since |
|---|---|---|---|
| HDFC Bank (Retail) | Consumer lending | ~280,000 decisions/month | Jan 2023 |
| Axis Bank (Digital) | Personal loans | ~190,000 decisions/month | Jun 2023 |
| EarlySalary | NBFC — salary advances | ~420,000 decisions/month | Mar 2022 |
| KreditBee | NBFC — consumer credit | ~380,000 decisions/month | Aug 2022 |
| SBI (Pilot) | Consumer lending | ~50,000 decisions/month | Nov 2025 (pilot) |
| BankBazaar | Aggregator | ~120,000 decisions/month | Feb 2024 |

**Total: ~1.44 million decisions/month** (as of April 2026)

---

## Product Roadmap (Current Quarter — Q2 2026)

### In Progress
- **Nexus Score v5.0 model** — incorporating WhatsApp usage patterns as a new signal. Expected +8% Gini improvement. ETA: June 2026. Owner: Dr. Vikram Bose
- **Dashboard redesign** — moving from current UI to new design system. ETA: May 2026. Owner: Tara Sundaram
- **Webhook v2** — real-time push notifications for decisions, replacing current polling. ETA: May 2026. Owner: Aditya Sharma

### Backlog (Next Quarter)
- **Bulk scoring API** — score up to 10,000 applicants in a single batch request (for portfolio monitoring use cases)
- **Explainability Report PDF** — auto-generated PDF explaining why an applicant was declined (for lenders to share with applicants, as per upcoming RBI guidelines)
- **Singapore expansion** — adapt model for Singaporean data sources (different telco partners, no SAP)

### Recently Shipped (Q1 2026)
- ✅ **SBI pilot** — onboarded State Bank of India on a limited pilot (50k decisions/month cap)
- ✅ **Consent API v2** — added IP capture and version tracking for stronger audit trail
- ✅ **Metabase dashboards v3** — rebuilt all internal analytics dashboards
- ✅ **p99 latency improvement** — reduced from 2100ms to 1500ms through Redis caching optimization

---

## Known Issues & Limitations (Be Aware As A New Joiner)

1. **No real-time SAP data** — SAP data is batch (daily). This means our score for someone who just made a large transaction an hour ago won't reflect that transaction until tomorrow morning. Lenders are aware of this limitation.

2. **Thin-file problem** — ~15% of applicants we score have very limited data (new mobile users, recently moved to India, etc.). For these applicants, our confidence interval is wide and we almost always return REFER. We're working on a separate "thin-file model" for Q3 2026.

3. **Model drift in monsoon months** — historically, our model's PSI rises above 0.2 during June–September because spending patterns change significantly. We do a model refresh every August to correct for this. Watch the Model Performance dashboard during this period.

4. **Dashboard slow on large date ranges** — querying more than 90 days of data in the Decision Explorer causes noticeable slowness (8–12 seconds). Known issue, fix is in the backlog. Workaround: use smaller date ranges and export to CSV for large analyses.
