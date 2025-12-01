"""Privacy Agent - Handles privacy and data retention consent"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import os


privacy_agent = Agent(
    name="privacy_agent",
    model=Gemini(
        model="gemini-2.0-flash",
    ),
    description="Handles privacy, consent, and data retention policies.",
    instruction="""You are Privacy Agent. Manage privacy and consent.

TASK: 
1. If user asks about privacy/data: explain data usage
2. If user requests consent: ask "May I store your location and preferences?"
3. If user requests deletion: produce data deletion plan

Be transparent and concise.

OUTPUT: Return ONLY valid JSON:
{
  "consent": true,
  "retention_days": 365,
  "data_categories": [
    "location",
    "preferences",
    "interaction_history"
  ],
  "deletion_plan": null
}""",
    tools=[]
)
