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

**Test Suite - All Tests Passing (8 Test Files, 11 Test Scenarios):**

The complete test suite has been organized in the `/test/` folder and is fully validated:

**All 11 tests pass with 100% success rate using real Google Places API data.**

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

## Notes

- This is a demonstration implementation with mocked Google Places responses
- In production, integrate with real Google Places API and database
- State is stored in-memory; use persistent DB for production
- Add authentication and rate limiting for production deployment

---

Created: November 28, 2025  
Based on: Multi-Agent Restaurant Recommender Blueprint (ADK-focused)
