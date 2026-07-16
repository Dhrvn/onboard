# Nexus Labs — Engineering Incident Runbook
*Version 2.1 | Last updated: April 2026 | Owner: Karan Mehta (DevOps)*

---

> This runbook is your step-by-step guide for handling production incidents. Bookmark this page. Read it before your first on-call shift. When something breaks at 2am, you won't want to figure out the process from scratch.

---

## Incident Severity Levels

| Level | Definition | Example | Response Time | Who Handles |
|---|---|---|---|---|
| **P1 — Critical** | Production is down or significantly degraded. Revenue impact. | API returning 500s, scoring engine offline, >5% error rate | 15 minutes, 24/7 | On-call engineer + senior engineer |
| **P2 — High** | Core functionality degraded but workaround exists | Dashboard loading slowly, one lender's API key broken | 1 hour (business hours), 2 hours (off hours) | On-call engineer |
| **P3 — Medium** | Non-critical issue affecting a subset of users | One Metabase dashboard wrong, staging environment down | Next business day | Assigned engineer |
| **P4 — Low** | Minor issue, cosmetic, or future risk | Outdated docs, non-critical alert firing too often | Next sprint | Backlog ticket |

---

## P1 Incident Response — Step by Step

### STEP 1: ACKNOWLEDGE (0–5 minutes)

1. **PagerDuty fires** → Open the alert immediately
2. Post in **#incidents** on Slack:
   ```
   🔴 P1 INCIDENT IN PROGRESS
   Time: [current time]
   What: [brief description of what's broken]
   Impact: [what's affected — which lenders, which APIs]
   Investigating: @[your name]
   ```
3. Acknowledge the PagerDuty alert (stops escalation to next on-call)
4. If you need backup immediately, ping @karan.mehta and @sneha.rajan directly

---

### STEP 2: ASSESS (5–15 minutes)

**Check these in order — takes 5 minutes if you're systematic:**

#### 2a. Check API health
```bash
# Check if the scoring API is responding
curl -w "\n%{http_code}\n" https://api.nexuslabs.com/health

# Expected: {"status": "healthy", "version": "3.2.1"} with HTTP 200
# If 500/503: API is down — go to Step 2b
# If slow response (>3 seconds): possible overload — check Step 2d
```

#### 2b. Check Kubernetes pods
```bash
# Connect to production cluster (VPN must be ON)
kubectl config use-context nexus-prod

# Check if pods are running
kubectl get pods -n production

# Look for pods in CrashLoopBackOff or Error state
# Healthy output example:
# scoring-api-7d9f8b-xkp2n   1/1   Running   0   2d
# scoring-api-7d9f8b-mnq7p   1/1   Running   0   2d
# scoring-api-7d9f8b-rtz8k   0/1   CrashLoopBackOff   5   12m  ← THIS IS BAD

# Get logs from a crashing pod
kubectl logs -n production scoring-api-7d9f8b-rtz8k --previous --tail=100
```

#### 2c. Check recent deployments
```bash
# Was anything deployed in the last 2 hours?
kubectl rollout history deployment/scoring-api -n production

# Check ArgoCD for recent syncs
# Go to: argocd.nexuslabs.internal (VPN required)
# Look for any sync that happened in the last hour
```

#### 2d. Check metrics
- **Datadog:** datadog.nexuslabs.internal → Dashboard: "Production API Health"
  - API request rate (should be 50–200 req/sec during business hours)
  - Error rate (alert if >1%, P1 if >5%)
  - p95 latency (alert if >1000ms, P1 if >2000ms)
  - CPU and memory usage for scoring pods

- **CloudWatch:** Check Lambda metrics if the issue might be in the data ingestion layer
  - Lambda: `nexus-sap-ingestor` — check error count and duration

#### 2e. Check Kafka
```bash
# Check if Kafka topics are healthy
# Connect via AWS MSK console or use kafkacat:
kafkacat -b nexus-kafka.internal:9092 -L | grep "raw.sap.transactions"

# Check consumer lag (if lag is growing, processing is behind)
kafka-consumer-groups.sh --bootstrap-server nexus-kafka.internal:9092 \
  --describe --group scoring-consumer-group
# Normal lag: < 1000 messages
# Concerning: > 10,000 messages
# Critical: > 100,000 messages (processing is broken)
```

