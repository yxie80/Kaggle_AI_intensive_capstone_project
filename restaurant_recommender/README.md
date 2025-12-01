# Multi-Agent Restaurant Recommender System

A comprehensive restaurant recommendation system built with Google's Agent Development Kit (ADK), demonstrating a multi-agent architecture for conversational AI.

## System Overview

This project implements a restaurant recommendation pipeline using multiple specialized agents:

- **Orchestrator Agent**: Main coordinator managing conversation flow
- **Environment Collector**: Gathers contextual data (time, day, location)
- **Energy Assessor**: Determines user energy level → search radius mapping
- **Budget & Group Agent**: Captures budget preference and group size
- **Food Preference Agent**: Collects cuisine and dish preferences
- **Discovery Agent**: Searches restaurants using Google Places API
- **Review Analyzer**: Analyzes reviews and computes sentiment scores
- **Suggestion Composer**: Creates top 3 recommendations with rationale
- **User Profiler**: Updates user preferences and history
- **Privacy Agent**: Handles consent and data retention

## Project Structure

```plain
restaurant_recommender/
├── agents/              # Individual agent definitions
│   ├── orchestrator_agent.py
│   ├── env_collector.py
│   ├── energy_assessor.py
│   ├── budget_group_agent.py
│   ├── discovery_agent.py
│   ├── food_preference_agent.py
│   ├── review_analyzer.py
│   ├── suggestion_composer.py
│   ├── user_profiler_agent.py
│   └── privacy_agent.py
├── runner/              # Orchestration runners
│   └── orchestrator_runner.py
├── backend/             # FastAPI backend
│   └── main.py
├── config/              # Configuration & settings
│   └── settings.py
├── utils/               # Utility functions
│   ├── scoring.py       # Restaurant ranking algorithm
│   └── state_manager.py # Conversation state management
├── integrations/        # External service integrations
│   └── google_places.py # Google Places API wrapper
└── main.py              # Main entry point for demo
```

## Key Features

### 1. Conversation Flow

```plain
User → Orchestrator → Collect Location
                    → Collect Energy Level
                    → Collect Budget & Group Size
                    → Collect Cuisine Preference
                    → Discover Restaurants (Google Places)
                    → Analyze Reviews & Score
                    → Compose Top 3 Recommendations
                    → User Selects Restaurant
                    → Update User Profile
```

### 2. Restaurant Scoring Algorithm

Composite score combines:

- **Rating** (40%): Quality metric
- **Distance** (25%): Proximity/convenience
- **Value Score** (20%): Price-to-quality ratio
- **Open Now** (15%): Availability boost

```python
score = 0.4 * norm_rating + 0.25 * norm_distance + 0.2 * value_score + 0.15 * open_flag
```

### 3. Agent Coordination

- Synchronous conversation with user
- Asynchronous agent calls for heavy processing
- State persistence across turns
- Natural language understanding and generation

## Configuration

Edit `config/settings.py` to customize:

- Search radius bounds
- Scoring weights
- Cuisine types
- Budget levels
- Data retention policies

## Usage

### Run Demo

```bash
# From capstone_project/restaurant_recommender/
python main.py
```

This will run an interactive demo showing a full restaurant recommendation conversation.

### Start FastAPI Server

```bash
# From capstone_project/restaurant_recommender/
python -m uvicorn backend.main:app --reload
```

Server runs on `http://localhost:8000`

### API Endpoints

#### Start New Conversation

```bash
POST /chat
{
  "user_id": "user_123",
  "message": "Hi, I'm hungry!"
}
```

#### Continue Conversation

```bash
POST /chat
{
  "user_id": "user_123",
  "context_id": "context-uuid",
  "message": "I prefer Thai food"
}
```

#### Get Conversation State

```bash
GET /state/{context_id}
```

#### Health Check

```bash
GET /health
```

## Agent Prompts

Each agent has a specialized system prompt guiding behavior:

### Energy Assessor

> "Ask user concise question to determine energy level 1-5. Map to radius:
> 1→1000m, 2→1000m, 3→3000m, 4→5000m, 5→5000m"

### Discovery Agent

> "Search nearby restaurants by lat,lng,radius and filter by price_level and open_now.
> Return up to 20 place objects with place_id, name, rating, distance, etc."

### Suggestion Composer

> "From scored places produce top 3 suggestions. Include name, rating, distance, open_until,
> and 1-line rationale. Include action buttons."

## State Management

Conversation state tracked in `ConversationState` class:

```python
state = ConversationState(
    context_id=uuid,
    user_id="user_123",
    location={"lat": 40.7128, "lng": -74.0060},
    energy_level=3,
    budget_level=2,
    group_size=2,
    preferred_cuisine="Thai",
    search_radius_m=3000,
    candidates=[...],
    recommendations=[...],
    selected_restaurant={...}
)
```

## Scoring Example

For a restaurant with:

- Rating: 4.5/5 (norm: 0.9)
- Distance: 1200m (norm: 0.88 assuming 10km max)
- Value Score: 0.85
- Open Now: Yes (1.0)

```plain
Score = 0.4 * 0.9 + 0.25 * 0.88 + 0.2 * 0.85 + 0.15 * 1.0
      = 0.36 + 0.22 + 0.17 + 0.15
      = 0.90  (out of 1.0)
```

## Integration Points

### Google Places API

- `nearby_search()`: Find restaurants by location/radius
- `place_details()`: Get detailed info including reviews
- `text_search()`: Text-based restaurant search

### Database (Future)

- Store user profiles
- Persist conversation history
- Cache popular restaurants

### Authentication (Future)

- OAuth 2.0 for user management
- JWT tokens for API access

## Testing

```bash
# Run demo conversation
python main.py

# Start API server and test endpoints
python -m uvicorn backend.main:app --reload
# Then use curl or Postman to test /chat, /state, /health
```

