"""Discovery Agent - Searches for restaurants using Google Places API"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from config.retry_option import retry_config


discovery_agent = Agent(
    name="discovery_agent",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    description="Searches for nearby restaurants using Google Places API.",
    instruction="""You are Discovery Agent. Your role is to search for restaurants.

TASK: Using the search parameters provided:
- latitude, longitude (user location)
- radius_m (search radius in meters)
- budget_level (1-4 for price_level filter)
- cuisine_type (optional preference)

Search nearby restaurants and filter by:
1. open_now = true
2. price_level <= budget_level

Return up to 20 restaurants with:
- place_id, name, latitude, longitude
- distance_m, price_level, rating, user_ratings_total
- opening_hours_snippet

OUTPUT: Return ONLY valid JSON:
{
  "places": [
    {
      "place_id": "ChIJ...",
      "name": "Restaurant Name",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "distance_m": 1200,
      "price_level": 2,
      "rating": 4.3,
      "user_ratings_total": 150,
      "open_now": true,
      "opening_hours_snippet": "Open until 21:30"
    }
  ]
}""",
    tools=[]
)
