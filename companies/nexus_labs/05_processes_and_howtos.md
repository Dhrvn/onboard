# Nexus Labs — Processes & How-To Guides
*Last updated: April 2026*

---

## How To Raise a Purchase Order (PO)

New joiners often need to purchase tools, subscriptions, or equipment. Here's the exact process:

1. **Check if it's already covered** — look at the approved tools list in the Company Handbook first. If the tool is listed, you already have access or can get it via IT.

2. **For new purchases under ₹5,000:** No PO needed. Submit as an expense on Keka after purchasing. Attach receipt.

3. **For purchases ₹5,000–₹50,000:**
   - Fill out the **Purchase Request Form** on Notion (Finance → Purchase Requests → New Request)
   - Get your manager's approval (they'll comment on the Notion page)
   - Tag @vikram.desai on Slack with the Notion link
   - Vikram will process within 3 business days
   - You'll receive a PO number via email
   - Use the PO number when placing the order

4. **For purchases above ₹50,000:**
   - Same as above, but also needs CFO (Divya Pillai) approval
   - Allow 5–7 business days
   - Must include 3 vendor quotes

**Common mistake:** Purchasing first, then asking for a PO. This creates accounting problems. Always get PO approval before purchasing for anything above ₹5,000.

---

## How To File an Expense Reimbursement

1. Open **Keka** → **My Actions** → **Expense Claims**
2. Click **"New Expense Claim"**
3. Fill in: Date, Category (Travel/Meals/Software/Other), Amount, Description
4. Upload receipt photo (mandatory for amounts above ₹500)
5. Submit — your manager gets a notification to approve
6. Once approved, reimbursement arrives in your next payroll cycle (or within 15 working days)

**Categories explained:**
- **Travel:** Uber/Ola/train/flight for work purposes. Include trip purpose in description.
- **Meals:** Client meals or team meals approved by manager. Solo meals not reimbursable unless traveling.
- **Software:** Any work-related software subscription not provided by IT.
- **Equipment:** Work-from-home equipment (max ₹10,000/year, pre-approved by manager).

---

## How To Raise a Jira Ticket

