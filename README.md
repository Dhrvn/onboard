# OnboardIQ — Hire fast. Ramp faster.

> Agentic AI that turns new hires into contributors from day one — no manager interruptions, no knowledge gaps, no wasted weeks.

**🌐 Live Demo:** [onboardiq-production-608f.up.railway.app](https://onboardiq-production-608f.up.railway.app)

---

## What it does

OnboardIQ is a multi-agent AI onboarding platform. It's not a chatbot — it takes real actions across your company's tools autonomously.

| Capability | What happens |
|---|---|
| **Company Intelligence** | Upload your docs once. OnboardIQ answers any question from your actual company knowledge base using semantic RAG |
| **Autonomous Slack Messaging** | New hire asks for AWS access → OnboardIQ identifies the right person and sends the DM automatically |
| **Jira Ticket Creation** | Creates properly formatted tickets with acceptance criteria from a natural language request |
| **Live Web Search Agent** | When docs don't have the answer, searches the web in real time and synthesizes results |
| **30/60/90 Day Plans** | Generates fully personalized onboarding plans per role using company-specific context |
| **Manager Dashboard** | Tracks knowledge gaps, active employees, and unanswered questions — with one-click answers that train the AI |
| **Multi-Company SaaS** | Any company uploads their docs and gets their own OnboardIQ instance in 5 minutes |
| **Self-Improving Knowledge Base** | Every manager answer gets added back to the docs — the system gets smarter over time |

---

## Architecture

```
Browser (React/HTML)
        ↓
FastAPI Backend (server.py)
        ↓
Agent Loop (agents.py)
    ├── Tool: web_search → Anthropic native search
    ├── Tool: send_slack_message → Slack SDK (real DMs)
    └── Tool: create_jira_ticket → formatted ticket drafts
        ↓
Semantic RAG (search.py)
    ├── TF-IDF vectorization
    ├── Cosine similarity ranking
    └── Top-k chunk retrieval
        ↓
Claude API (claude-sonnet-4-6)
    └── Tool use / multi-step reasoning
        ↓
Company Knowledge Base
    └── Per-company isolated doc store
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Claude API (claude-sonnet-4-6) with tool use |
| **Agent Framework** | Custom agentic loop with multi-step reasoning |
| **RAG** | TF-IDF semantic search + cosine similarity (scikit-learn) |
| **Slack Integration** | Slack SDK — real message sending, not drafts |
| **Backend** | Python + FastAPI |
| **Frontend** | Vanilla HTML/CSS/JS (no framework needed) |
| **Deployment** | Railway |
| **Memory** | Session-based conversation history |

---

## Key Technical Decisions

**Why custom RAG over LangChain/LlamaIndex?**
Built TF-IDF chunking from scratch to understand the fundamentals and avoid framework overhead. Gives full control over chunk size, overlap, and retrieval strategy.

**Why tool use over function calling patterns?**
Claude's native tool use API enables genuine multi-step reasoning — the agent decides which tools to use, in what order, and when to stop. Not a predetermined chain.

**Why FastAPI over Flask?**
Async support, automatic OpenAPI docs, Pydantic validation. Better suited for production API patterns.

**Why multi-tenant from the start?**
Any company should be able to plug in their docs and get their own isolated instance. Built the multi-company architecture early to avoid painful refactoring later.

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/Dhrvn/onboard.git
cd onboard

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your ANTHROPIC_API_KEY and SLACK_BOT_TOKEN to .env

# Run locally
uvicorn server:app --reload
```

Open `http://localhost:8000`

---

## Project Structure

```
onboardiq/
├── server.py              # FastAPI app + all API routes
├── agents.py              # Agentic loop + tool definitions
├── search.py              # TF-IDF RAG implementation
├── onboardiq.py           # System prompt + core logic
├── company_manager.py     # Multi-company registry
├── slack_integration.py   # Real Slack message sending
├── companies/
│   └── nexus_labs/        # Demo company docs (9 files)
├── static/
│   ├── landing.html       # Marketing landing page
│   ├── app.html           # Main chat interface
│   ├── setup.html         # Company setup flow
│   └── manager.html       # Manager dashboard
└── requirements.txt
```

---

## Demo Company — Nexus Labs

The repo includes a fully fleshed-out demo company: **Nexus Labs** — a fictional fintech startup with 9 realistic documents covering:

- Company handbook (leave policy, tools, processes)
- Tech stack and data pipelines (SAP ingestion, Kafka, Snowflake)
- Org structure (25 named employees with Slack handles)
- Role-specific guides (SE, DA, BA — with 30/60/90 day plans)
- Process how-tos (PO requests, expense claims, incident response)
- New joiner FAQ (30 real questions with detailed answers)
- Product specification (full API docs with request/response schemas)
- Incident runbook (production debugging with kubectl commands)
- Active sprint board (real Jira tickets in different states)

---

## URLs

| Route | Description |
|---|---|
| `/` | Landing page |
| `/app?company=nexus_labs` | Chat interface (demo) |
| `/setup` | Add a new company |
| `/manager?company=nexus_labs` | Manager dashboard |

---

## What I learned building this

1. **Agentic RAG > traditional RAG** — retrieval as one step in a reasoning loop, not the whole architecture
2. **Context engineering matters** — separating docs from conversation history dramatically improved memory
3. **Tool use is genuinely different from function calling** — the agent decides what to do, not you
4. **Multi-tenancy from day one** — retrofitting it later would have been painful
5. **MCP is becoming infrastructure** — the Slack integration previews what full MCP looks like

---

## Built by

**Abhishek Dhruvan Pabbineedi**
Cornell Tech MBA (2026–2027) | Previously: Tata Technologies (BMW + Tata Motors)

[LinkedIn](https://linkedin.com/in/abhishekdhruvan) · [Live Demo](https://onboardiq-production-608f.up.railway.app)

---

*Built solo in 2 weeks before starting Cornell Tech MBA.*
