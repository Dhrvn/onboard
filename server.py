# server.py - Multi-company OnboardIQ

import os
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import anthropic
from dotenv import load_dotenv

load_dotenv()

from search import load_and_chunk_docs, build_smart_context
from onboardiq import SYSTEM_PROMPT, log_unanswered_question, check_if_unanswered
from agents import run_agent, TOOLS
from company_manager import (
    get_company, list_companies, create_company,
    save_company_doc, get_company_context, company_id_from_name,
    load_registry
)

app = FastAPI()
client = anthropic.Anthropic()
sessions = {}

# ============================================================
# DATA MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    employee_name: str
    role: str
    session_id: str
    company_id: str = "nexus_labs"

class ChatResponse(BaseModel):
    answer: str
    flagged: bool
    actions: list = []

class CompanySetupRequest(BaseModel):
    name: str
    description: str
    color: str = "#6366f1"
    roles: list = ["Software Engineer", "Data Analyst", "Business Analyst"]

# ============================================================
# STATIC FILES & HOME
# ============================================================

@app.get("/")
def serve_home():
    return FileResponse("static/landing.html")

@app.get("/app")
def serve_app():
    return FileResponse("static/app.html")

@app.get("/setup")
def serve_setup():
    return FileResponse("static/setup.html")

@app.get("/manager")
def serve_manager():
    return FileResponse("static/manager.html")

@app.get("/manager-data")
def get_manager_data(company_id: str = "nexus_labs"):
    """Returns all data the manager dashboard needs."""
    import datetime
    
    # Get unanswered questions for this company
    questions = []
    try:
        with open("unanswered_questions.txt", "r") as f:
            for line in f.readlines():
                parts = line.strip().split(" | ")
                if len(parts) >= 4 and parts[1] == company_id:
                    questions.append({
                        "timestamp": parts[0],
                        "company": parts[1],
                        "employee": parts[2],
                        "question": parts[3]
                    })
    except FileNotFoundError:
        pass

    # Get active sessions
    active_employees = []
    seen = set()
    for q in questions:
        if q["employee"] not in seen:
            active_employees.append(q["employee"])
            seen.add(q["employee"])

    # Get company info
    company = get_company(company_id)

    return {
        "company": company,
        "unanswered_questions": questions,
        "active_employees": active_employees,
        "total_unanswered": len(questions),
        "generated_at": datetime.datetime.now().strftime("%B %d, %Y at %H:%M")
    }

# ============================================================
# COMPANY ENDPOINTS
# ============================================================

@app.get("/companies")
def get_companies():
    """List all registered companies."""
    return {"companies": list_companies()}

@app.get("/companies/{company_id}")
def get_company_details(company_id: str):
    """Get details for a specific company."""
    company = get_company(company_id)
    if not company:
        return JSONResponse(status_code=404, content={"error": "Company not found"})
    return company

@app.post("/companies/create")
def create_new_company(request: CompanySetupRequest):
    """Register a new company."""
    company_id = company_id_from_name(request.name)

    # Check if already exists
    existing = get_company(company_id)
    if existing:
        return {"company": existing, "message": "Company already exists"}

    company = create_company(
        company_id=company_id,
        name=request.name,
        description=request.description,
        color=request.color,
        roles=request.roles
    )
    return {"company": company, "message": "Company created successfully"}

@app.post("/companies/{company_id}/upload-doc")
async def upload_company_doc(
    company_id: str,
    file: UploadFile = File(...)
):
    """Upload a document for a company."""
    company = get_company(company_id)
    if not company:
        return JSONResponse(status_code=404, content={"error": "Company not found"})

    # Read file content
    content = await file.read()

    # Only accept text/markdown files
    filename = file.filename
    if not filename.endswith(('.md', '.txt')):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .md and .txt files supported"}
        )

    # Save the doc
    save_company_doc(company_id, filename, content.decode('utf-8'))

    return {
        "message": f"Document '{filename}' uploaded successfully",
        "company_id": company_id
    }

