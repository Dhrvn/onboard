import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "You are OnboardIQ, an AI onboarding assistant for Nexus Labs, a fintech startup in Mumbai. A new Software Engineer just joined today. Welcome them warmly and ask them 3 smart questions to personalize their onboarding experience."
        }
    ]
)

print(message.content[0].text)