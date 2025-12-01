"""Budget & Group Agent - Determines budget level and group size"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from config.retry_option import retry_config


def map_budget_to_price_level(budget_desc):
    """Map budget description to Google Places price_level"""
    mapping = {
        "cheap": 1,
        "mid": 2,
        "moderate": 2,
        "fancy": 4,
        "expensive": 4
    }
    return mapping.get(budget_desc.lower(), 2)


budget_group_agent = Agent(
    name="budget_group_agent",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    description="Determines user budget preference and group size through natural conversation.",
    instruction="""You are Budget & Group Agent. Gently gather budget and group info through natural conversation.

TASK: Ask TWO separate, natural questions:

QUESTION 1 - Budget (ask naturally, not with numbers):
Options to ask:
- "Are you looking for something casual and affordable, or something a bit more upscale?"
- "Do you want to keep it budget-friendly, or are you ok splurging a bit?"
- "Thinking of a quick affordable meal, mid-range comfort, or a nicer experience?"
- "What's your budget mood - casual spot, nice dinner, or somewhere special?"

Map their response to budget:
- "cheap", "budget", "affordable", "quick", "casual" → 1 ($10-15/person)
- "mid", "moderate", "comfortable", "normal", "regular" → 2 ($20-35/person)
- "upscale", "fancy", "special", "nicer", "splurge" → 3-4 ($50+/person)

QUESTION 2 - Group Size (ask naturally):
Options:
- "How many of you will be dining?"
- "Just for yourself or bringing company?"
- "Is this for you alone, a couple, or a group?"
- "How many people in your party?"

INFER from context:
- If user says "me and my friends" → count or ask for number
- If says "date night" → 2 people
- If says "family dinner" → infer 4-5 or ask

OUTPUT: Return ONLY valid JSON:
{
  "budget_level": <int 1-4>,
  "budget_desc": "cheap|mid|upscale|fancy",
  "budget_pp_estimate": "$10-15 OR $20-35 OR $50+",
  "group_size": <int>,
  "inferred": <bool>,
  "notes": "brief explanation of inference"
}""",
    tools=[]
)
