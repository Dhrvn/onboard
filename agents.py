# agents.py
# This is where our agent tools live.
# Tools are functions the AI can CHOOSE to call.
# The AI decides when to use them — that's what makes it agentic.

from slack_integration import send_slack_dm, send_slack_channel_message, test_connection
import os
import json
import anthropic
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# TOOL DEFINITIONS
# These tell Claude what tools exist and when to use them.
# Claude reads these descriptions and decides on its own
# whether to call a tool or just answer directly.
# ============================================================

TOOLS = [
    {
        "name": "web_search",
        "description": """Search the internet for current information.
        Use this when:
        - The question cannot be answered from the Nexus Labs knowledge base
        - The user asks about something external (a tool, technology, concept)
        - The knowledge base says it doesn't have the answer
        - The user explicitly asks to search online
        Do NOT use for questions clearly answerable from Nexus Labs docs.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and concise."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_jira_ticket",
        "description": """Create a draft Jira ticket for the employee.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "type": {"type": "string"},
                "description": {"type": "string"},
                "acceptance_criteria": {"type": "string"}
            },
            "required": ["title", "type", "description"]
        }
    },
    {
        "name": "send_slack_message",
        "description": """Actually SEND a Slack message to someone in the workspace.
        Use this when:
        - The employee wants to contact someone at the company
        - The employee asks you to message someone on their behalf
        - The employee needs to request access to a tool
        - The employee says 'send', 'message', 'ping', or 'reach out to'
        This ACTUALLY sends the message — not just a draft.
        Always confirm with the employee what you're about to send before sending.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "Name or username of the person to message e.g. 'dhruvan' or 'adhruvan11'"
                },
                "message": {
                    "type": "string",
                    "description": "The full message to send"
                },
                "channel": {
                    "type": "string",
                    "description": "Optional — channel name if sending to a channel instead of a DM"
                }
            },
            "required": ["recipient", "message"]
        }
    }
    
]

# ============================================================
# TOOL EXECUTION
# When Claude decides to use a tool, we actually run it here.
# This is the "action" part of the agent.
# ============================================================

def execute_tool(tool_name, tool_input):
    """
    Executes whichever tool Claude decided to use.
    Returns the result back to Claude so it can 
    incorporate it into its final answer.
    """
    
    if tool_name == "web_search":
        return run_web_search(tool_input["query"])
    
    elif tool_name == "draft_slack_message":
        return draft_slack_message(
            tool_input["recipient"],
            tool_input["purpose"],
            tool_input["employee_name"],
            tool_input["employee_role"],
            tool_input.get("context", "")
        )
    
    elif tool_name == "create_jira_ticket":
        return create_jira_ticket(
            tool_input["title"],
            tool_input["type"],
            tool_input["description"],
            tool_input.get("acceptance_criteria", "To be defined")
        )

    elif tool_name == "send_slack_message":
        recipient = tool_input["recipient"]
        message = tool_input["message"]
        channel = tool_input.get("channel")
        
        if channel:
            result = send_slack_channel_message(channel, message)
        else:
            result = send_slack_dm(recipient, message)
        
        return result    
    
    return {"error": f"Unknown tool: {tool_name}"}


def run_web_search(query):
    """
    Searches the web using Anthropic's native web search.
    """
    print(f"🔍 Agent searching web for: {query}")
    
    try:
        import anthropic as ant
        search_client = ant.Anthropic()
        
        response = search_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user", 
                "content": f"Search for and summarize: {query}. Be concise and factual."
            }]
        )
        
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text
        
        return {
            "results": [{"title": "Web Search", "url": "", "snippet": result_text}],
            "query": query,
            "summary": result_text
        }
    
    except Exception as e:
        print(f"Search error: {e}")
        return {"error": str(e), "message": "Search failed — answering from knowledge"}

def draft_slack_message(recipient, purpose, employee_name, employee_role, context=""):
    """
    Drafts a professional Slack message.
    Returns the ready-to-send message text.
    """
    print(f"✍️ Agent drafting Slack message to {recipient}")
    
    # Build context-aware message
    message = f"""Hi {recipient.split('@')[0].replace('.', ' ').title()}! 👋

I'm {employee_name}, just joined Nexus Labs as a {employee_role}. 

{purpose}"""
    
    if context:
        message += f"\n\n{context}"
    
    message += "\n\nThanks so much! Looking forward to working with you."
    
    return {
        "message": message,
        "recipient": recipient,
        "action": "slack_message_drafted"
    }


def create_jira_ticket(title, ticket_type, description, acceptance_criteria):
    """
    Creates a formatted Jira ticket draft.
    """
    print(f"🎫 Agent creating Jira ticket: {title}")
    
    ticket = {
        "title": title,
        "type": ticket_type,
        "description": description,
        "acceptance_criteria": acceptance_criteria,
        "status": "Draft — ready to create in Jira",
        "action": "jira_ticket_drafted"
    }
    
    return ticket


# ============================================================
# MAIN AGENT FUNCTION
# This is the agentic loop:
# 1. Send message to Claude with tools available
# 2. Claude decides: answer directly OR use a tool
# 3. If tool: we run it, send result back to Claude
# 4. Claude incorporates result and gives final answer
# 5. Repeat until Claude is done
# ============================================================

def run_agent(message, system_prompt, conversation_history, client):
    """
    Runs the full agentic loop.
    Claude can use multiple tools in sequence before answering.
    Returns the final answer + any actions taken.
    """
    
    actions_taken = []
    
    # Add user message to history
    messages = conversation_history + [
        {"role": "user", "content": message}
    ]
    
    # Agent loop — keeps running until Claude gives a final answer
    max_iterations = 5  # safety limit
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Call Claude with tools available
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )
        
        # Check why Claude stopped
        if response.stop_reason == "end_turn":
            # Claude is done — extract final text answer
            final_answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_answer = block.text
                    break
            
            return {
                "answer": final_answer,
                "actions": actions_taken
            }
        
        elif response.stop_reason == "tool_use":
            # Claude wants to use a tool
            # Add Claude's response to message history
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Find which tool Claude wants to use
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    print(f"🤖 Agent using tool: {tool_name}")
                    
                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)
                    
                    # Track what actions were taken
                    actions_taken.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result
                    })
                    
                    # Format result for Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result)
                    })
            
            # Send tool results back to Claude
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        else:
            # Unexpected stop reason
            break
    
    return {
        "answer": "I ran into an issue processing your request. Please try again.",
        "actions": actions_taken
    }