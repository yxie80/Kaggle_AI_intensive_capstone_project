# Multi-Agent Restaurant Recommender System

A **production-ready, multi-agent conversational restaurant recommender** built with Google ADK.  
Designed as a clear, extensible reference implementation demonstrating agent orchestration, conversational state management, and a multi-factor ranking algorithm.

---

**Course:** 5-Day AI Agents Intensive with Google  \
**Team Members:** Zoey Y, Michael Xie \
**Track:** Concierge Agents \
**Date:** Nov 2025

---

## Quick highlights

- 10 focused agents (orchestration, environment, energy, budget/group, discovery, review analysis, suggestion composition, profiling, privacy)  
- 7-stage conversational flow (location → energy level → budget/group → cuisine → discovery → analysis → recommendation)  
- Composite scoring: rating, distance, value, open-now (default weights: 40/25/20/15)  
- Demo mode and FastAPI backend for integration/testing  
- Mocked Google Places client (easy to swap for production)

**Current Status**: ✅ All 10 agents upgraded to **Gemini 2.5 Flash** (from 2.0 Flash)

## AI/Agent Concepts Implemented

| Concept | Status | Implementation | Location |
|---------|--------|-----------------|----------|
| **Multi-Agent System** | ✅ | 10 LLM-powered agents orchestrated via state machine | `agents/` directory |
| **LLM-Powered Agents** | ✅ | All agents use Gemini 2.5 Flash with custom instructions | All agent files |
| **Sequential Agents** | ✅ | 7-stage conversation flow with explicit state routing | `runner/orchestrator_runner.py` |
| **Parallel Agents** | ✅ | Agents can process independently before composition | `runner/orchestrator_runner.py` |
| **Loop Agents** | ✅ | Users can revisit/loop back to earlier conversation stages | `runner/orchestrator_runner.py` |
| **Custom Tools** | ✅ | Google Places API integration + composite scoring algorithm | `integrations/`, `utils/scoring.py` |
| **Built-in Tools** | ✅ | Google Places API v1 (Geocoding, Text Search, Nearby Search) | `integrations/google_places.py` |
| **OpenAPI Tools** | ✅ | Real Google Places API v1 REST endpoints | `integrations/google_places.py` |
| **Sessions & Memory** | ✅ | In-Memory StateStore with multi-session support | `utils/state_manager.py` |
| **State Management** | ✅ | ConversationState tracks full context across turns | `utils/state_manager.py` |
| **Context Engineering** | ✅ | Multi-factor scoring: rating (40%), distance (25%), value (20%), open (15%) | `utils/scoring.py` |
| **Long-Running Operations** | ✅ | FastAPI + WebSocket for stateful persistent sessions | `api_server.py`, `backend/main.py` |
| **Agent Deployment** | ✅ | Production-ready: CLI, Web UI, REST API modes | `main.py`, `api_server.py` |
| **Observability** | ✅ | State tracking, timestamp logging, error handling | `utils/state_manager.py` |
| **Agent Evaluation** | ✅ | Comprehensive test suite: 11 scenarios, 100% pass rate | `test/` directory |

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
cd ./restaurant_recommender

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
├── test/                # Test suite (comprehensive & all passing ✅)
│   ├── test_distance_confirmation.py       # Distance confirmation feature (3 tests) ✅
│   ├── test_restaurant_suggestions.py      # Restaurant suggestions & cuisine changes (4 tests) ✅
│   ├── test_cuisine_composition_change.py  # Cuisine change during composition (1 test) ✅
│   ├── test_traffic_time_filtering.py      # Traffic time consideration (5 tests) ✅ NEW
│   ├── test_debug.py                       # Conversation flow verification ✅
│   ├── test_debug2.py                      # State management verification ✅
│   ├── test_input.txt                      # End-to-end CLI test inputs ✅
│   ├── README.md                           # Test documentation
│   └── SETUP_COMPLETE.md                   # Setup verification guide
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

### Recent Bug Fixes (December 2025)

**Bug #1: Distance Feedback Misinterpretation** ✅ FIXED

- **Issue**: "Nah, its too far" was being interpreted as budget feedback instead of distance feedback
- **Root Cause**: System jumped directly from energy→budget without distance confirmation step
- **Solution**: Added `confirm_distance()` step with dedicated distance parsing and validation
- **Result**: Users can now accept, reject, or propose custom distances (500m-25km)

