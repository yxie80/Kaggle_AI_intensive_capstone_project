# Multi-Agent Restaurant Recommender System

A comprehensive restaurant recommendation system built with Google's Agent Development Kit (ADK), demonstrating a multi-agent architecture for conversational AI.

**Current Status**: ✅ All 10 agents upgraded to **Gemini 2.5 Flash** (from 2.0 Flash)

## System Overview

This project implements a restaurant recommendation pipeline using multiple specialized agents:

- **Orchestrator Agent**: Main coordinator managing conversation flow (Gemini 2.5 Flash)
- **Environment Collector**: Gathers contextual data (time, day, location) (Gemini 2.5 Flash)
- **Energy Assessor**: Determines user energy level → search radius mapping (Gemini 2.5 Flash)
- **Budget & Group Agent**: Captures budget preference and group size (Gemini 2.5 Flash)
- **Food Preference Agent**: Collects cuisine and dish preferences (Gemini 2.5 Flash)
- **Discovery Agent**: Searches restaurants using Google Places API (Gemini 2.5 Flash)
- **Review Analyzer**: Analyzes reviews and computes sentiment scores (Gemini 2.5 Flash)
- **Suggestion Composer**: Creates top 3 recommendations with rationale (Gemini 2.5 Flash)
- **User Profiler**: Updates user preferences and history (Gemini 2.5 Flash)
- **Privacy Agent**: Handles consent and data retention (Gemini 2.5 Flash)

## Quick Start (Local Development)

### Prerequisites

- Python 3.133 or higher
- Pipenv for dependency management
- Google Cloud API key (with Places API v1 and Geocoding API enabled)

### Setup & Run in 3 Steps

```bash
# Step 1: Navigate to project directory
cd /Users/michael_x/workstation/capstone_project/restaurant_recommender

# Step 2: Install dependencies via Pipenv
pipenv install

# Step 3: Set your Google API key
export GOOGLE_API_KEY=your_api_key_here

# Step 4: Run the interactive CLI demo
pipenv run python main.py
```

**That's it!** The app will start the interactive restaurant recommendation conversation.

### Sample Interaction

```plain
You: I'm in Melbourne CBD in Australia
Assistant: Got it - CBD, Melbourne VIC 3000, Australia...

You: Pretty tired after work
Assistant: Sounds like you've had a long day! No problem...

You: Mid-range would be nice
Assistant: Perfect - comfortable mid-range it is!

You: Me and 2 friends, so 3 total
Assistant: Excellent! Let me search...

You: Thai food would be great
Assistant: Found fantastic Thai options:
  1. Zawaddi Thai (4.4★) - 0.4 km away
  2. Nana Thai (4.2★) - 0.5 km away
  3. Sampaotong Thai (5.0★) - 2.9 km away
```

## Project Structure

```plain
restaurant_recommender/
├── agents/              # Individual agent definitions (10 agents, all Gemini 2.5 Flash)
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
├── test/                # Test suite (organized & verified)
│   ├── test_debug.py    # Conversation flow tests ✅
│   ├── test_debug2.py   # State management tests ✅
│   └── test_input.txt   # End-to-end CLI test inputs ✅
├── Pipfile              # Dependency management
└── main.py              # Main entry point for demo
```

## Key Features

### ✅ Recent Updates (December 2025)

**Model Upgrade - All Agents Now Using Gemini 2.5 Flash:**

All 10 specialized agents have been upgraded from `gemini-2.0-flash` to `gemini-2.5-flash`:

| Agent | File | Model | Status |
|-------|------|-------|--------|
| Orchestrator | orchestrator_agent.py | Gemini 2.5 Flash | ✅ Upgraded |
| Environment Collector | env_collector.py | Gemini 2.5 Flash | ✅ Upgraded |
| Energy Assessor | energy_assessor.py | Gemini 2.5 Flash | ✅ Upgraded |
| Budget & Group | budget_group_agent.py | Gemini 2.5 Flash | ✅ Upgraded |
| Food Preference | food_preference_agent.py | Gemini 2.5 Flash | ✅ Upgraded |
| Discovery | discovery_agent.py | Gemini 2.5 Flash | ✅ Upgraded |
| Review Analyzer | review_analyzer.py | Gemini 2.5 Flash | ✅ Upgraded |
| Suggestion Composer | suggestion_composer.py | Gemini 2.5 Flash | ✅ Upgraded |
| User Profiler | user_profiler_agent.py | Gemini 2.5 Flash | ✅ Upgraded |
| Privacy | privacy_agent.py | Gemini 2.5 Flash | ✅ Upgraded |

