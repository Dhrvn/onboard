# Nexus Labs — Tech Stack & Data Infrastructure
*Last updated: April 2026 | Owner: Karan Mehta (DevOps Lead)*

---

## Overview

Nexus Labs runs a real-time credit scoring pipeline. At its core, we ingest data from multiple sources (SAP, banking partners, telcos), enrich it, run it through ML models, and return a credit score + decision within 800ms.

This document covers our full technical architecture. Every engineer and data analyst should read this in Week 1.

---

## Architecture Overview

```
External Data Sources
    │
    ▼
Ingestion Layer (Kafka + custom connectors)
    │
    ▼
Raw Data Lake (AWS S3)
    │
    ▼
Transformation Layer (Apache Spark on EMR)
    │
    ▼
Feature Store (Redis + Snowflake)
    │
    ▼
ML Inference Layer (FastAPI + SageMaker)
    │
    ▼
Decision Engine (Python microservice)
    │
    ▼
Response to Bank/Lender (REST API, <800ms)
```

---

## SAP Data Ingestion — Full Walkthrough

This is one of the most common questions from new joiners, so here is a detailed explanation.

### What is SAP in our context?
Several of our banking partners (HDFC, Axis, SBI) use SAP S/4HANA for their core banking operations. We receive batch exports of anonymized transaction data from these banks every day. This data feeds our credit models.

### How the daily SAP ingestion works:

**Step 1 — Bank generates export (11pm IST)**
The bank's SAP system runs an automated job at 11pm every night. It exports the previous day's transaction records in a compressed CSV format and drops them to a shared **AWS S3 bucket** (one per bank partner, access controlled via IAM roles).

**Step 2 — S3 Event triggers ingestion (11pm–12am IST)**
When a new file lands in the S3 bucket, an **S3 Event Notification** fires. This triggers an **AWS Lambda function** (`nexus-sap-ingestor`) which does the following:
- Validates the file checksum (to ensure no corruption)
- Checks the file schema matches expected format
- Moves the file to our **raw data lake** at `s3://nexus-raw-data/sap/{bank_name}/{date}/`
- Publishes a message to a **Kafka topic** called `raw.sap.transactions`

**Step 3 — Spark job processes the data (12am–3am IST)**
An Apache Spark job running on **AWS EMR** consumes from the Kafka topic. It:
- Decrypts the data (all data is AES-256 encrypted at rest)
- Applies schema validation and data quality checks
- Enriches transactions with internal customer identifiers
- Computes derived features (average transaction value, spending velocity, etc.)
- Writes clean data to **Snowflake** (our data warehouse) in the `sap_transactions` table
- Writes feature vectors to our **Redis feature store** for real-time model serving

**Step 4 — Data quality report (6am IST)**
An automated Airflow DAG called `sap_dq_report` runs at 6am. It:
- Checks row counts vs expected volumes
- Checks for nulls/anomalies in key fields
- Sends a Slack message to `#data-ops` with a green/red status
- If red, pages the on-call data engineer via PagerDuty

**Step 5 — Available for use (by 7am IST)**
By 7am, the previous day's SAP data is available in:
- Snowflake: `nexus_prod.sap.transactions` (for analytics)
- Redis: Feature store keys prefixed `sap_feat:` (for real-time scoring)

### Common issues and how to handle them:

| Issue | What it looks like | What to do |
|---|---|---|
| File doesn't arrive by midnight | `#data-ops` alert: "SAP file missing for HDFC" | Check Slack #data-ops. Ping Priya Nair |
| Schema mismatch | Lambda logs show validation error | Check CloudWatch logs for `nexus-sap-ingestor`. Ping Karan Mehta |
| Spark job fails | Airflow shows red DAG | Check Airflow UI at airflow.nexuslabs.internal. Ping on-call engineer |
| DQ report is red | Slack alert in #data-ops | Do NOT use that day's data for model retraining. Escalate to Priya Nair |

### Who owns this pipeline?
- **Overall ownership:** Priya Nair (Data Engineering Lead)
- **Infrastructure:** Karan Mehta (DevOps)
- **On-call rotation:** Data team rotates weekly. Check #data-ops pinned message for current on-call

---

## Other Data Sources

### Telco Data (Jio, Airtel)
- **Frequency:** Real-time via API calls
- **What we get:** App usage patterns, recharge history (anonymized)
- **How:** REST API with OAuth2, credentials in AWS Secrets Manager
- **Owner:** Arjun Patel (Data Engineer)

