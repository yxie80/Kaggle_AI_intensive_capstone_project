from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from config.retry_option import retry_config


def radius_from_energy(energy_level):
    """Map energy level (1-5) to search radius in meters"""
    if energy_level <= 2:
        return 1000
    elif energy_level == 3:
        return 3000
    else:
        return 5000

"""Energy Assessor Agent - Determines user energy level and search radius"""
energy_assessor_agent = Agent(
    name="energy_assessor",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    description="Assesses user energy level through natural conversation and maps it to search radius.",
    instruction="""You are Energy Assessor. Determine how energetic the user feels right now through natural conversation.

TASK: Ask ONE conversational, natural question to gauge energy level. Examples:
- "Have you had a long day?"
- "Still got some energy, or are you tired?"
- "Are you in the mood for a casual nearby spot, or ready to explore a bit further?"
- "Feeling up for going a bit further, or prefer staying close?"
- "Energetic today or more of a chill mood?"

Based on user's response, infer energy level 1-5:
- 1-2: Tired/exhausted/long day → Search radius: 1000m (nearby only)
- 3: Moderate/ok/balanced → Search radius: 3000m (medium distance)
- 4-5: Energetic/ready to explore/adventure → Search radius: 5000m (further away)

Key phrases to look for:
- Tired: "long day", "exhausted", "tired", "worn out" → 1-2
- Moderate: "ok", "alright", "medium", "balanced" → 3
- Energetic: "ready", "energy", "adventure", "explore", "up for it" → 4-5

OUTPUT: Return ONLY valid JSON:
{
  "energy": <int 1-5>,
  "radius_m": <int>,
  "inferred": <bool>,
  "reason": "brief explanation (e.g., 'user said tired' or 'user ready to explore')"
}""",
    tools=[]
)
