# Nexus Labs — New Joiner FAQ
*Compiled from 3 years of onboarding feedback | Last updated: April 2026 | Owner: Ananya Iyer*

---

> This document contains the 30 most frequently asked questions from new joiners in their first 90 days. If your question isn't here, ask in #ask-anything on Slack — and we'll add it here.

---

## SECTION 1 — DAY 1 LOGISTICS

**Q1: I haven't received my laptop yet. What do I do?**
Ping @riya.sharma on Slack immediately. Laptops are prepared 2 days before your start date. If it hasn't arrived by 11am on Day 1, Riya will arrange a loaner. Don't wait — reach out proactively.

**Q2: What are my login credentials for Gmail, Slack, and Keka?**
All credentials are sent to your personal email address the evening before your start date from onboarding@nexuslabs.com. Check your spam folder first. If you can't find them, ping @riya.sharma or @ananya.iyer. Your default password will be `NexusYYYY@<last4ofphone>` — you'll be forced to change it on first login.

**Q3: Do I need to come to the office on Day 1?**
Yes, for Mumbai and Bangalore joiners. Day 1 orientation is in-person at the respective office. The orientation starts at 10am sharp. Bring your original ID proof (Aadhaar/Passport) for document verification. Singapore joiners attend virtually.

**Q4: What should I wear?**
We're smart casual. Jeans and a clean t-shirt is fine. You'll rarely see a suit here. On client visit days, business casual is expected — your manager will let you know in advance.

**Q5: I don't know anyone yet. How do I figure out who to talk to?**
Your buddy will reach out to you on Slack before noon on Day 1. They're your go-to for everything social and "dumb questions." Also check the Org Structure doc — it has everyone's Slack handles. Don't hesitate to cold-DM anyone. People here respond warmly to new joiners reaching out.

---

## SECTION 2 — TOOLS & ACCESS

**Q6: How long does it take to get all my tool access set up?**
Most access (Gmail, Slack, Keka, Jira, Metabase) is ready on Day 1. GitHub access takes 1–2 days — your tech lead handles this. AWS and Snowflake access takes 2–3 days because they require manager confirmation. VPN setup usually happens on Day 2. If anything is delayed beyond these timelines, ping @riya.sharma.

**Q7: I need access to a tool that isn't in the standard list. How do I request it?**
1. Check with your manager that you actually need it
2. Ping @riya.sharma on Slack: *"Hi Riya, I need access to [tool name] for [reason]. My manager [name] has approved."*
3. For paid tools/subscriptions, you'll also need to follow the PO process (see Processes doc)
4. Most access requests are resolved within 2 business days