---

### STEP 3: COMMUNICATE (every 15 minutes during P1)

Post updates in #incidents every 15 minutes, even if you have no new info:

```
⏱️ UPDATE [TIME] — Still investigating. Current hypothesis: [what you think is wrong].
Actions taken: [what you've tried]. Next steps: [what you're doing next].
ETA to resolution: [your best estimate or "unknown"]
```

**If you know which lenders are affected**, ping @neha.krishnamurthy — she will contact them directly. Do not contact lenders yourself unless explicitly asked to.

---

### STEP 4: RESOLVE

#### Option A: Roll back a bad deployment (most common P1 cause)
```bash
# Roll back to previous version
kubectl rollout undo deployment/scoring-api -n production

# Watch the rollout
kubectl rollout status deployment/scoring-api -n production

# Verify recovery
curl https://api.nexuslabs.com/health
# Wait for all pods to be Running
kubectl get pods -n production -w
```

#### Option B: Restart crashing pods
```bash
# Delete the crashing pod (Kubernetes will recreate it)
kubectl delete pod scoring-api-7d9f8b-rtz8k -n production

# If all pods are crashing, restart the deployment
kubectl rollout restart deployment/scoring-api -n production
```

#### Option C: Scale up if overloaded
```bash
# Temporarily increase pod count
kubectl scale deployment scoring-api --replicas=8 -n production
# (Normal is 3 pods. Scale back down after incident.)
```

#### Option D: Database / Snowflake connection issue
```bash
# Check if Snowflake is reachable
python3 -c "
import snowflake.connector
conn = snowflake.connector.connect(
    user='service_account',
    account='nexuslabs',
    private_key_file='/secrets/snowflake_key.pem'
)
print('Snowflake OK:', conn.cursor().execute('SELECT 1').fetchone())
"
# If this fails: check AWS Secrets Manager for credential rotation
# Ping @priya.nair if Snowflake credentials have expired
```

#### Option E: Redis / Feature store issue
```bash
# Check Redis connectivity
redis-cli -h nexus-redis.internal -p 6379 ping
# Expected: PONG
# If timeout: Redis cluster may be down — check AWS ElastiCache console
# Ping @karan.mehta for Redis cluster issues
```

---

### STEP 5: CONFIRM RECOVERY (5 minutes)

Before declaring the incident resolved:

```bash
# 1. API health check
curl https://api.nexuslabs.com/health

# 2. Test a real scoring request (use test credentials)
curl -X POST https://api.nexuslabs.com/v3/score \
  -H "Authorization: Bearer TEST_KEY_INTERNAL" \
  -H "Content-Type: application/json" \
  -d '{"request_id":"incident_test_001","applicant":{"mobile":"+919999999999","pan":"TEST0000T","dob":"1990-01-01","consent_token":"test"},"loan_context":{"loan_type":"personal_loan","requested_amount_inr":100000,"tenure_months":12},"lender_id":"INTERNAL_TEST"}'

# 3. Check error rate in Datadog — should be back to <0.1%

# 4. Check p95 latency — should be back to <800ms

# 5. Confirm with a lender if one was specifically affected (via Neha)
```

Once confirmed, post in #incidents:
```
✅ RESOLVED [TIME]
Duration: [X minutes/hours]
Root cause: [brief description]
Fix applied: [what you did]
Post-mortem: Will be written by [date — within 24 hours]
```

---

### STEP 6: POST-MORTEM (within 24 hours)

**Mandatory for all P1 incidents.** Use the template in Notion (Engineering → Runbooks → Post-Mortem Template).

Sections to fill:
1. Incident summary (1 paragraph)
2. Timeline (minute-by-minute)
3. Root cause (keep asking "why" — aim for 5 whys)
4. Contributing factors
5. What we did well
6. Action items (specific, assigned, time-bound — add to Jira)

Share the post-mortem in #incidents and tag @sneha.rajan and @karan.mehta for review.

---

## P2 Incident Response

P2 is less urgent but still needs a systematic approach:

1. Post in #incidents (yellow emoji): `🟡 P2 ISSUE: [description]`
2. Investigate using the same diagnostic steps as P1
3. Update every 30 minutes
4. No need to wake anyone up — handle during business hours
5. Post-mortem optional (recommended if it could have been P1)

