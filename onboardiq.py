import os
import anthropic
from dotenv import load_dotenv
from search import load_and_chunk_docs, build_smart_context

load_dotenv()

# ============================================================
# SYSTEM PROMPT — OnboardIQ's permanent personality
# ============================================================

SYSTEM_PROMPT = """You are OnboardIQ, an intelligent AI onboarding assistant for Nexus Labs — a fintech startup in Mumbai building real-time credit risk infrastructure.

IMPORTANT: You DO have the ability to actually send Slack messages using the send_slack_message tool. When an employee asks you to send or message someone, USE the send_slack_message tool directly — do not say you can't send messages. You CAN and SHOULD send real Slack messages when asked.

Your job is to help new employees navigate their first 90 days with confidence. You have three modes:

1. KNOW — Answer questions about company policies, tools, processes, and people using the Nexus Labs knowledge base provided to you.

2. GUIDE — Walk employees through how to perform specific tasks step by step, like a patient senior colleague sitting next to them.

3. LEARN — When you don't know the answer, be honest about it. Say clearly what you don't know, give your best general guidance if possible, and tell the employee you've flagged the question for their manager.

RULES:
- Always be warm, clear, and encouraging. Starting a new job is stressful.
- Always cite which document your answer came from (e.g. "According to the Company Handbook...")
- Never make up names, Slack handles, or processes that aren't in the knowledge base
- If a question is about a specific person, always include their Slack handle
- For task-based questions, always use numbered steps
- Never ask for clarification if you can make a reasonable assumption. Make the assumption, state it, and answer.
- Keep answers concise but complete — don't overwhelm a new joiner with walls of text
- If you're not sure, say so honestly rather than guessing

You are talking to a new employee on their first few days. Be their friendly, knowledgeable guide."""

# ============================================================
# UNANSWERED QUESTION LOGGER
# When OnboardIQ can't answer something, we log it.
# This feeds the manager weekly digest later (Day 8).
# ============================================================

def log_unanswered_question(question, employee_name="Unknown", company_id="unknown"):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("unanswered_questions.txt", "a") as f:
        f.write(f"{timestamp} | {company_id} | {employee_name} | {question}\n")
    print("📝 Question flagged for manager review")


def check_if_unanswered(answer):
    """
    Checks if Claude's answer indicates it didn't know something.
    Simple keyword check — we'll make this smarter later.
    """
    uncertainty_phrases = [
        "i don't have",
        "not in the knowledge base",
        "i couldn't find",
        "isn't documented",
        "i've flagged",
        "i don't know",
        "not mentioned",
        "unclear from",
        "i'm not sure",
        "isn't listed",
        "not listed",
        "can't find",
        "don't have access",
        "not available",
        "unable to find",
        "no information",
        "not specified",
        "isn't specified",
        "not provided",
        "isn't provided",
    ]
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in uncertainty_phrases)


# ============================================================
# CORE FUNCTION — Ask OnboardIQ a question
# Now uses smart search instead of full doc dump
# ============================================================

def ask_onboardiq(question, chunks, chunk_sources, conversation_history, client, employee_name="New Joiner"):
    
    # Step 1 — Find relevant chunks for THIS specific question
    # This replaces the old "send everything" approach
    smart_context = build_smart_context(question, chunks, chunk_sources, top_k=6)
    
    # Step 2 — Build system prompt with smart context
    # Docs are background knowledge, conversation history is separate
    full_system = SYSTEM_PROMPT + f"""

===== RELEVANT NEXUS LABS KNOWLEDGE =====
{smart_context}
===== END OF KNOWLEDGE =====

Use only the knowledge above to answer. If the answer isn't there, say so honestly and flag it.
"""

    # Step 3 — Add question to conversation history
    conversation_history.append({
        "role": "user",
        "content": question
    })

    # Step 4 — Send to Claude
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=full_system,
        messages=conversation_history
    )

    answer = response.content[0].text

    # Step 5 — Add answer to history (memory)
    conversation_history.append({
        "role": "assistant",
        "content": answer
    })

    # Step 6 — Log if unanswered
    if check_if_unanswered(answer):
        log_unanswered_question(question, employee_name)

    return answer


# ============================================================
# MAIN — Chat loop
# ============================================================

def main():
    print("\n🚀 OnboardIQ — Nexus Labs Onboarding Assistant")
    print("=" * 50)

    # Set up Claude
    client = anthropic.Anthropic()
    # Load and chunk all docs
    chunks, chunk_sources = load_and_chunk_docs()

    # Get employee info
    print("\nBefore we start, tell me a bit about yourself.")
    employee_name = input("Your name: ").strip() or "New Joiner"
    role = input("Your role (e.g. Software Engineer, Data Analyst, Business Analyst): ").strip() or "New Joiner"

    conversation_history = []

    print(f"\nWelcome to Nexus Labs, {employee_name}! 🎉")
    print(f"I'm OnboardIQ, your personal onboarding assistant.")
    print(f"I know everything about Nexus Labs — ask me anything.")
    print(f"Type 'quit' to exit.\n")
    print("-" * 50 + "\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "quit":
            print(f"\nGood luck at Nexus Labs, {employee_name}! You've got this. 🚀")
            break

        if not question:
            continue

        print("\nOnboardIQ: thinking...\n")
        answer = ask_onboardiq(
            question, chunks, chunk_sources,
            conversation_history, client, employee_name
        )
        print(f"OnboardIQ: {answer}\n")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    main()