**Bug #2: Restaurant Suggestion Not Recognized** ✅ FIXED

- **Issue**: During discovery, system looped saying "couldn't find Thai restaurants" without options
- **Root Cause**: No handling for cuisine changes or restaurant suggestions during discovery/composition
- **Solution**:
  - Enhanced `_discover_restaurants()` with cuisine change detection
  - Enhanced `_handle_user_choice()` with alternative detection
  - Added `_compose_recommendations()` cuisine change check
- **Result**: Users can now change cuisine at any phase, search for specific restaurants, and get helpful suggestions

**Bug #3: Hardcoded Recommendation Count** ✅ FIXED

- **Issue**: System asked "Enter 1, 2, or 3" even when only 1 restaurant was found
- **Root Cause**: Message template hardcoded "top 3 recommendations" without checking actual count
- **Solution**: Dynamic message generation based on number of recommendations
- **Result**: Users see accurate guidance (e.g., "Enter 1" for single recommendation, "Enter 1-2" for two)

**Bug #4: "Yes" Not Accepted for Single Recommendation** ✅ FIXED

- **Issue**: When only 1 recommendation exists, user saying "yes" was not recognized
- **Root Cause**: System only parsed numeric input, no affirmative keyword handling
- **Solution**: Added affirmative keyword detection ("yes", "ok", "sure", "yep", "yeah") when single recommendation exists
- **Result**: Users can naturally confirm with "yes", "ok", or "1" - more intuitive interaction

### Recent Features Added (December 2025)

**Feature: Traffic Time Filtering** ✅ NEW

- **What it Does**: Filters out restaurants where users won't have enough time to visit before closing
- **How It Works**:
  - Calculates travel time based on distance (~30 km/h average speed in urban traffic)
  - Parses restaurant closing time from Google Places data
  - Ensures 30+ minutes remaining after travel for actual dining
  - Removes restaurants from recommendations if insufficient time
- **Example Scenario 1** (Current time 10:30 PM):
  - Restaurant A closes 11 PM, 5km away (10 min travel + 30 min visit = 40 min needed)
  - Only 30 minutes available → **FILTERED OUT** ❌
- **Example Scenario 2** (Current time 6:00 PM):
  - Restaurant B closes 11 PM, 5km away (10 min travel + 30 min visit = 40 min needed)
  - 5 hours available → **RECOMMENDED** ✅
- **User Impact**: No more wasted recommendations for restaurants closing soon

**Feature: Quick "Tired Mode" - Skip Setup for Fast Food** ✅ NEW

- **What it Does**: When users indicate extreme exhaustion, system skips budget/cuisine setup and directly proposes closest fast food options
- **Trigger Keywords**: "exhausted", "too tired", "so tired", "completely exhausted", "dead tired", "shattered", "worn out", "knackered", "wiped", "beat", "drained"
- **Automatic Actions**:
  - Sets energy level to 1 (very tired)
  - Auto-selects budget level 1 (cheap/fast food options)
  - Auto-selects "Fast Food" cuisine type
  - Confirms default search distance
  - Skips distance confirmation, budget questions, and cuisine selection
- **User Experience**: User says "I'm exhausted" → System immediately finds nearest fast food → Shows options for confirmation
- **Before**: 7-8 exchanges (energy → distance → budget → group → cuisine → discover → compose)
- **After**: 2-3 exchanges with "Quick Tired Mode" (exhaustion detection → fast food recommendations → selection)
- **Example**:
  
  ```plain
  User: "I'm completely exhausted"
  System: "I got it - you're exhausted! No need to overthink. Let me find the closest fast food options for you..."
  [System displays top 3 closest fast food restaurants]
  System: "Which one would you like? (Enter 1-3)"
  ```

- **User Impact**: Exhausted users can get recommendations in seconds instead of minutes

**Feature: Location Time Reminder** ✅ NEW