---

## Common Incidents and Fixes

### "SAP data not arriving" (happens ~2x/month)
**Symptoms:** #data-ops alert "SAP file missing for [bank]", DQ report red
**Cause:** Usually the bank's export job failed, or file landed in wrong S3 path
**Fix:**
1. Check S3 bucket: `s3://nexus-raw-data/sap/{bank_name}/{today_date}/`
2. If file missing: ping @priya.nair — she'll contact the bank's technical team
3. If file present but Lambda failed: check CloudWatch logs for `nexus-sap-ingestor`
4. Data for that day will be missing — note in the DQ report and ensure analysts don't use it

### "High API latency" (p95 > 1000ms)
**Symptoms:** Datadog latency alert, lenders reporting slow responses
**Common causes:**
1. **Feature store cache miss:** Redis cold — run `python scripts/warm_feature_cache.py` (ask @dev.mallik for the script)
2. **Snowflake slow:** Check Snowflake query history for long-running queries. Kill any query running >60 seconds.
3. **Pod overload:** Check CPU — if >80%, scale up pods (see Option C above)
4. **ML model inference slow:** Check SageMaker endpoint metrics

### "Dashboard not loading" (P2/P3)
**Symptoms:** Users report blank screen or spinner that never resolves
**Fix:**
1. Check if the backend API is healthy: `curl https://api.nexuslabs.com/health`
2. Check browser console errors — usually a CORS issue or auth token expiry
3. Check Metabase service: `kubectl get pods -n production | grep metabase`
4. Hard reload (Ctrl+Shift+R) often fixes client-side caching issues — ask affected user to try first

### "Lender's API key not working" (P2)
**Symptoms:** Lender reports 401 errors, their requests returning `NX_ERR_003`
**Fix:**
1. Check the lender's key status in the admin dashboard (admin.nexuslabs.internal → Lenders → [lender name])
2. Key may have auto-rotated (90-day rotation) — check if they received the rotation email
3. If key is showing as active but still failing, rotate manually and send new key to @neha.krishnamurthy to pass to the lender

---

## On-Call Checklist Before Your Shift

- [ ] PagerDuty app installed and notifications enabled on your phone
- [ ] VPN configured and tested
- [ ] Can access: CloudWatch, Datadog, Airflow, ArgoCD, Kubernetes (kubectl)
- [ ] Have read this runbook fully
- [ ] Know who the senior engineer backup is for this week (check #data-ops pinned message)
- [ ] Laptop charged and available (don't go to an area with no internet during your on-call week)
- [ ] Have tested the `curl` health check command from your terminal

---

## Useful Commands Cheat Sheet

```bash
# Check all production pods
kubectl get pods -n production

# Get logs for a specific pod
kubectl logs -n production <pod-name> --tail=200

# Restart a deployment
kubectl rollout restart deployment/<name> -n production

# Roll back a deployment
kubectl rollout undo deployment/<name> -n production

# Scale a deployment
kubectl scale deployment/<name> --replicas=5 -n production

# Check API health
curl https://api.nexuslabs.com/health

# SSH into a pod for debugging
kubectl exec -it <pod-name> -n production -- /bin/bash

# Check Kafka consumer lag
kafka-consumer-groups.sh --bootstrap-server nexus-kafka.internal:9092 \
  --describe --group scoring-consumer-group

# Check Redis
redis-cli -h nexus-redis.internal -p 6379 ping
redis-cli -h nexus-redis.internal -p 6379 info memory
```

---

## Key Contacts During Incidents

| Role | Person | Slack | Phone (P1 only) |
|---|---|---|---|
| On-call (current week) | See #data-ops pinned | — | PagerDuty |
| DevOps backup | Karan Mehta | @karan.mehta | +91 98XXX XXXXX |
| CTO (P1 escalation) | Sneha Rajan | @sneha.rajan | +91 97XXX XXXXX |
| Lender relations | Neha Krishnamurthy | @neha.krishnamurthy | +91 96XXX XXXXX |
| Data pipeline issues | Priya Nair | @priya.nair | +91 95XXX XXXXX |
| AWS support | — | — | AWS Support console (Business tier) |