## Future Enhancements

1. **Real Google Places Integration**: Call actual API with credentials
2. **Database Persistence**: Store profiles, history, preferences
3. **Redis Caching**: Cache popular restaurants and results
4. **Advanced NLU**: Better parsing of cuisine types and preferences
5. **Review Sentiment Analysis**: Use ML for review summarization
6. **Multi-language Support**: Handle multiple languages
7. **Booking Integration**: Direct booking links and calendar integration
8. **Photo Display**: Show restaurant images in recommendations
9. **Dietary Restrictions**: Accommodate allergies and dietary needs
10. **Real-time Analytics**: Track usage and improve recommendations

## Dependencies

- `google-adk` (Agent Development Kit)
- `fastapi` (REST API)
- `uvicorn` (ASGI server)
- `pydantic` (Data validation)

## Natural Language Understanding

The system excels at understanding **conversational English** rather than requiring structured numeric inputs. This makes interactions feel natural and intuitive.

### Energy Level Detection

**Question**: "Have you had a long day, or are you still full of energy?"

The system recognizes natural language patterns:

- **Tired/Low Energy** (maps to energy=2, 1000m radius): "tired", "long day", "exhausted", "drained", "worn out"
- **Energetic/High Energy** (maps to energy=4, 5000m radius): "energy", "ready", "adventure", "explore", "enthusiastic"
- **Moderate** (energy=3, 3000m radius): Any unclear response defaults to moderate

**Examples**:

- "Pretty tired after work" → energy=2, searches 1000m
- "Ready to explore!" → energy=4, searches 5000m
- "Not sure" → energy=3, searches 3000m

### Budget Understanding

**Question**: "Budget-wise - are you thinking casual and affordable, comfortable mid-range, or a nicer experience?"

Budget keyword mapping:

- **Budget/Cheap** (level=1): "cheap", "affordable", "casual", "budget", "inexpensive"
- **Mid-range** (level=2): "mid", "moderate", "comfortable", "average", "reasonable"
- **Upscale/Fancy** (level=4): "fancy", "special", "upscale", "splurge", "nice", "fine dining"

**Examples**:

- "Casual and affordable would be great" → budget=1
- "Mid-range sounds nice" → budget=2
- "Want to splurge a bit" → budget=4

### Group Size Detection

**Question**: "How many people will you be dining with?"

Group parsing:

- "just me" → 1 person
- "couple", "me and a friend" → 2 people
- "family" → 4 people
- "friends" → 5 people
- Direct numbers: "3", "for 5 people", etc.

**Examples**:

- "Solo tonight" → group_size=1
- "Me and my partner" → group_size=2
- "Family dinner for 4" → group_size=4
- "Bringing 3 friends" → group_size=5

### Cuisine Preference

**Question**: "What kind of cuisine are you in the mood for?"

Supports any cuisine type: Thai, Italian, Japanese, Mexican, Indian, Chinese, etc.

**Examples**:

- "Thai food would be great" → cuisine='Thai'
- "I'm craving Japanese" → cuisine='Japanese'
- "Something Italian tonight" → cuisine='Italian'

### Example Conversation

```plain
ASSISTANT: "Hi! I'm your restaurant recommender. To help you find the perfect 
restaurant, I need to ask you a few things. First, what's your location?"

USER: "I'm in New York, Manhattan"
→ Location set to New York, Manhattan

A: "Great! Now, quick question - have you had a long day, or are you still 
full of energy? Or somewhere in between?"

USER: "Pretty tired after work"
→ SYSTEM DETECTS: "tired" keyword → energy=2, search_radius=1000m
A: "Sounds like you've had a long day! No problem - I'll search nearby 
(within 1000m). So, budget-wise - are you thinking casual and affordable, 
comfortable mid-range, or something special?"

USER: "Mid-range would be nice"
→ SYSTEM DETECTS: "mid-range" keyword → budget=2
A: "Perfect - comfortable mid-range it is! One more thing: how many people 
will you be dining with? Just you, or bringing company?"

USER: "Me and 2 friends, so 3 total"
→ SYSTEM DETECTS: "friends" + "3" → group_size=3
A: "Excellent! I'm searching for amazing Thai restaurants for a small group. 
Let me find the perfect spots..."

USER: "Thai food would be great"
→ SYSTEM DETECTS: "Thai" keyword → cuisine='Thai'

A: [Searches Thai restaurants]
   [Analyzes reviews]
   [Scores and ranks top 3]
   
   "Found some fantastic Thai options for you! Here are my top picks:
   
   1. Golden Thai Kitchen (4.5★) - 800m away
   2. Pad Thai Express (4.2★) - 1200m away
   3. Thai Orchid Fine Dining (4.7★) - 1500m away
   
   Which one catches your eye?"

USER: "I'll go with the first one"
→ SYSTEM SELECTS: Golden Thai Kitchen
A: "Excellent choice! I'm booking Golden Thai Kitchen for you. They're open 
until 21:30. Enjoy your meal with your friends!"
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Demo entry point |
| `agents/*.py` | Individual agent definitions |
| `runner/orchestrator_runner.py` | Main orchestration logic |
| `backend/main.py` | FastAPI server |
| `config/settings.py` | Configuration constants |
| `utils/scoring.py` | Restaurant ranking logic |
| `utils/state_manager.py` | Conversation state |
| `integrations/google_places.py` | Google Places wrapper |

## Notes

- This is a demonstration implementation with mocked Google Places responses
- In production, integrate with real Google Places API and database
- State is stored in-memory; use persistent DB for production
- Add authentication and rate limiting for production deployment

---

Created: November 28, 2025  
Based on: Multi-Agent Restaurant Recommender Blueprint (ADK-focused)