**Why Upgrade to Gemini 2.5 Flash?**

- Improved reasoning and context understanding
- Better multi-turn conversation handling
- Enhanced natural language comprehension
- Faster inference times
- Better error handling and edge cases

**Test Suite - All Tests Passing:**

The complete test suite has been organized in the `/test/` folder and is fully validated:

- ✅ **test_debug.py**: Conversation flow verification (6 steps)
- ✅ **test_debug2.py**: State management verification (7 steps)  
- ✅ **test_input.txt**: End-to-end CLI test with real data

All tests pass with 100% success rate using real Google Places API data.

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

## Architecture: `next_step` Pattern vs. Agent Chaining

This system uses an **explicit state machine routing pattern** (`next_step`) rather than agent chaining or tool-based coordination. Here's why:

### Design Pattern: State Machine with `next_step` Routing

```plaintext
User Input
    ↓
OrchestratorRunner (State Machine Router)
    ↓
Check state.location → if None, run _collect_location()
Check state.energy_level → if None, run _collect_energy()
Check state.budget_level → if None, run _collect_budget_group()
Check state.preferred_cuisine → if None, run _collect_cuisine()
Check state.candidates → if None, run _discover_restaurants()
Check state.recommendations → if None, run _compose_recommendations()
    ↓
Returns: {"message": "...", "next_step": "collect_energy", ...}
    ↓
Response sent to user/frontend with routing hint
```

### Why NOT Agent Chaining?

**Agent Chaining** (sequential agent calls) would require:

```python
orchestrator_agent() 
  → energy_assessor_agent()
    → budget_group_agent()
      → discovery_agent()
        → review_analyzer_agent()
```

**Problems with chaining for this use case:**

| Issue | Impact |
|-------|--------|
| **User Interaction Required** | Each step needs user response; chaining assumes continuous execution |
| **Token Overhead** | 6 agents × full history = 6× context window usage = high cost |
| **Not Idiomatic ADK** | Google ADK designed for system-to-system, not user-interactive conversations |
| **Error Recovery** | Chain failure = restart entire flow; `next_step` allows retry from any point |
| **Flexibility** | User wants to change budget? Chain restarts; `next_step` jumps back to budget step |

### Why NOT Agent Tools?

**Tool-based approach** (LLM function calling):

```python
@agent_tool
def discover_restaurants(location, budget): ...

@agent_tool  
def analyze_reviews(restaurants): ...
```

**Problems:**

| Issue | Impact |
|-------|--------|
| **Over-Engineering** | Tools for deterministic logic add unnecessary complexity |
| **Loss of Control** | LLM decides what to call, might skip steps or make wrong choices |
| **Token Overhead** | Tool schemas, descriptions add context overhead |
| **Non-Deterministic** | Same input might route differently based on LLM reasoning |

### Why `next_step` Works Best

✅ **Advantages:**

- **Explicit & Predictable**: Clear state transitions, same input = same behavior
- **Lightweight**: Just a string routing key
- **Fast**: No LLM reasoning needed for routing
- **User-Friendly**: Waits for input between steps, supports clarifications
- **Cost-Efficient**: Minimal token usage, no context explosion
- **Error Recovery**: Jump to any state, retry partial flows
- **Testable**: Easy to predict and verify behavior
- **Flexible**: Users can say "Actually, change budget" and go back

### When to Use Each Pattern

| Pattern | Use When | Example |
|---------|----------|---------|
| **`next_step` State Machine** | User-interactive multi-turn conversations | This system ✓ |
| **Agent Chaining** | Automated end-to-end workflows | Email pipeline, data processing |
| **Agent Tools** | LLM needs dynamic decision-making | Research assistant, code debugger |

### Implementation Details

**Current implementation** in `orchestrator_runner.py`:

