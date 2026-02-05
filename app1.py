
import json
import os
import requests
from app import get_idle_seconds

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-api-key-here")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_PROMPT = """
you are an autonomous monitoring agent.

your task:
Decide what to do based on employee idle time.

Rules:
- Respond ONLY in valid JSON
- choose EXACTLY ONE action
- Allowed actions: log_normal,raise_alert,stop
"""

idle_seconds=get_idle_seconds()

print(f"idle detected : {idle_seconds} seconds")

payload = {
    
}