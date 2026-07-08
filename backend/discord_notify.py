import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def notify_task_created(title: str, description: str, workspace_id: int):
    """Send a Discord notification when a task is saved via tool calling."""
    if not DISCORD_WEBHOOK_URL:
        print("Warning: DISCORD_WEBHOOK_URL not set, skipping notification.")
        return

    payload = {
        "embeds": [
            {
                "title": f"📋 New Task Created",
                "description": description or "No description provided.",
                "color": 5814783,
                "fields": [
                    {"name": "Task", "value": title, "inline": True},
                    {"name": "Workspace ID", "value": str(workspace_id), "inline": True},
                ],
            }
        ]
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"Discord notification failed: {e}")