```python
async def process_message(self, context_id: str, user_message: str):
    state = self.state_store.get_state(context_id)
    
    # Route based on conversation stage
    if not state.location:
        return await self._collect_location(state, user_message)
    elif state.energy_level is None:
        return await self._collect_energy(state, user_message)
    elif state.budget_level is None or state.group_size is None:
        return await self._collect_budget_group(state, user_message)
    elif state.preferred_cuisine is None:
        return await self._collect_cuisine(state, user_message)
    elif not state.candidates:
        return await self._discover_restaurants(state, user_message)
    elif not state.recommendations:
        return await self._compose_recommendations(state, user_message)
    else:
        return await self._handle_user_choice(state, user_message)
```

**Benefits of this approach:**

- Each function handles one conversation stage
- Agents can be called from appropriate stages (e.g., `discovery_agent` in `_discover_restaurants()`)
- State is explicitly tracked and validated
- User can revisit earlier stages if needed

## Configuration

Edit `config/settings.py` to customize:

- Search radius bounds
- Scoring weights
- Cuisine types
- Budget levels
- Data retention policies

## Usage

### Option 1: Interactive CLI (Development) - **RECOMMENDED**

**Start the Interactive Demo:**

```bash
# From capstone_project/restaurant_recommender/
pipenv run python main.py
```

**Features:**

- Interactive terminal-based interface
- Multi-turn conversation with live user input
- Type "quit", "exit", or "bye" to end conversation
- Real Google Places API integration for restaurant search
- Comprehensive state management across turns
- Perfect for testing and development

**Example interaction:**

```plain
You: I'm in Melbourne CBD in Australia
Assistant: Got it - CBD, Melbourne VIC 3000, Australia. Now, quick question...

You: Pretty tired after work
Assistant: Sounds like you've had a long day!...

You: quit
Thank you for using the Restaurant Recommender!
```

### Option 2: Run Test Suite (Verification)

**Run All Tests:**

```bash
# Test 1: Conversation Flow
pipenv run python test/test_debug.py

# Test 2: State Management
pipenv run python test/test_debug2.py

# Test 3: End-to-End CLI (Automated Input)
timeout 30 bash -c 'cat test/test_input.txt | pipenv run python main.py'
```

**Test Results** (All ✅ PASSING):

- test_debug.py: Verifies conversation routing through 6 steps
- test_debug2.py: Verifies state persistence through 7 steps  
- CLI Test: End-to-end conversation with real data (finds real restaurants)

**Real Data Example from Test:**

```plain
Location: Melbourne CBD → -37.8136, 144.9631
Energy: "Pretty tired" → Level 2, 1000m search radius
Cuisine: "Thai" → 4 restaurants found
Distance Formatting: 0.4 km, 0.5 km, 2.9 km
```

### Option 3: FastAPI Web Server (Production)

**Start the Server:**

```bash
# From capstone_project/restaurant_recommender/
pipenv run python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the Web UI:** Open browser to `http://localhost:8000`

**Features:**

- Beautiful web UI with chat interface
- WebSocket support for real-time communication
- REST API endpoints
- Built-in Swagger docs at `http://localhost:8000/docs`
- CORS enabled for cross-origin requests

### When to Use Each Option

| Option | Use Case | Start Command |
|--------|----------|---------------|
| **CLI** | Development, testing, quick demo | `pipenv run python main.py` |
| **Tests** | Verify functionality, regression testing | `pipenv run python test/test_debug.py` |
| **Web Server** | Production deployment, UI access, API integration | `pipenv run python -m uvicorn backend.main:app --reload` |

### Run Multiple Options Simultaneously

You can run CLI and tests independently:

