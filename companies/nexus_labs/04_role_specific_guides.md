# Nexus Labs — Role-Specific Onboarding Guides
*Last updated: April 2026*

---

# SOFTWARE ENGINEER — Your First 90 Days

## Your First Week Goals
By end of Week 1, you should:
- Have a working local development environment
- Have read and understood the architecture overview (Tech Stack doc)
- Have made your first (small) code contribution — even a docs fix counts
- Know who your go-to people are for infrastructure and data questions

## Week 1 Technical Setup (Step by Step)

### 1. Clone the main repo
```bash
git clone https://github.com/nexuslabs/nexus-core
cd nexus-core
```

### 2. Set up your local environment
```bash
# We use Python 3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up environment variables
Copy the sample env file and fill in values (ask your tech lead for secrets):
```bash
cp .env.example .env
```

### 4. Run the app locally
```bash
uvicorn main:app --reload
```
API will be running at `http://localhost:8000`
API docs at `http://localhost:8000/docs` (Swagger UI — explore this!)

### 5. Run tests
```bash
pytest tests/
```
All tests should pass on a fresh clone. If they don't, ping @aditya.sharma immediately.

---

## Your First 30 Days — What Good Looks Like

- Shipped at least 2 PRs (can be small — bug fixes, test additions, docs)
- Can explain the end-to-end credit scoring flow to someone else
- Attended all sprint ceremonies and starting to contribute in planning
- Have a clear picture of what your first "real" feature will be

## Days 30–60

- Owning at least 1 feature end-to-end
- Have done at least 1 code review for a teammate
- Understand the monitoring setup (CloudWatch, Datadog)
- Have been added to the on-call rotation (read-only observer first)

## Days 60–90

- Have shipped a feature to production (with support)
- Can handle a P2 incident independently
- Have given feedback in at least 1 retrospective
- Have a clear 6-month goal discussed with your manager

---

## Key Things Engineers Get Wrong in Week 1

1. **Testing against prod** — don't. Always use staging.
2. **Committing secrets** — run `git diff` before committing. We have pre-commit hooks but don't rely on them.
3. **Going silent when stuck** — if you're stuck for more than 2 hours, ask for help. No one judges.
4. **Skipping code reviews** — every PR needs a review. Don't merge your own PRs.
5. **Not writing tests** — our test coverage requirement is 80%. PRs without tests will be sent back.

---

## Useful Commands You'll Use Daily

```bash
# Start local server
uvicorn main:app --reload

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_scoring_engine.py

# Check code style
flake8 .

# Format code
black .

# Check what's in staging
kubectl get pods -n staging

# View logs for a service
kubectl logs -n staging deployment/scoring-api --tail=100
```

---
---

# DATA ANALYST — Your First 90 Days

## Your Role at Nexus Labs

As a Data Analyst, you sit at the intersection of data engineering and product/business. Your job is to:
- Answer business questions with data ("How many credit decisions did we make in March?")
- Build and maintain dashboards in Metabase
- Monitor data quality and flag anomalies
- Support the ML team with feature analysis
- Help product managers with experiment analysis (A/B tests)

## Your Primary Tools

| Tool | What you'll use it for | How to get access |
|---|---|---|
| **Snowflake** | All your SQL queries | Request from @priya.nair |
| **Metabase** | Building dashboards and reports | Self-signup with company email |
| **Airflow** | Monitoring data pipelines (view only) | VPN + ask @karan.mehta |
| **Jupyter Notebooks** | Ad-hoc Python analysis | Set up locally (guide below) |
| **GitHub** | Version-controlling your SQL and notebooks | Ask your tech lead |

## Week 1 Setup

### 1. Get Snowflake access
Ping @priya.nair on Slack. She'll create your account with read access to:
- `nexus_prod.sap` — SAP transaction data
- `nexus_prod.telco` — Telco/mobile data
- `nexus_prod.decisions` — Credit decisions made by our engine
- `nexus_prod.customers` — Anonymized customer profiles

### 2. Set up Python locally
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install pandas numpy matplotlib seaborn jupyter snowflake-connector-python
jupyter notebook
```

### 3. Connect Python to Snowflake
```python
import snowflake.connector

conn = snowflake.connector.connect(
    user='your_username',       # from Priya
    password='your_password',   # from Priya
    account='nexuslabs',
    warehouse='ANALYST_WH',
    database='NEXUS_PROD',
    schema='SAP'
)

