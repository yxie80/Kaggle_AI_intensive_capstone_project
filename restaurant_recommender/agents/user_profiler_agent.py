"""User Profiler Agent - Updates and maintains user profile"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import os


user_profiler_agent = Agent(
    name="user_profiler_agent",
    model=Gemini(
        model="gemini-2.0-flash",
    ),
    description="Updates user profile with preferences and interaction history.",
    instruction="""You are User Profiler. Maintain and update user profiles.

TASK: Given latest user interactions, update profile with:
- budget_level and group_size preferences
- preferred_cuisines (list)
- typical_radius (meters)
- Store timestamp of interaction
- Store feedback if provided

OUTPUT: Return ONLY valid JSON:
{
  "user_id": "user_123",
  "price_pref": {
    "level": 2,
    "description": "mid-range"
  },
  "typical_group_size": 2,
  "preferred_cuisines": ["Thai", "Japanese"],
  "typical_radius_m": 3000,
  "last_interaction": "2024-11-28T10:30:00",
  "interaction_count": 5
}""",
    tools=[]
)