1. Go to **Jira** (jira.nexuslabs.internal)
2. Select the relevant project board (ask your manager which board your team uses)
3. Click **"Create"**
4. Fill in:
   - **Issue Type:** Bug / Story / Task / Spike
   - **Summary:** One clear sentence describing the work
   - **Description:** Context, what needs to be done, why
   - **Acceptance Criteria:** How do we know it's done?
   - **Assignee:** Yourself (if you're doing it) or leave blank for the team to pick up
   - **Priority:** Blocker / High / Medium / Low
   - **Sprint:** Current sprint (if it needs to be done now) or Backlog
5. Click **Create**
6. Share the ticket link in the relevant Slack channel if others need visibility

**Issue type guide:**
- **Bug:** Something broken that shouldn't be
- **Story:** A user-facing feature or improvement
- **Task:** Internal work with no direct user impact (infra, docs, refactor)
- **Spike:** Research or investigation work where the output is a recommendation, not code

---

## How To Request Access to AWS

1. Ping @karan.mehta on Slack: *"Hi Karan, I'm [name], [role], joined [date]. I need AWS read access to [specific service — e.g., S3, CloudWatch]. My manager is [manager name]."*
2. Karan will ask your manager to confirm
3. He'll create your IAM user and send credentials via Slack (encrypted)
4. You'll need to set up MFA immediately — Karan will walk you through it
5. **Default access is read-only.** Write access requires justification and senior engineer approval.

---

## How To Get On-Call (Engineers & Data)

On-call rotates weekly. Here's how it works:

**Before your first on-call shift:**
1. Make sure PagerDuty is set up on your phone (ask @karan.mehta for invite)
2. Make sure you have VPN access and can access CloudWatch, Airflow, and Datadog from your phone
3. Read the **Incident Runbook** in Notion (Engineering → Runbooks → Incident Response)
4. Shadow an experienced on-call engineer for 2 weeks before going solo

**During your on-call week:**
- You're expected to respond to P1 alerts within **15 minutes**, day or night
- P2 alerts: within **1 hour** during business hours, **2 hours** outside
- Always post in #incidents when you start investigating
- Always write a brief post-mortem within 24 hours of a P1 incident (template in Notion)

**You are NOT expected to be on-call in your first 60 days.** Let your manager know when you feel ready.

---

## How To Run a Retrospective

Retros happen every 2 weeks on Friday. Format:

1. **What went well?** (5 min) — everyone adds sticky notes on Miro
2. **What didn't go well?** (5 min) — everyone adds sticky notes
3. **What was confusing or surprising?** (3 min)
4. **Action items** (10 min) — pick 2–3 things to actually change, assign owners
5. **Review last retro's action items** (5 min) — did we do them?

Rules:
- No blame, no names in "what didn't go well" — focus on systems and processes
- Every action item needs an owner and a deadline
- The facilitator rotates — you'll take a turn within your first 3 months

---

## How To Do a Code Review

When reviewing a teammate's PR:

**What to check:**
- Does the code do what the PR description says?
- Are there tests? Do they cover the main cases?
- Is the code readable? Would you understand it in 6 months?
- Are there any obvious security issues? (hardcoded credentials, SQL injection risks, etc.)
- Does it follow our code style? (flake8 + black)

**How to give feedback:**
- Use GitHub's inline comment feature — comment on the specific line
- Distinguish between blocking issues and suggestions: use "Blocking:" or "Suggestion:" prefix
- Be specific. "This is confusing" is not helpful. "This function name doesn't describe what it does — consider renaming to `calculate_risk_score`" is helpful.
- Approve when you're satisfied, or "Request changes" if there are blocking issues

**Response time:** Try to review within 1 business day. If you're busy, say so in the PR comments so the author knows.

---

## How To Write a Post-Mortem

After any P1 incident, a post-mortem is mandatory within 24 hours. Use the Notion template (Engineering → Runbooks → Post-Mortem Template). It should include:

1. **Incident summary** — what happened, when, how long it lasted, what the impact was
2. **Timeline** — minute-by-minute log of what happened and what actions were taken
3. **Root cause** — the actual reason it happened (keep asking "why" until you get to a root cause)
4. **Contributing factors** — what made it worse or harder to detect
5. **What we did well** — don't only focus on failures
6. **Action items** — specific, assigned, time-bound things to prevent recurrence

Post-mortems are **blameless**. We're fixing systems, not punishing people.

---

## How To Give and Receive Feedback

Nexus Labs has a direct feedback culture. Here are our norms:

**Giving feedback:**
- Be specific and timely — give feedback close to the event
- Focus on behavior, not character: "The PR you submitted had no tests" not "You're careless"
- Include impact: "This caused the deploy to be reverted, which delayed our release by a day"
- Follow SBI format: **Situation** → **Behavior** → **Impact**

**Receiving feedback:**
- Don't get defensive — ask clarifying questions instead
- "Can you give me a specific example?" is always a fair response
- You don't have to agree, but you should acknowledge and reflect

**Where to give feedback:**
- Direct, in-person/Slack for minor things
- 1:1 with your manager for anything significant
- Keka's performance review module for formal quarterly feedback

---

## Useful Internal Links

| Resource | URL / Location |
|---|---|
| All Notion docs | notion.nexuslabs.internal |
| Jira | jira.nexuslabs.internal |
| Airflow | airflow.nexuslabs.internal |
| Metabase | metabase.nexuslabs.internal |
| Datadog | datadog.nexuslabs.internal |
| Keka (HR) | nexuslabs.keka.com |
| GitHub | github.com/nexuslabs |
| AWS Console | console.aws.amazon.com |
| VPN (WireGuard config) | Request from @riya.sharma |
| Post-mortem template | Notion → Engineering → Runbooks |
| PRD template | Notion → Product → Templates |
| Purchase request form | Notion → Finance → Purchase Requests |