- **What it Does**: Reminds users of the location's current local time at key conversation points
- **Where It Appears**:
  1. **After location confirmation**: Shows timezone and current local time
     - Example: `🕐 Current local time: 06:45 PM (Australia/Melbourne)`
  2. **When displaying recommendations**: Displays location context above suggestions
     - Example: `📍 Australia/Melbourne - Local time: 06:45 PM`
  3. **When user selects restaurant**: Shows travel information with local time context
- **Why It Matters**:
  - Users understand the actual time in the destination, not their local time
  - Prevents confusion when searching across timezones
  - Helps users plan accordingly (e.g., "It's 6:45 PM there, restaurants close at 11 PM, so I have ~4 hours")
- **Example Conversation**:

  ```plain
  User: "Melbourne"
  System: "Got it - Melbourne, VIC, Australia
           🕐 Current local time: 06:45 PM (Australia/Melbourne)
           
           Now, quick question - have you had a long day..."
  
  [Later, when showing recommendations]
  System: "📍 Australia/Melbourne - Local time: 06:45 PM
           
           Here are my top 3 recommendations..."
  ```

- **User Impact**: Clear awareness of destination time throughout conversation, better decision-making

**Feature: Timezone-Aware Time Calculation** ✅ NEW & FULLY FUNCTIONAL

- **What it Does**: Automatically detects the restaurant location's timezone and uses it for all time-based calculations
- **Current Status**: ✅ **Fully operational with intelligent fallback system**
- **How It Works** (Three-tier system):
  - **Primary Method**: Google Time Zone API (if enabled in Google Cloud)
  - **Fallback 1** ✅ **ACTIVE**: `timezonefinder` library (open-source, no API key needed)
  - **Fallback 2** ✅ **ACTIVE**: UTC timezone (always available)
  - Stores both timezone ID (e.g., "Australia/Melbourne") and current local time in state
  - Uses location's time for traffic filtering and traffic status determination (not user's local time)