**Q8: I'm locked out of my account. What do I do?**
For Google/Gmail: use the "Forgot password" flow with your company email. For Slack, Keka, or any internal tool: ping @riya.sharma on WhatsApp (+91 98XXX XXXXX — she'll share it on Day 1) since you won't have Slack access. For AWS: ping @karan.mehta.

**Q9: Do I need the VPN all the time?**
Only to access internal tools: Airflow, Metabase, Datadog, Jira, and the internal Notion workspace. Gmail, Slack, GitHub, and Keka work without VPN. Install WireGuard (config file from @riya.sharma) and only activate it when accessing internal tools. Keep it off otherwise — it slows your connection.

**Q10: I accidentally committed a secret/API key to GitHub. What do I do?**
Don't panic, but act immediately:
1. Message @karan.mehta and @aditya.sharma on Slack RIGHT NOW — don't wait
2. Do NOT try to delete the commit yourself — that often makes it worse
3. The secret needs to be rotated (invalidated and replaced) within the hour
4. Karan will handle the GitHub side; you handle rotating the credential
5. This happens to everyone at least once. We won't judge — but we need to know fast.

---

## SECTION 3 — WORKING NORMS

**Q11: When am I expected to be online/reachable?**
Core hours are 11am–4pm IST, Monday to Friday. During these hours, respond to Slack messages within 30 minutes. Outside core hours, respond within a few hours if you're working. If you're offline for the day, set your Slack status accordingly. We don't expect 24/7 availability — but we do expect you to be reachable during core hours.

**Q12: How quickly should I respond to Slack messages?**
During core hours: within 30 minutes for direct messages, within a few hours for channel messages. If something is urgent, people will call you or use @here/@channel. If a message can wait, it will. Don't feel pressure to respond instantly to every notification — batch your Slack time.

**Q13: How do meetings work here? Do I just show up to all calendar invites?**
If you're invited, you're expected to attend unless you decline with a reason. Declining is totally acceptable — just do it explicitly rather than ghosting. For recurring meetings (standups, sprint ceremonies), attend unless you have a conflict and notify the facilitator. "Optional" meetings in the invite are genuinely optional.

**Q14: I disagree with something my manager or team has decided. What should I do?**
Raise it. We mean it when we say "radical transparency." The expected behavior is: raise your concern once clearly and specifically, in the relevant meeting or in a 1:1. If you're overruled, commit fully ("disagree and commit"). Don't slow-walk decisions you disagree with. If you feel your concern wasn't heard, escalate to your skip-level — that's what they're there for.

**Q15: How does remote work actually work here? Is it really flexible?**
Yes, genuinely. Up to 3 days/week remote, no approval needed — just block your calendar and set your Slack status to "WFH." For full remote weeks (up to 4/year), notify your manager at least a week in advance. The only requirement is that you're fully present and reachable during core hours regardless of where you are. Nobody is checking whether you're at a desk.

---

## SECTION 4 — MONEY & HR

**Q16: When do I get paid and how do I see my payslip?**
Salary is credited on the last working day of every month. Payslips are available on Keka → Payroll → My Payslips. Your first payslip will show a prorated amount if you joined mid-month. If you don't see your payslip by the 2nd of the following month, ping @ananya.iyer.

**Q17: How do I claim an expense for a work lunch/Uber?**
Open Keka → My Actions → Expense Claims → New Expense Claim. Select category, enter amount, add description (e.g., "Uber to Axis Bank client meeting, 14 Apr"), upload receipt photo. Submit. Your manager gets notified to approve. Reimbursement arrives in the next payroll cycle or within 15 working days of approval. Keep all receipts — no receipt, no reimbursement for amounts above ₹500.

**Q18: I need to buy a software tool for my work. How do I get it approved?**
Under ₹5,000: Buy it, expense it on Keka, attach receipt — no pre-approval needed.
₹5,000–₹50,000: Fill out Purchase Request on Notion (Finance → Purchase Requests), get manager approval, tag @vikram.desai. Allow 3 business days.
Above ₹50,000: Same process + CFO approval + 3 vendor quotes. Allow 5–7 business days.
**Important:** Don't buy first and ask later for anything above ₹5,000.

**Q19: When can I start taking leaves? Is there a waiting period?**
No waiting period. You can apply for leave from Day 1. However, taking leave in your first 2 weeks (outside genuine emergencies) is strongly discouraged — use that time to onboard. Apply on Keka at least 3 days in advance for PL/CL. For sick leave, inform your manager on Slack the same morning — no advance notice required.

**Q20: What's the notice period if I want to leave?**
During probation (first 6 months): 2 weeks. After probation: 2 months. This is a real 2-month notice — we will ask you to serve it. If you need to negotiate a shorter period, discuss with @ananya.iyer — it's handled case by case.

---

## SECTION 5 — TECHNICAL (ENGINEERING & DATA)

**Q21: The SAP data for today seems off / the numbers don't match what I expect. What do I do?**
1. First check #data-ops on Slack — there may already be an alert about it
2. Check the DQ report in Snowflake: `SELECT * FROM nexus_prod.dq.daily_report WHERE report_date = CURRENT_DATE`
3. If the DQ report shows red for SAP, **do not use that day's data** for any analysis or model retraining
4. Ping @priya.nair with specifics: which table, what anomaly, what date range
5. If it's before 9am and Priya isn't online yet, ping @arjun.patel as backup

**Q22: My local tests are passing but the CI pipeline is failing. What do I do?**
This usually means your local environment differs from CI. Common causes:
1. **Missing dependency:** Check if you've added something to your venv but forgot to add it to `requirements.txt`
2. **Environment variable missing in CI:** Check GitHub Actions secrets — ask @karan.mehta to add it
3. **Test order dependency:** CI runs tests in a different order. Your test might be relying on state from a previous test.
4. Check the GitHub Actions logs carefully — the error is almost always in the first red step. Post the log in #engineering and tag @aditya.sharma if you're stuck.

**Q23: I want to run a query on production data for an analysis. Is that allowed?**
Read-only queries on production Snowflake are fine for data analysts with proper access. For engineers, use the staging Snowflake environment by default. **Never run UPDATE, DELETE, or INSERT on production data** without explicit written approval from @priya.nair and your manager. All production data access is logged and audited. If in doubt, ask.

**Q24: How do I know which Airflow DAG controls which data pipeline?**
Go to airflow.nexuslabs.internal (VPN required). DAGs are named descriptively:
- `sap_daily_ingest` — SAP bank data ingestion
- `sap_dq_report` — SAP data quality check (runs 6am daily)
- `utility_weekly_ingest` — Utility payment data (runs Sunday 2am)
- `feature_store_refresh` — Updates Redis feature store (runs hourly)
- `model_retraining_weekly` — Retrains credit models (runs Saturday 1am)
- `metabase_cache_refresh` — Refreshes Metabase dashboards (runs 8am daily)
If a DAG is red, check the task logs in Airflow UI first, then ping the owner (listed in the DAG description).

**Q25: I need to add a new field to an existing database table. What's the process?**
1. Write a migration script (we use Alembic for FastAPI services, dbt for Snowflake)
2. Test the migration on your local environment first
3. Open a PR with the migration file — tag @aditya.sharma for backend, @priya.nair for Snowflake
4. Migration PRs need 2 approvals (not 1)
5. Never run migrations directly on production — they go through the standard deploy process
6. For Snowflake schema changes, always check with @priya.nair first — downstream models may depend on existing fields

---

## SECTION 6 — CULTURE & GROWTH

**Q26: How does performance review work here?**
Formal reviews happen twice a year — in October and April. The process:
1. You fill out a self-assessment on Keka (template provided 2 weeks before)
2. Your manager writes their assessment independently
3. You have a calibration conversation (1:1 with manager)
4. Feedback is shared openly — no hidden scores
5. Compensation changes (if any) happen after the April review cycle
Informal check-ins happen at Month 2 and Month 5 during probation. Outside of formal cycles, you can and should ask your manager for feedback anytime.

**Q27: Is there a learning & development budget?**
Yes. Every employee gets ₹30,000/year for learning. This covers:
- Online courses (Coursera, Udemy, O'Reilly, etc.)
- Conference attendance (travel + ticket, with manager approval)
- Books (buy on Amazon, expense it)
- Certifications (AWS, GCP, dbt, etc. — highly encouraged for technical roles)
Submit via Keka → Expenses → Category: Learning & Development. No pre-approval needed under ₹5,000. Above that, follow standard PO process.

**Q28: I feel like I'm not contributing enough in my first few weeks. Is that normal?**
100% normal and expected. The first 4 weeks are purely about absorbing context — the codebase, the data, the business, the people. Nobody expects you to be shipping features in Week 1. What we do expect is curiosity, questions, and showing up fully. If you're still feeling lost after Week 6, have a direct conversation with your manager — don't let it fester silently.

**Q29: How do I get promoted?**
Promotions at Nexus Labs are based on demonstrated impact, not tenure. The process:
1. Your manager nominates you during a review cycle
2. Your work is reviewed by a small calibration committee (your manager + their manager + one peer)
3. The bar is: "Are you already consistently operating at the next level?"
4. Promotions are communicated at the start of a new quarter
There's no fixed timeline — some engineers get promoted in 14 months, some in 3 years. The best thing to do is have an explicit conversation with your manager about what the next level looks like and get regular feedback on your progress.

**Q30: Where can I share ideas or feedback about how we work?**
Multiple channels:
- **#feedback** on Slack — anonymous submissions via the Typeform link pinned in the channel
- **Monthly All-Hands** — there's always an open Q&A section. Rohan and Sneha answer everything.
- **Retros** — your team's retrospective is the right place for process feedback
- **Direct to HR** — @ananya.iyer has an open door policy (and a standing invite on her calendar for anyone to book a 20-min chat)
- **Skip-level 1:1s** — you can request a 1:1 with your manager's manager anytime. It's encouraged, not a red flag.

---

## STILL NOT ANSWERED?

Post in **#ask-anything** on Slack. It's a judgment-free channel monitored by HR, your buddy network, and senior team members. No question is too basic. The only bad question is the one you were too nervous to ask and spent 3 hours figuring out alone.
