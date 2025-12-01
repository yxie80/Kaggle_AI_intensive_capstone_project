"""Food Preference Agent - Determines preferred cuisine and dish"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import os


food_preference_agent = Agent(
    name="food_preference_agent",
    model=Gemini(
        model="gemini-2.0-flash"
    ),
    description="Determines user food preferences and cuisine type.",
    instruction="""You are Food Preference Agent. Help user pick their preferred cuisine.

TASK: Given a list of available cuisine types (max 6), ask user to pick one or suggest an alternative.

Ask: "Which cuisine appeals to you most?" and optionally "Any specific dish in mind?"

OUTPUT: Return ONLY valid JSON:
{
  "preferred_cuisine": "Thai",
  "preferred_dish": "Pad Thai",
  "inferred": false
}""",
    tools=[]
)
