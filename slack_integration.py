# slack_integration.py
# Real Slack integration for OnboardIQ
# This actually SENDS messages — not just drafts them

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Initialize Slack client
slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# ============================================================
# CORE FUNCTIONS
# ============================================================

def send_slack_dm(recipient_email_or_name, message, sender_name="OnboardIQ"):
    """
    Actually sends a Slack DM to a person.
    recipient can be email or display name.
    """
    try:
        # Step 1 — Find the user in the workspace
        user_id = find_user(recipient_email_or_name)
        
        if not user_id:
            return {
                "success": False,
                "error": f"Could not find user: {recipient_email_or_name}",
                "action": "slack_dm_failed"
            }
        
        # Step 2 — Open a DM channel with them
        dm_response = slack_client.conversations_open(users=[user_id])
        channel_id = dm_response["channel"]["id"]
        
        # Step 3 — Send the message
        result = slack_client.chat_postMessage(
            channel=channel_id,
            text=message,
            username=f"OnboardIQ Bot",
            icon_emoji=":robot_face:"
        )
        
        print(f"✅ Slack DM sent to {recipient_email_or_name}")
        return {
            "success": True,
            "message_ts": result["ts"],
            "channel": channel_id,
            "action": "slack_dm_sent",
            "recipient": recipient_email_or_name
        }

    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
        return {
            "success": False,
            "error": e.response['error'],
            "action": "slack_dm_failed"
        }


def send_slack_channel_message(channel_name, message):
    """
    Sends a message to a Slack channel.
    channel_name should be like 'general' or 'data-ops'
    """
    try:
        # Add # if not present
        if not channel_name.startswith('#'):
            channel_name = f"#{channel_name}"
        
        result = slack_client.chat_postMessage(
            channel=channel_name,
            text=message,
            username="OnboardIQ Bot",
            icon_emoji=":robot_face:"
        )
        
        print(f"✅ Slack message sent to {channel_name}")
        return {
            "success": True,
            "channel": channel_name,
            "action": "slack_channel_message_sent"
        }

    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")
        return {
            "success": False,
            "error": e.response['error'],
            "action": "slack_channel_message_failed"
        }


def find_user(identifier):
    """
    Finds a Slack user by name or email.
    Returns their user_id or None.
    """
    try:
        # Try by email first
        if "@" in identifier:
            response = slack_client.users_lookupByEmail(email=identifier)
            return response["user"]["id"]
        
        # Try by display name
        response = slack_client.users_list()
        for member in response["members"]:
            name = member.get("real_name", "").lower()
            display = member.get("name", "").lower()
            search = identifier.lower()
            
            if search in name or search in display:
                return member["id"]
        
        return None

    except SlackApiError as e:
        print(f"User lookup error: {e.response['error']}")
        return None


def get_workspace_members():
    """
    Returns list of all workspace members.
    Useful for the agent to know who's in the workspace.
    """
    try:
        response = slack_client.users_list()
        members = []
        
        for member in response["members"]:
            if not member.get("is_bot") and not member.get("deleted"):
                members.append({
                    "id": member["id"],
                    "name": member.get("real_name", ""),
                    "username": member.get("name", ""),
                    "email": member.get("profile", {}).get("email", "")
                })
        
        return members

    except SlackApiError as e:
        print(f"Error fetching members: {e.response['error']}")
        return []


def test_connection():
    """
    Tests if the Slack connection works.
    Call this on startup.
    """
    try:
        response = slack_client.auth_test()
        print(f"✅ Slack connected: {response['team']} as {response['user']}")
        return True
    except SlackApiError as e:
        print(f"❌ Slack connection failed: {e.response['error']}")
        return False


# ============================================================
# TEST — run directly to verify connection
# python3.11 slack_integration.py
# ============================================================
if __name__ == "__main__":
    print("Testing Slack connection...")
    test_connection()
    
    print("\nWorkspace members:")
    members = get_workspace_members()
    for m in members:
        print(f"  - {m['name']} (@{m['username']})")