```bash
# Terminal 1: Interactive CLI
pipenv run python main.py

# Terminal 2: Run tests
pipenv run python test/test_debug.py

# Terminal 3: Start web server
pipenv run python -m uvicorn backend.main:app --reload
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

## API Integration Implementation

### Google Places API v1 Integration ✅

The system now uses real Google Places API v1 for restaurant discovery with the following features:

#### Setup Steps

1. **Enable APIs in Google Cloud Console**:
   - Google Places API v1
   - Google Geocoding API
   - Gemini API

2. **Add API Key to `.env` file**:

   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Install Dependencies**:

   ```bash
   pipenv install google-genai requests python-dotenv
   ```

#### How It Works

**Geocoding (Address → Coordinates)**:

- Converts user location input (e.g., "Melbourne CBD") to geographic coordinates
- Uses `geocode()` method with real Google Geocoding API
- Supports fuzzy matching for typos (e.g., "Melbroune" → "Melbourne")
- Fallback to mock data if API fails

**Text Search (Cuisine-Specific Discovery)**:

- Uses Google Places API v1 `searchText` endpoint
- Sends query like "Thai restaurant" to find cuisine-specific results
- Filters by location radius, price level, and open now status
- Returns up to 20 restaurants with ratings, prices, and distances

**Nearby Search (General Discovery)**:

- Alternative endpoint for all restaurants in area
- Used when no specific cuisine is provided
- Supports price level and availability filtering

#### Key Technical Details

**FieldMask Header**:

- Required by Places API v1 to specify which fields to return
- Example: `X-Goog-FieldMask: places.id,places.displayName,places.location,places.rating,places.userRatingCount,places.priceLevel,places.formattedAddress,places.types`
- Specifies only needed fields for performance

**Field Transformations**:

- API returns camelCase JSON (e.g., `displayName.text`)
- System transforms to snake_case for internal use
- Price levels mapped from enum (PRICE_LEVEL_INEXPENSIVE → 1) to numeric scale

**Error Handling**:

- Graceful fallback to mock data on API errors
- Detailed error logging for debugging
- Continues conversation even if real API unavailable

#### Distance Calculation

- Uses Haversine formula for accurate geographic distances
- Calculates distance from search center to each restaurant
- Returns distances in meters for ranking and display

### Real API Results Example

**Request**:

```json
{
  "textQuery": "Thai restaurant",
  "locationBias": {
    "circle": {
      "center": {"latitude": -37.8136, "longitude": 144.9631},
      "radius": 1000
    }
  },
  "maxResultCount": 20,
  "openNow": true,
  "languageCode": "en"
}
```

**Response** (Real Data from Melbourne, Australia):

- **Kan Eang by Thai Culinary** - 4.8★ - 554m away
- **Number 12 Thai Restaurant** - 4.7★ - 556m away
- **Nisa's Thai Street Food (Melbourne's CBD)** - 4.5★ - 590m away

### Environment Configuration

Edit `.env` to customize:

```bash
GOOGLE_API_KEY=your_key_here
```

Edit `config/settings.py` for:

- Search radius bounds (default: 1000m-5000m based on energy level)
- Price level filtering (1-4 scale)
- Cuisine preferences
- Scoring weights

## Future Enhancements

1. ✅ **Real Google Places Integration**: COMPLETED ✓
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

All dependencies are managed via Pipenv and specified in the `Pipfile`:

**Core Dependencies:**

- `google-adk`: Agent Development Kit for building multi-agent systems
- `google-genai`: Gemini API client library (currently using `gemini-2.5-flash`)
- `fastapi`: Web framework for API endpoints
- `uvicorn`: ASGI server for running FastAPI
- `pydantic`: Data validation using Python type annotations
- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management

**Installation:**

```bash
pipenv install
```

To activate the Pipenv environment:

```bash
pipenv shell
```

To run commands in the Pipenv environment without activating:

```bash
pipenv run <command>
```

## Model Information

### Current Model: Gemini 2.5 Flash

**What is Gemini 2.5 Flash?**

Gemini 2.5 Flash is Google's latest high-performance language model optimized for:

- Fast inference across all modalities
- Multi-turn conversational reasoning
- Better understanding of context and nuance
- Improved instruction following
- Reduced latency compared to previous versions

**Performance Characteristics:**

- Input tokens: Fast processing
- Output tokens: Lower latency
- Context window: 1M tokens
- Ideal for: Real-time applications, conversational AI, multi-agent systems

**Compared to Previous Version (Gemini 2.0 Flash):**

- Better reasoning in complex scenarios
- Improved multi-turn conversation handling
- More reliable response consistency
- Faster inference times
- Better error recovery

**All 10 agents in this system now use Gemini 2.5 Flash** for optimal performance in the restaurant recommendation workflow.

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