# ============================================================
# CHAT ENDPOINT — now company-aware
# ============================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if request.session_id not in sessions:
        sessions[request.session_id] = []

    history = sessions[request.session_id]

    # Get company details
    company = get_company(request.company_id)
    company_name = company["name"] if company else "Your Company"
    company_desc = company.get("description", "") if company else ""

    # Get company-specific context
    smart_context = get_company_context(
        request.company_id,
        request.message,
        top_k=6
    )

    # Build system prompt — now company-aware
    full_system = f"""You are OnboardIQ, an intelligent AI onboarding assistant for {company_name}.
{f'About the company: {company_desc}' if company_desc else ''}

Your job is to help new employees navigate their first 90 days with confidence.

The employee's name is {request.employee_name} and their role is {request.role}.
Tailor your answers to their specific role where relevant.

You have three modes:
1. KNOW — Answer from the company knowledge base
2. GUIDE — Walk through tasks step by step
3. LEARN — Be honest when you don't know, flag it

RULES:
- Always be warm, clear, and encouraging
- Always cite which document your answer came from
- Never make up names or processes not in the knowledge base
- Never ask for clarification — make reasonable assumptions and answer
- For task questions, use numbered steps
- If unsure, say so honestly

You have access to tools:
- web_search: Search internet for external info
- draft_slack_message: Draft a Slack message for the employee
- create_jira_ticket: Create a Jira ticket draft

AGENT RULES:
- Answer from knowledge base first
- Use web_search only for external/unknown topics
- When employee needs to contact someone, use send_slack_message 
  to ACTUALLY SEND the message — not draft_slack_message
- Only use draft_slack_message if employee explicitly says 
  "draft" or "show me what you'd send"
- Before sending, tell the employee exactly what you're 
  about to send and who you're sending it to
- After sending, confirm it was delivered
- You can use multiple tools in sequence if needed

===== {company_name.upper()} KNOWLEDGE BASE =====
{smart_context}
===== END OF KNOWLEDGE BASE =====
"""

    # Run agent
    result = run_agent(
        request.message,
        full_system,
        history,
        client
    )

    answer = result["answer"]
    actions = result["actions"]

    # Update history
    history.append({"role": "user", "content": request.message})
    history.append({"role": "assistant", "content": answer})

    # Log if unanswered
    flagged = check_if_unanswered(answer)
    if flagged:
        log_unanswered_question(
            request.message,
            request.employee_name,
            request.company_id
        )

    return ChatResponse(answer=answer, flagged=flagged, actions=actions)


# ============================================================
# PLAN GENERATOR — now company-aware
# ============================================================

@app.post("/generate-plan")
def generate_plan(request: ChatRequest):
    company = get_company(request.company_id)
    company_name = company["name"] if company else "Your Company"

    smart_context = get_company_context(
        request.company_id,
        f"onboarding plan for {request.role} first 90 days goals tasks",
        top_k=8
    )

    plan_prompt = f"""Generate a detailed personalized 30/60/90 day onboarding plan for:
Employee: {request.employee_name}
Role: {request.role}
Company: {company_name}
Date: {datetime.now().strftime("%B %d, %Y")}

Use real tool names, real people names, real processes from the knowledge base.
Make it specific, actionable, warm and encouraging.
Split into: First 30 Days, Days 30-60, Days 60-90.
End with Key Contacts section.

===== {company_name.upper()} KNOWLEDGE BASE =====
{smart_context}
===== END ====="""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": plan_prompt}]
    )

    return {"plan": response.content[0].text}


# ============================================================
# PROGRESS TRACKING
# ============================================================

@app.post("/update-progress")
def update_progress(data: dict):
    session_id = data.get("session_id", "unknown")
    progress = data.get("progress", {})
    with open(f"progress_{session_id}.json", "w") as f:
        json.dump(progress, f)
    return {"status": "saved"}

@app.get("/get-progress/{session_id}")
def get_progress(session_id: str):
    try:
        with open(f"progress_{session_id}.json", "r") as f:
            return {"progress": json.load(f)}
    except FileNotFoundError:
        return {"progress": {}}

@app.get("/unanswered")
def get_unanswered():
    try:
        with open("unanswered_questions.txt", "r") as f:
            lines = f.readlines()
        return {"questions": lines, "count": len(lines)}
    except FileNotFoundError:
        return {"questions": [], "count": 0}

app.mount("/static", StaticFiles(directory="static"), name="static")