"""Environment Collector Agent - Gathers contextual environment data"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from datetime import datetime
import json
import os


def get_env_data():
    """Collect environment data"""
    now = datetime.now()
    return {
        "local_time": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
        "is_workday": now.weekday() < 5,  # Monday=0, Friday=4
        "special_dates": [],
        "food_types": ["Thai", "Japanese", "Italian", "Mexican", "Indian", "Chinese"]
    }


env_collector_agent = Agent(
    name="env_collector",
    model=Gemini(
        model="gemini-2.0-flash"
    ),
    description="Collects current environment data including time, weekday, and cached cuisine types.",
    instruction="""You are Env Collector. Your role is to gather and structure current environmental context.
    
TASK: Provide current local time, weekday, whether it's a workday, nearby cuisine types (use the provided list), and notable special dates.

OUTPUT: Return ONLY valid JSON matching this schema:
{
  "local_time": "HH:MM",
  "weekday": "Monday",
  "is_workday": true,
  "special_dates": [{"date":"YYYY-MM-DD","label":"..."}],
  "food_types": ["Thai","Japanese"]
}

Be concise and return only JSON.""",
    tools=[]
)
