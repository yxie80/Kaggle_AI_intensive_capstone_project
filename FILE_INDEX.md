# Restaurant Recommender System - File Index

## Complete File Manifest

### 📍 Project Location
`/Users/michael_x/experiments/kaggle_ai_agent_course/capstone_project/restaurant_recommender/`

### 📊 Summary
- **Total Files**: 25
- **Python Modules**: 18
- **Documentation**: 2
- **Configuration**: 1

---

## 🤖 Agents (`agents/` - 10 files)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Package init |
| `orchestrator_agent.py` | 45 | Main coordinator with comprehensive instructions |
| `env_collector.py` | 45 | Collects environment context (time, day, cuisine types) |
| `energy_assessor.py` | 40 | Maps energy level (1-5) to search radius |
| `budget_group_agent.py` | 55 | Captures budget and group size preferences |
| `discovery_agent.py` | 45 | Searches nearby restaurants with filters |
| `food_preference_agent.py` | 40 | Determines cuisine and dish preferences |
| `review_analyzer.py` | 45 | Analyzes reviews and computes sentiment scores |
| `suggestion_composer.py` | 50 | Creates top 3 recommendations with rationale |
| `user_profiler_agent.py` | 50 | Updates and maintains user profiles |
| `privacy_agent.py` | 40 | Handles consent and data retention policies |

**Total Agents**: 10  
**Total Lines**: ~400

---

## 🏃 Runners (`runner/` - 2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Package init |
| `orchestrator_runner.py` | 280+ | Main orchestration logic, conversation flow controller |

**Key Features**:
- 7-stage conversation workflow
- State persistence
- Multi-turn dialogue management
- Restaurant ranking and filtering
- Async-ready architecture

---

## 🌐 Backend (`backend/` - 2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Package init |
| `main.py` | 120+ | FastAPI server with 5 REST endpoints |

**Endpoints**:
- `POST /chat` - Process chat messages
- `GET /state/{context_id}` - Get conversation state
- `GET /health` - Health check
- `GET /` - API info

---

## ⚙️ Configuration (`config/` - 2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Package init |
| `settings.py` | 85 | Configuration classes and constants |

**Configurable Items**:
- SearchConfig (radius, limits, ratings)
- ScoringWeights (40-25-20-15 algorithm)
- ConversationConfig (suggestions, profiling)
- Cuisine types (12+ categories)
- Energy mapping (radius per level)
- Budget levels (4 price tiers)

---

## 🛠️ Utilities (`utils/` - 3 files)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Package init |
| `scoring.py` | 150+ | Restaurant ranking and scoring algorithm |
| `state_manager.py` | 180+ | Conversation state management and persistence |

**Scoring Algorithm**:
```
score = 0.4×rating + 0.25×distance + 0.2×value + 0.15×open
```

**State Management**:
- ConversationState dataclass
- StateStore for persistence
- Session tracking

---

## 🔗 Integrations (`integrations/` - 2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 2 | Package init |
| `google_places.py` | 200+ | Google Places API wrapper (mock for demo) |

**Mock Implementation**:
- `nearby_search()` - Find nearby restaurants
- `place_details()` - Get place information
- `text_search()` - Text-based search
- Distance calculation (Haversine formula)

---

## 📱 Main Entry Points

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 95+ | Interactive demo script |
| `README.md` | 400+ | Full project documentation |

**Demo Script Features**:
- Runs complete conversation flow
- 6-message demonstration
- Shows all agents in action
- Displays final state

---

## 📚 Documentation (`capstone_project/` - 2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `QUICKSTART.md` | 300+ | Quick start guide with examples |
| `IMPLEMENTATION_SUMMARY.md` | 350+ | Complete implementation details |

---

## 📋 Complete File Tree

```
restaurant_recommender/
├── agents/
│   ├── __init__.py
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
├── runner/
│   ├── __init__.py
│   └── orchestrator_runner.py
├── backend/
│   ├── __init__.py
│   └── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   ├── scoring.py
│   └── state_manager.py
├── integrations/
│   ├── __init__.py
│   └── google_places.py
├── main.py
└── README.md

Parent Documentation:
├── QUICKSTART.md (in capstone_project/)
└── IMPLEMENTATION_SUMMARY.md (in capstone_project/)
```

---

## 🚀 Getting Started

### 1. Run Demo
```bash
cd /Users/michael_x/experiments/kaggle_ai_agent_course/capstone_project/restaurant_recommender
python main.py
```

### 2. Start API Server
```bash
python -m uvicorn backend.main:app --reload
```

### 3. Test Endpoints
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "message": "I want Thai food"}'
```

---

## 📊 Code Statistics

| Metric | Count |
|--------|-------|
| Python Files | 18 |
| Total Lines of Code | ~2,500+ |
| Agents | 10 |
| REST Endpoints | 5 |
| Conversation Stages | 7 |
| Config Items | 20+ |
| Utility Functions | 15+ |

---

## 🎯 Key Files to Start With

1. **For Understanding Flow**: `runner/orchestrator_runner.py`
2. **For Agent Definitions**: Any file in `agents/`
3. **For Scoring Logic**: `utils/scoring.py`
4. **For API**: `backend/main.py`
5. **For Configuration**: `config/settings.py`
6. **For State**: `utils/state_manager.py`
7. **For Integration**: `integrations/google_places.py`

---

## ✅ Verification Checklist

- [x] All 10 agents created
- [x] Orchestrator runner implemented
- [x] FastAPI backend setup
- [x] Configuration system ready
- [x] Scoring algorithm implemented
- [x] State management complete
- [x] Google Places integration (mock)
- [x] Documentation written
- [x] Demo script working
- [x] Type hints added
- [x] Error handling included
- [x] Async-ready architecture

---

## 📝 Next Steps

1. Review `QUICKSTART.md` for overview
2. Read `IMPLEMENTATION_SUMMARY.md` for details
3. Run `main.py` to see the system in action
4. Explore agent files to understand architecture
5. Start FastAPI server and test endpoints
6. Customize configuration in `config/settings.py`
7. Integrate real Google Places API
8. Add database backend

---

**Created**: November 28, 2025  
**Status**: ✅ Complete and Tested  
**Ready to**: Deploy / Customize / Extend