# Test it
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM transactions LIMIT 10")
print(cursor.fetchall())
```

### 4. Key Snowflake tables to know

| Table | What's in it | Refreshed |
|---|---|---|
| `nexus_prod.sap.transactions` | Daily SAP bank transaction data | Daily 7am |
| `nexus_prod.decisions.credit_decisions` | Every credit decision we've made | Real-time |
| `nexus_prod.decisions.model_scores` | Raw model scores before decision | Real-time |
| `nexus_prod.customers.profiles` | Anonymized customer profiles | Daily |
| `nexus_prod.telco.usage_features` | Telco-derived features | Daily |
| `nexus_prod.dq.daily_report` | Data quality metrics by source | Daily 7am |

---

## Your First 30 Days — What Good Looks Like

- Can write SQL queries independently in Snowflake
- Have built at least 1 dashboard in Metabase
- Understand the data model (can explain what's in each key table)
- Have answered at least 1 real business question for a PM or manager

## Days 30–60

- Own a recurring report (weekly/monthly business metrics)
- Have done an ad-hoc analysis that influenced a product or business decision
- Understand the full data pipeline (where data comes from, how it's transformed)

## Days 60–90

- Have proposed and built a new dashboard from scratch
- Can identify and escalate data quality issues independently
- Starting to support ML team with feature analysis

---

## Common Analyst Questions (and Answers)

**Q: Where do I find yesterday's credit decision volume?**
```sql
SELECT DATE(decision_time), COUNT(*) as decisions
FROM nexus_prod.decisions.credit_decisions
WHERE decision_time >= DATEADD(day, -7, CURRENT_DATE)
GROUP BY 1
ORDER BY 1 DESC;
```

**Q: How do I check if the SAP data for today has arrived?**
```sql
SELECT MAX(transaction_date), COUNT(*)
FROM nexus_prod.sap.transactions
WHERE ingestion_date = CURRENT_DATE;
```
If this returns 0 rows, the SAP pipeline may have failed. Check #data-ops on Slack.

**Q: How do I request a new Metabase dashboard to be shared with a team?**
Build it yourself, then share the link in the relevant Slack channel and tag the team.

---
---

# BUSINESS ANALYST — Your First 90 Days

## Your Role at Nexus Labs

As a BA at Nexus Labs, you work primarily with the Product and Operations teams. Your job is to:
- Translate business requirements into clear specs for engineering and data teams
- Analyze product performance and identify improvement areas
- Support lender/partner onboarding (helping bank partners integrate our API)
- Document processes and maintain our Notion wiki
- Run competitor and market analysis

## Your Primary Tools

| Tool | What you'll use it for |
|---|---|
| **Notion** | Writing specs, documenting processes, maintaining wiki |
| **Jira** | Creating and managing tickets, tracking project progress |
| **Metabase** | Self-serve data analysis (no SQL required for basic queries) |
| **Google Slides / Docs** | Presentations and reports for leadership |
| **Miro** | Process mapping, user journey diagrams |

## Week 1 — What To Focus On

Unlike engineers who need technical setup, your Week 1 is about **context absorption**:

1. **Read every doc in this Notion space** — especially the product specs for our two main products (Nexus Score API and Nexus Dashboard)
2. **Shadow 3 customer calls** — ask Neha Krishnamurthy (@neha.krishnamurthy) to add you to upcoming bank partner calls
3. **Map the end-to-end user journey** — draw (in Miro) how a bank goes from signing up to getting their first credit score from us
4. **Meet everyone in Product and Ops** — your job requires trust across teams, build it early

## Your First 30 Days — What Good Looks Like

- Have written at least 1 Product Requirements Document (PRD) or spec, even a small one
- Can explain Nexus Labs' core products and business model to an outsider
- Have sat in on at least 2 bank partner calls
- Have mapped at least one internal process that wasn't documented before

## How To Write a PRD at Nexus Labs

Every feature spec should include:
1. **Problem statement** — what user problem are we solving?
2. **Success metrics** — how will we know it worked? (be specific: "reduce lender onboarding time from 5 days to 2 days")
3. **User stories** — "As a [user], I want to [action] so that [outcome]"
4. **Scope** — what's in and what's explicitly out of scope
5. **Dependencies** — which teams need to be involved?
6. **Open questions** — what do we still need to figure out?

Use the PRD template in Notion: `Product → Templates → PRD Template`

## Days 30–60

- Own a project from spec to delivery (working with engineering)
- Have presented findings or a recommendation to at least one senior stakeholder
- Started building relationships with 2–3 bank partner contacts

## Days 60–90

- Have a project you shipped that you can point to
- Starting to proactively identify problems, not just react to requests
- Have contributed to or improved at least one Notion documentation page

---

## Working With Engineering as a BA

Tips from the team:
- **Be specific in your tickets.** Vague requirements cause delays. "Make the dashboard better" is not a ticket. "Add a filter for date range on the decisions table, defaulting to last 7 days" is a ticket.
- **Always include acceptance criteria.** How will the engineer know when it's done?
- **Respect the sprint.** Don't add urgent requests mid-sprint without talking to the PM first.
- **Join sprint planning.** You don't have to attend every standup but you should be in planning.
- **Don't go directly to engineers for estimates.** Route through the PM.
