"""Review Analyzer Agent - Analyzes reviews and computes sentiment scores"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
import os


review_analyzer_agent = Agent(
    name="review_analyzer_agent",
    model=Gemini(
        model="gemini-2.0-flash",
    ),
    description="Analyzes reviews and computes sentiment scores for restaurants.",
    instruction="""You are Review Analyzer. Analyze restaurant reviews.

TASK: Given N reviews for a restaurant:
1. Summarize pros and cons (1-2 items each)
2. Compute sentiment score [-1 to 1]: -1=very negative, 0=neutral, 1=very positive
3. Extract value_score [0 to 1]: how good value for money
4. Determine good_for_groups [boolean]
5. Produce 1-line summary

OUTPUT: Return ONLY valid JSON:
{
  "place_id": "ChIJ...",
  "avg_rating": 4.2,
  "total_ratings": 120,
  "sentiment": 0.72,
  "pros": "fresh ingredients, quick service",
  "cons": "tight seating",
  "value_score": 0.8,
  "good_for_groups": true,
  "summary": "Great Pad Thai, good value, small tables"
}""",
    tools=[]
)
