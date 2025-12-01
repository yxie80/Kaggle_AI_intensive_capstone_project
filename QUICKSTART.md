# Quick Start Guide - Restaurant Recommender

## What's Been Created

I've drafted a complete **multi-agent restaurant recommendation system** in `/capstone_project/restaurant_recommender/` based on the blueprint. Here's what's included:

## Project Contents

### 🤖 10 Specialized Agents

1. **Orchestrator Agent** - Main conversation coordinator
2. **Environment Collector** - Gathers time, day, location context
3. **Energy Assessor** - Maps energy level (1-5) to search radius
4. **Budget & Group Agent** - Captures budget and group size
5. **Food Preference Agent** - Collects cuisine preferences
6. **Discovery Agent** - Searches restaurants (Google Places interface)
7. **Review Analyzer** - Analyzes reviews and computes sentiment
8. **Suggestion Composer** - Creates top 3 recommendations
9. **User Profiler** - Updates user preferences
10. **Privacy Agent** - Handles consent and data retention

### 📂 Directory Structure

```plain
restaurant_recommender/
├── agents/              # 10 agent definitions
├── runner/              # Orchestrator runner (main logic)
├── backend/             # FastAPI server
├── config/              # Settings and constants
├── utils/               # Scoring, state management
├── integrations/        # Google Places API wrapper
├── main.py             # Interactive demo
└── README.md           # Full documentation
```

### 🔄 Conversation Flow

```plain
User: "I'm hungry!"
↓
Orchestrator: Collects preferences through conversation
  → Energy level? (determines search radius)
  → Budget? Group size?
  → Cuisine preference?
↓
Discovery: Searches nearby restaurants
↓
Analysis: Reviews restaurants, computes scores
↓
Recommendations: Top 3 suggestions with rationale
↓
Selection: User picks restaurant
↓
Complete: Save to profile
```

## 💬 Natural Language Conversation

The system understands **conversational English**, not numeric ratings:

### Energy Level Detection

Instead of asking "Rate 1-5", the system asks: *"Have you had a long day, or are you still full of energy?"*

**Recognized keywords:**

- **Tired** (energy=2, 1000m search): "tired", "long day", "exhausted", "drained", "worn out"
- **Energetic** (energy=4, 5000m search): "energy", "ready", "adventure", "explore", "enthusiastic"
- **Default** (energy=3, 3000m search): Anything else

### Budget Understanding

Instead of asking for tier numbers, the system asks: *"Are you thinking casual and affordable, comfortable mid-range, or a nicer experience?"*

**Recognized keywords:**

- **Cheap** (level=1): "cheap", "affordable", "casual", "budget", "inexpensive"
- **Mid-range** (level=2): "mid", "moderate", "comfortable", "average"
- **Fancy** (level=4): "fancy", "special", "upscale", "splurge", "nice"

### Group Size Detection

The system parses natural phrases: *"How many people will you be dining with?"*

**Recognized keywords:**

- "just me" → 1 person
- "couple" → 2 people
- "family" → 4 people
- "friends" → 5 people
- Or direct numbers: "3", "for 5 people", etc.

### Example Conversation - 1

```plain
ASSISTANT: "What's your location?"
USER: "New York, Manhattan"

A: "Have you had a long day, or are you still full of energy?"
USER: "Pretty tired after work"
→ System detects "tired" keyword, sets energy=2, search radius=1000m

A: "Sounds like you've had a long day! Budget-wise - are you thinking 
casual and affordable, comfortable mid-range, or a nicer experience?"
USER: "Mid-range would be nice"
→ System detects "mid-range" keyword, sets budget level=2

A: "Perfect! How many people will you be dining with?"
USER: "Me and 2 friends"
→ System detects "friends" keyword, sets group_size=3

A: "What kind of cuisine are you in the mood for?"
USER: "Thai food would be great"
→ System searches Thai restaurants with your preferences
```

This natural interaction feels like talking to a real friend, not filling out a form!

## Key Features

### 1. Intelligent Ranking Algorithm

- Combines rating (40%), distance (25%), value (20%), open now (15%)
- Customizable weights in config

### 2. State Management

- Tracks conversation context across turns
- Persists user preferences
- In-memory store (use database in production)

### 3. Flexible Configuration

- Adjustable search radius mapping
- Customizable cuisine types
- Budget level definitions
- Scoring weights

### 4. Mock Google Places Integration

- Ready for real API integration
- Calculates distances using Haversine formula
- Filters by price, open status

### 5. FastAPI Backend

- RESTful endpoints for chat and state
- Health check endpoint
- Easy integration with frontends

## How to Run

### Option 1: Demo Mode

```bash
cd /Users/michael_x/experiments/kaggle_ai_agent_course/capstone_project/restaurant_recommender
python main.py
```

Shows a full sample conversation demonstrating the entire flow.

### Option 2: FastAPI Server

