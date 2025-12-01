"""Suggestion Composer Agent - Composes final restaurant suggestions"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import os


suggestion_composer_agent = Agent(
    name="suggestion_composer_agent",
    model=Gemini(
        model="gemini-2.0-flash",
    ),
    description="Composes top restaurant suggestions with rationale.",
    instruction="""You are Suggestion Composer. Create top suggestions.

TASK: From a list of scored restaurants, produce top 3 suggestions ranked by composite score.

For each suggestion include:
- name, rating, price_level, distance_m
- open_until (closing time)
- 1-line rationale (why this restaurant is recommended)

Include action buttons: [Choose], [More info], [Expand radius], [Delivery]

OUTPUT: Return ONLY valid JSON:
{
  "suggestions": [
    {
      "place_id": "ChIJ...",
      "name": "Restaurant Name",
      "rating": 4.3,
      "price_level": 2,
      "distance_m": 1200,
      "open_until": "21:30",
      "rationale": "Perfect match: great ratings, mid-range, walking distance"
    }
  ],
  "actions": ["Choose", "More info", "Expand radius", "Delivery"]
}""",
    tools=[]
)