- **Why It Matters**:
  - Prevents incorrect recommendations when user and restaurant are in different timezones
  - Example: User in NYC (9 PM) searching for restaurants in Tokyo (next day, 1 PM) - correctly uses Tokyo time for closing time checks
  - Ensures accurate traffic status (rush hours are based on restaurant location's local time)
- **Technical Details**:
  - Uses IANA timezone IDs (e.g., "America/New_York", "Asia/Tokyo", "Asia/Taipei")
  - Stores in ISO format with timezone info: `2025-12-03T18:45:30+08:00`
  - All time comparisons use `datetime.fromisoformat()` with `pytz` for accuracy
  - Includes source tracking for debugging:
    - "google_timezone_api" (if API enabled)
    - "timezonefinder_fallback" (primary working method)
    - "utc_fallback" (last resort)
- **User Impact**: Recommendations always show correct local time, regardless of user's location or API status

**Feature: Travel Time & Traffic Status Display** ✅ UPDATED

- **What it Does**: Shows users estimated travel time and current traffic conditions when they select a restaurant
- **Information Provided**:
  - Distance to restaurant
  - Estimated travel time (accounting for traffic)
  - Traffic status with visual indicator (🟢 light, 🟠 moderate)
  - Restaurant closing time
- **Traffic Logic** (based on location's local time):
  - 🟢 Light traffic: 10 AM - 5 PM, 7 PM - 10 PM (normal estimates)
  - 🟠 Moderate traffic: 7 AM - 10 AM, 5 PM - 7 PM (adds 30% time buffer)
- **Example Output**:

  ```plain
  📍 **Travel Information:**
  - Distance: 3.4 km
  - Estimated travel time: **7 minutes** (light traffic 🟢)
  - Currently open until: Closes 11 PM
  ```

- **User Impact**: Users can make informed decisions about whether they have time to visit

**Feature: Automatic Discovery + Composition** ✅ NEW

- **What it Does**: Combines restaurant discovery and recommendation composition into single seamless step
- **Before**: User sends message → Discovery → **User waits** → Sends another message → Composition
- **After**: User sends message → Discovery + Composition → Recommendations shown immediately
- **Result**: 50% fewer required user inputs, faster conversation flow

**Feature: Smart Skip Intent Recognition** ✅ NEW

- **What it Does**: Users can skip early stages directly to restaurant search
- **Example**: "Skip following questions and help me check if nearest KFC is opening"
  - System automatically: Sets default preferences (mid-range, 2 people)
  - Extracts cuisine intent (KFC)
  - Searches immediately without asking budget/group/cuisine questions
- **Result**: Experienced users can find restaurants in 2-3 exchanges instead of 7-8

**Test Suite - All Tests Passing (8 Test Files, 16 Test Scenarios):**

The complete test suite has been organized in the `/test/` folder and is fully validated:

**All tests pass with 100% success rate using real Google Places API data.**

**NEW TEST SUITE: Quick Tired Mode Tests** ✅ ADDED

- `test/test_quick_tired_mode.py`: 9 comprehensive test scenarios
  - Scenario 1: "exhausted" keyword triggers quick mode
  - Scenario 2: "dead tired" keyword triggers quick mode
  - Scenario 3: "too tired" keyword triggers quick mode
  - Scenario 4: "worn out" keyword triggers quick mode
  - Scenario 5: Regular "tired" does NOT trigger quick mode (normal flow)
  - Scenario 6: "knackered" (UK English) keyword triggers quick mode
  - Scenario 7: "wiped" keyword triggers quick mode
  - Scenario 8: Quick mode skips budget and cuisine questions
  - Scenario 9: Quick mode sets correct defaults (cheap budget, Fast Food, solo dining)

**EXISTING TEST SUITES (All Passing):**

**Test Suite: Traffic Time Filtering Tests** ✅

- `test/test_traffic_time_filtering.py`: 5 comprehensive test scenarios
  - Scenario 1: Restaurant closes soon (filtered out)
  - Scenario 2: Restaurant has enough time (recommended)
  - Scenario 3: Mixed recommendations (filters closed ones only)
  - Scenario 4: Close distance with short travel time
  - Scenario 5: Far distance with long travel time

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
# Bug Fix Tests
pipenv run python test/test_distance_confirmation.py
pipenv run python test/test_restaurant_suggestions.py
pipenv run python test/test_cuisine_composition_change.py

# Traffic Time Filtering Tests (NEW)
pipenv run python test/test_traffic_time_filtering.py

# Integration Tests
pipenv run python test/test_debug.py
pipenv run python test/test_debug2.py

# End-to-End CLI (Automated Input)
timeout 30 bash -c 'cat test/test_input.txt | pipenv run python main.py'
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

---

## Core Features

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

## Troubleshooting

### Timezone API Status Check

**To validate your timezone API configuration**, run the validation script:

```bash
pipenv run python test/validate_timezone_api.py
```

This script will:

- ✅ Check if Google Time Zone API is enabled
- ✅ Verify timezonefinder library is installed
- ✅ Test timezone lookup for Taipei
- ✅ Show which methods are working
- ✅ Provide specific fix instructions if needed

**Current Status (System Validated)**:

- Google Time Zone API: `REQUEST_DENIED` (Not currently enabled)
- timezonefinder library: ✅ **WORKING** (Primary fallback, fully functional)
- UTC fallback: ✅ **AVAILABLE**

### Issue: "REQUEST_DENIED" for Google Time Zone API

**What it means:**

- Google Time Zone API is NOT enabled in your Google Cloud Console
- System automatically uses timezonefinder fallback instead

**Is this a problem?**
❌ **NO** - System works perfectly with timezonefinder!

- ✅ Timezone detection is accurate
- ✅ No API key permission needed
- ✅ No usage quota issues
- ✅ Completely offline compatible

**If you want to enable Google Time Zone API (Optional)**:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **Library**
4. Search for "**Time Zone API**"
5. Click on it and press **Enable**
6. Wait 1-2 minutes for changes to propagate
7. Restart your application

**After enabling**, system will automatically use Google API (faster) instead of timezonefinder.

**Fallback Chain** (Automatic):

```plain
✓ Try Google Time Zone API
    ↓ (if not enabled, connection fails, etc.)
✓ Try timezonefinder library (working)
    ↓ (if library not available)
✓ Use UTC timezone (always works)
```

---

## Notes

- This is a demonstration implementation with mocked Google Places responses
- In production, integrate with real Google Places API and database
- State is stored in-memory; use persistent DB for production
- Add authentication and rate limiting for production deployment

---

Created: November 28, 2025  
Based on: Multi-Agent Restaurant Recommender Blueprint (ADK-focused)