```bash
cd /Users/michael_x/experiments/kaggle_ai_agent_course/capstone_project/restaurant_recommender
python -m uvicorn backend.main:app --reload
```

Then test endpoints:

```bash
# Start conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "message": "Hi, Im hungry!"
  }'

# Continue conversation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "context_id": "YOUR_CONTEXT_ID",
    "message": "Thai food"
  }'

# Check health
curl http://localhost:8000/health
```

## Customization Points

### 1. Agent Prompts

Edit in `agents/*.py` - each agent has a `instruction` parameter

### 2. Scoring Weights

In `config/settings.py`:

```python
DEFAULT_SCORING_WEIGHTS = ScoringWeights(
    rating_weight=0.4,
    distance_weight=0.25,
    value_weight=0.2,
    open_weight=0.15
)
```

### 3. Search Parameters

In `config/settings.py`:

```python
DEFAULT_SEARCH_CONFIG = SearchConfig(
    default_radius_m=3000,
    max_results=20,
    min_rating=3.5
)
```

### 4. Cuisine Types

In `config/settings.py`:

```python
CUISINE_TYPES = [
    "Thai",
    "Japanese",
    "Italian",
    # Add more...
]
```

## Integration Next Steps

### 1. Real Google Places API

Replace mock in `integrations/google_places.py` with:

```python
import googlemaps

client = googlemaps.Client(key=GOOGLE_API_KEY)
results = client.places_nearby(
    location=(latitude, longitude),
    radius=radius_m,
    type='restaurant'
)
```

### 2. Database

Replace `utils/state_manager.py` in-memory store with:

- PostgreSQL for production
- Redis for caching

### 3. Authentication

Add to `backend/main.py`:

```python
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.post("/chat")
async def chat(request: ChatRequest, credentials = Depends(security)):
    # Verify JWT token
    ...
```

### 4. Sentiment Analysis

In `agents/review_analyzer.py`, integrate:

```python
from transformers import pipeline
sentiment = pipeline("sentiment-analysis")
result = sentiment("Great food!")
```

## Files Overview

| File | Purpose |
|------|---------|
| `agents/orchestrator_agent.py` | Main coordinator agent |
| `runner/orchestrator_runner.py` | Conversation flow logic |
| `backend/main.py` | FastAPI server |
| `config/settings.py` | Configuration constants |
| `utils/scoring.py` | Restaurant ranking (40-25-20-15 algorithm) |
| `utils/state_manager.py` | Conversation state tracking |
| `integrations/google_places.py` | Google Places wrapper |
| `main.py` | Interactive demo script |

## Architecture Highlights

### Agent Coordination

- Orchestrator routes between agents
- Each agent specialized for one task
- Async-ready for parallel processing

### State Flow

```plain
ConversationState
├── User inputs (energy, budget, cuisine)
├── Search parameters (radius, location)
├── Discovered candidates
├── Scored recommendations
└── Selected restaurant
```

### Scoring Formula

```plain
composite_score = (0.4 × normalized_rating) +
                 (0.25 × normalized_distance) +
                 (0.2 × value_score) +
                 (0.15 × open_now_boost)
```

## Example Conversation - 2

```plain
User: "Hi, I'm hungry!"
Orchestrator: "I've got your location. How energetic are you feeling? (1-5)"

User: "3"
Orchestrator: "Energy level 3 noted! Search radius set to 3000m. What's your budget? (cheap/mid/fancy)"

User: "mid-range"
Orchestrator: "Great! What type of cuisine interests you?"

User: "Thai"
Orchestrator: "Found 3 great Thai restaurants! Here are my top picks..."

[Shows recommendations with ratings, distance, and rationale]

User: "1"
Orchestrator: "Excellent choice! I'm booking Golden Thai Kitchen for you..."
```

## Next Steps

1. **Test the demo**: `python main.py`
2. **Review agent prompts**: Look at `agents/*.py` files
3. **Explore scoring algorithm**: Check `utils/scoring.py`
4. **Start the server**: `python -m uvicorn backend.main:app --reload`
5. **Integrate real Google Places API**: Replace mock in `integrations/google_places.py`
6. **Add database**: Move state to PostgreSQL
7. **Deploy**: Use Docker + Cloud Run or Kubernetes

## Key Implementation Details

### Multi-Agent Coordination

- Orchestrator maintains conversation context
- Each agent has specific responsibilities
- State persisted across turns
- Natural conversation flow

### Scoring System

- Multi-factor ranking (rating, distance, value, availability)
- Tunable weights for different use cases
- Distance calculated using Haversine formula
- Open-now boost for immediate availability

### Error Handling

- Graceful fallbacks for parsing errors
- Default values for missing preferences
- Context validation at each step

---

The system is **ready to run** and demonstrates a complete multi-agent architecture for conversational restaurant recommendations!

For detailed documentation, see `restaurant_recommender/README.md`