### Utility Payment Data
- **Frequency:** Weekly batch (every Sunday 2am)
- **What we get:** Electricity, gas, water bill payment history
- **How:** SFTP from 3 utility aggregators, ingested via Airflow DAG `utility_weekly_ingest`
- **Owner:** Priya Nair

### Internal Transaction Data
- **Frequency:** Real-time streaming
- **What we get:** In-app transaction events from our own lending product
- **How:** Kafka topic `prod.transactions`, published by our lending microservice
- **Owner:** Engineering team

---

## Language & Frameworks

| Area | Technology | Version | Notes |
|---|---|---|---|
| Backend APIs | Python + FastAPI | 3.11 / 0.110 | All microservices |
| Data Processing | Apache Spark (PySpark) | 3.5 | Runs on AWS EMR |
| ML Models | Python + scikit-learn, XGBoost | Latest | Deployed on SageMaker |
| ML Ops | MLflow | 2.x | Model registry + experiment tracking |
| Orchestration | Apache Airflow | 2.8 | At airflow.nexuslabs.internal |
| Streaming | Apache Kafka | 3.x | Managed via AWS MSK |
| Frontend | React + TypeScript | 18 / 5 | Internal dashboard only |
| Infrastructure | Terraform | 1.7 | All infra as code |
| Containers | Docker + Kubernetes (EKS) | — | All services containerized |

---

## Environments

| Environment | Purpose | URL Pattern | Who can deploy |
|---|---|---|---|
| `dev` | Local development | localhost / dev.nexuslabs.internal | Everyone |
| `staging` | Pre-production testing | staging.nexuslabs.internal | Engineers (auto-deploy on merge to `main`) |
| `prod` | Live production | api.nexuslabs.com | Senior engineers + DevOps only |

**Never test against production data.** Staging has a full anonymized copy of prod data refreshed weekly.

---

## Git & Deployment Workflow

### Branch strategy
```
main (protected) ← staging auto-deploys from here
  ↑
feature/your-feature-name  ← you work here
```

### How to ship code:
1. Create a branch from `main`: `git checkout -b feature/your-feature-name`
2. Write code, commit with clear messages
3. Open a Pull Request on GitHub against `main`
4. Get **at least 1 approval** from a team member (2 approvals for data pipeline changes)
5. All CI checks must pass (tests + linting via GitHub Actions)
6. Merge to `main` → auto-deploys to staging within 10 minutes
7. Test on staging
8. For prod deploy: create a release tag → Karan Mehta or a senior engineer deploys

### Commit message format
```
[type]: short description

Types: feat, fix, data, infra, docs, test
Example: feat: add SAP schema validation for HDFC format
```

---

## Monitoring & Alerting

| Tool | What it monitors | Access |
|---|---|---|
| **CloudWatch** | AWS infrastructure, Lambda logs | AWS console |
| **Datadog** | Application performance, API latency | datadog.nexuslabs.internal |
| **Airflow UI** | Data pipeline DAG runs | airflow.nexuslabs.internal |
| **PagerDuty** | On-call alerting | Ask Karan for access |
| **Metabase** | Business metrics, data quality dashboards | metabase.nexuslabs.internal |

**P1 incidents** (production down): Page on-call immediately via PagerDuty
**P2 incidents** (degraded performance): Post in #incidents on Slack
**P3** (non-urgent issues): Create a Jira ticket

---

## Security Rules (Non-Negotiable)

1. **Never commit credentials or API keys** to GitHub. Use AWS Secrets Manager or `.env` files (which are in `.gitignore`)
2. **Never access production data directly** without manager approval and audit log
3. **All data at rest is AES-256 encrypted.** Do not store raw PII on your local machine
4. **MFA is mandatory** on all accounts (GitHub, AWS, Google Workspace)
5. **VPN required** to access internal tools (airflow, metabase, datadog). VPN setup: ask Riya Sharma

---

## New Engineer Setup Checklist

- [ ] Get GitHub access from your tech lead
- [ ] Clone the main repo: `git clone https://github.com/nexuslabs/nexus-core`
- [ ] Set up local dev environment (follow `README.md` in the repo)
- [ ] Get AWS read-only access from Karan Mehta
- [ ] Get Snowflake read access from Priya Nair
- [ ] Install VPN (WireGuard) — config file from Riya Sharma
- [ ] Set up MFA on all accounts
- [ ] Join Slack channels: `#engineering`, `#data-ops`, `#deployments`, `#incidents`
- [ ] Attend your first sprint planning (ask manager for calendar invite)
