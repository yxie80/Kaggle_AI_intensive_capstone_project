"""Main orchestrator runner for the restaurant recommendation system"""

import asyncio
from typing import Dict, Any, Optional
from agents.orchestrator_agent import orchestrator_agent
from agents.env_collector import env_collector_agent, get_env_data
from agents.energy_assessor import energy_assessor_agent
from agents.budget_group_agent import budget_group_agent
from agents.discovery_agent import discovery_agent
from agents.food_preference_agent import food_preference_agent
from agents.review_analyzer import review_analyzer_agent
from agents.suggestion_composer import suggestion_composer_agent
from agents.user_profiler_agent import user_profiler_agent
from agents.privacy_agent import privacy_agent
from utils.state_manager import ConversationState, get_state_store


class OrchestratorRunner:
    """Orchestrator that manages the recommendation flow"""
    
    def __init__(self):
        self.state_store = get_state_store()
        self.conversation_history = []
    
    async def start_conversation(self, user_id: str, user_message: str) -> Dict[str, Any]:
        """
        Start a new conversation
        
        Args:
            user_id: Unique user identifier
            user_message: Initial user message
            
        Returns:
            Response dict with context_id and initial orchestrator response
        """
        # Create new conversation state
        state = self.state_store.create_state(user_id)
        
        # Greet user and collect environment data
        env_data = get_env_data()
        
        response = {
            "context_id": state.context_id,
            "user_id": user_id,
            "status": "started",
            "environment": env_data,
            "message": f"Hi! I'm your restaurant recommender. You're reaching me on a {env_data['weekday']} at {env_data['local_time']}. "
                      f"To help you find the perfect restaurant, I need to ask you a few things. First, what's your location (city or coordinates)?",
            "next_step": "collect_location"
        }
        
        return response
    
    async def process_message(self, context_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user message and advance conversation
        
        Args:
            context_id: Conversation context ID
            user_message: User's message
            
        Returns:
            Response dict with next step
        """
        state = self.state_store.get_state(context_id)
        if not state:
            return {"error": "Context not found"}
        
        # Route based on current conversation stage
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
    
    async def _collect_location(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Collect user location"""
        # Parse location (simplified - in production use geocoding API)
        # For now, use default coordinates (New York)
        state.set_location(40.7128, -74.0060)
        self.state_store.save_state(state)
        
        return {
            "context_id": state.context_id,
            "message": "Great! I've got your location. Now, quick question - have you had a long day, or are you still full of energy? "
                      "Or somewhere in between?",
            "next_step": "collect_energy",
            "location": state.location
        }
    
    async def _collect_energy(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Collect energy level"""
        try:
            energy = int(user_message.strip().split()[0])
            if 1 <= energy <= 5:
                state.set_energy_level(energy)
                self.state_store.save_state(state)
                
                energy_desc = {
                    1: "very tired",
                    2: "tired",
                    3: "moderate energy",
                    4: "energetic",
                    5: "very energetic"
                }.get(energy, "moderate")
                
                return {
                    "context_id": state.context_id,
                    "message": f"Got it - you're feeling {energy_desc}. I'll search within {state.search_radius_m}m. "
                              f"Next up: what's your budget? Thinking casual and affordable, comfortable mid-range, or a nicer experience?",
                    "next_step": "collect_budget",
                    "energy": energy,
                    "search_radius_m": state.search_radius_m
                }
        except (ValueError, IndexError):
            pass
        
        # Try to understand from natural language keywords
        message_lower = user_message.lower()
        tired_keywords = ["tired", "long day", "exhausted", "drained", "worn out"]
        energetic_keywords = ["energy", "ready", "adventure", "explore", "enthusiastic"]
        
        if any(kw in message_lower for kw in tired_keywords):
            energy = 2
            state.set_energy_level(energy)
            self.state_store.save_state(state)
            return {
                "context_id": state.context_id,
                "message": f"Sounds like you've had a long day! No problem - I'll search nearby (within {state.search_radius_m}m). "
                          f"So, budget-wise - are you thinking casual, mid-range, or something special?",
                "next_step": "collect_budget",
                "energy": energy
            }
        elif any(kw in message_lower for kw in energetic_keywords):
            energy = 4
            state.set_energy_level(energy)
            self.state_store.save_state(state)
            return {
                "context_id": state.context_id,
                "message": f"Awesome! You're ready to explore. I'll expand my search to {state.search_radius_m}m. "
                          f"Budget check - casual and affordable, mid-range comfort, or treating yourself?",
                "next_step": "collect_budget",
                "energy": energy
            }
        else:
            # Default to moderate
            energy = 3
            state.set_energy_level(energy)
            self.state_store.save_state(state)
            return {
                "context_id": state.context_id,
                "message": f"Got it - moderate energy. I'll search within {state.search_radius_m}m. "
                          f"Budget question: affordable, mid-range, or upscale?",
                "next_step": "collect_budget",
                "energy": energy
            }
    
    async def _collect_budget_group(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Collect budget and group size with natural language"""
        parts = user_message.lower().split()
        
        # Enhanced budget keyword mapping
        budget_keywords = {
            "cheap": 1, "budget": 1, "$": 1, "affordable": 1, "casual": 1, "quick": 1,
            "mid": 2, "moderate": 2, "$$": 2, "comfortable": 2, "normal": 2, "regular": 2,
            "upscale": 3, "$$$": 3, "nice": 3, "good": 3,
            "fancy": 4, "expensive": 4, "$$$$": 4, "special": 4, "splurge": 4
        }
        
        # Find budget from keywords
        budget = None
        for part in parts:
            if part in budget_keywords:
                budget = budget_keywords[part]
                break
        
        if not budget:
            return {
                "context_id": state.context_id,
                "message": "Not quite sure about your budget. Are you thinking casual and affordable, mid-range comfort, or a nicer experience?",
                "next_step": "collect_budget"
            }
        
        budget_desc_map = {
            1: "casual and affordable",
            2: "comfortable mid-range",
            3: "nice upscale",
            4: "fancy special"
        }
        budget_desc = budget_desc_map.get(budget, "mid-range")
        
        state.set_budget(budget, 2)  # Default group size = 2
        self.state_store.save_state(state)
        
        return {
            "context_id": state.context_id,
            "message": f"Perfect - {budget_desc} it is! One more thing: how many people will you be dining with? Just you, or bringing company?",
            "next_step": "collect_group_size",
            "budget": budget,
            "budget_desc": budget_desc
        }
    
    async def _collect_cuisine(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Collect cuisine preference and parse group size"""
        from config.settings import CUISINE_TYPES
        
        # First, try to extract group size from the message
        words = user_message.lower().split()
        try:
            # Look for numbers that might indicate group size
            for word in words:
                if word.isdigit():
                    group_size = int(word)
                    if 1 <= group_size <= 20:
                        state.group_size = group_size
                        break
        except ValueError:
            pass
        
        # Check for group size keywords
        group_keywords = {
            "just me": 1, "alone": 1, "myself": 1,
            "two": 2, "couple": 2, "us": 2,
            "three": 3, "few": 3,
            "four": 4, "family": 4,
            "group": 5, "friends": 5
        }
        
        for kw, size in group_keywords.items():
            if kw in user_message.lower():
                state.group_size = size
                break
        
        # Match cuisine - case-insensitive matching
        message_lower = user_message.lower()
        cuisine = None
        for c in CUISINE_TYPES:
            if c.lower() in message_lower:
                cuisine = c
                break
        
        # If no exact match, try partial matching
        if not cuisine:
            for c in CUISINE_TYPES:
                if c.lower()[:3] in message_lower:  # Match first 3 letters
                    cuisine = c
                    break
        
        # Default to the first cuisine type if none found
        cuisine = cuisine or (CUISINE_TYPES[0] if CUISINE_TYPES else "Thai")
        
        state.set_cuisine_preference(cuisine)
        self.state_store.save_state(state)
        
        group_desc = {
            1: "solo",
            2: "as a couple",
            3: "as a small group",
            4: "as a family",
            5: "with your friends"
        }.get(state.group_size or 2, f"for {state.group_size or 2} people")
        
        return {
            "context_id": state.context_id,
            "message": f"Excellent! I'm searching for amazing {cuisine} restaurants {group_desc}. Let me find the perfect spots...",
            "next_step": "discover_restaurants",
            "cuisine": cuisine,
            "group_size": state.group_size
        }
    
    async def _discover_restaurants(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Discover restaurants matching criteria"""
        # Generate mock restaurant data based on requested cuisine
        cuisine = state.preferred_cuisine or "Thai"
        
        # Restaurant name templates based on cuisine
        name_templates = {
            "Thai": ["Golden Thai Kitchen", "Pad Thai Express", "Thai Orchid Fine Dining"],
            "Italian": ["Bella Italia Restaurant", "Pasta Perfetto", "Italian Trattoria Fine Dining"],
            "Japanese": ["Golden Sushi Bar", "Tokyo Express", "Sakura Fine Dining"],
            "Mexican": ["Casa Mexico", "Taco Express", "El Pueblo Fine Dining"],
            "Indian": ["Taj Mahal Cuisine", "Curry Express", "Maharaja Fine Dining"],
            "Chinese": ["Golden Dragon", "Beijing Express", "Dynasty Fine Dining"]
        }
        
        names = name_templates.get(cuisine, [f"{cuisine} Restaurant 1", f"{cuisine} Express", f"{cuisine} Fine Dining"])
        
        # Simulated restaurant data (in production, call Google Places API)
        candidates = [
            {
                "place_id": "place_1",
                "name": names[0],
                "latitude": 40.7128,
                "longitude": -74.0060,
                "distance_m": 800,
                "price_level": 2,
                "rating": 4.5,
                "user_ratings_total": 150,
                "open_now": True,
                "opening_hours_snippet": "Open until 21:30",
                "value_score": 0.85
            },
            {
                "place_id": "place_2",
                "name": names[1],
                "latitude": 40.7150,
                "longitude": -74.0080,
                "distance_m": 1200,
                "price_level": 1,
                "rating": 4.2,
                "user_ratings_total": 200,
                "open_now": True,
                "opening_hours_snippet": "Open until 22:00",
                "value_score": 0.9
            },
            {
                "place_id": "place_3",
                "name": names[2],
                "latitude": 40.7100,
                "longitude": -74.0050,
                "distance_m": 1500,
                "price_level": 3,
                "rating": 4.7,
                "user_ratings_total": 320,
                "open_now": True,
                "opening_hours_snippet": "Open until 23:00",
                "value_score": 0.75
            }
        ]
        
        state.set_candidates(candidates)
        self.state_store.save_state(state)
        
        return {
            "context_id": state.context_id,
            "message": f"Found {len(candidates)} great {state.preferred_cuisine} restaurants! Analyzing reviews...",
            "next_step": "analyze_and_compose",
            "candidates_count": len(candidates)
        }
    
    async def _compose_recommendations(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Compose top 3 recommendations"""
        from utils.scoring import rank_restaurants
        
        # Score and rank candidates
        top_3 = rank_restaurants(state.candidates, top_n=3)
        
        recommendations = []
        for i, restaurant in enumerate(top_3, 1):
            recommendations.append({
                "rank": i,
                "place_id": restaurant["place_id"],
                "name": restaurant["name"],
                "rating": restaurant["rating"],
                "price_level": restaurant["price_level"],
                "distance_m": restaurant["distance_m"],
                "open_until": restaurant["opening_hours_snippet"],
                "score": round(restaurant.get("composite_score", 0), 2),
                "rationale": f"Excellent {state.preferred_cuisine} option with {restaurant['rating']}★ rating, "
                           f"{restaurant['distance_m']}m away"
            })
        
        state.set_recommendations(recommendations)
        self.state_store.save_state(state)
        
        msg = "Here are my top 3 recommendations:\n\n"
        for rec in recommendations:
            msg += f"{rec['rank']}. **{rec['name']}** ({rec['rating']}★) - {rec['distance_m']}m away\n"
            msg += f"   {rec['rationale']}\n\n"
        msg += "Which one would you like? (Enter 1, 2, or 3)"
        
        return {
            "context_id": state.context_id,
            "message": msg,
            "next_step": "select_restaurant",
            "recommendations": recommendations
        }
    
    async def _handle_user_choice(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Handle user's restaurant selection"""
        try:
            choice = int(user_message.strip().split()[0])
            if 1 <= choice <= 3 and choice <= len(state.recommendations):
                selected = state.recommendations[choice - 1]
                state.select_restaurant(selected)
                self.state_store.save_state(state)
                
                return {
                    "context_id": state.context_id,
                    "message": f"Great choice! I'm booking **{selected['name']}** for you. "
                              f"You can visit them now - they're open until {selected['open_until']}. "
                              f"Enjoy your meal! Rate your experience when you're done.",
                    "next_step": "complete",
                    "selected": selected
                }
        except (ValueError, IndexError):
            pass
        
        return {
            "context_id": state.context_id,
            "message": "I didn't understand that. Please enter 1, 2, or 3 to select a restaurant.",
            "next_step": "select_restaurant"
        }


async def run_orchestrator_demo():
    """Demo orchestrator flow"""
    runner = OrchestratorRunner()
    
    # Start conversation
    result = await runner.start_conversation("user_123", "Hi, I'm hungry!")
    print("START:", result)
    print()
    
    # Simulate conversation flow
    messages = [
        "New York",
        "3",
        "mid-range",
        "Thai",
        "test"
    ]
    
    context_id = result["context_id"]
    
    for msg in messages:
        result = await runner.process_message(context_id, msg)
        print(f"USER: {msg}")
        print(f"RESPONSE: {result.get('message', result)}")
        print()


if __name__ == "__main__":
    asyncio.run(run_orchestrator_demo())
