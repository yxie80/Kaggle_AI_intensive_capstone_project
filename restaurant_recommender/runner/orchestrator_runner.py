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
from integrations.google_places import GooglePlacesClient


class OrchestratorRunner:
    """Orchestrator that manages the recommendation flow"""
    
    def __init__(self):
        self.state_store = get_state_store()
        self.conversation_history = []
        self.places_client = GooglePlacesClient()  # Initialize real API client
    
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
            "message": f"Hi! I'm your restaurant recommender. You're reaching me on a {env_data['weekday']} at {env_data['local_time']}. "  #TODO: Asking customer if they want to use current time/location
                      f"To help you find the perfect restaurant, I need to ask you a few things. First, what's your location (city or coordinates)?",
            "next_step": "collect_location" #TODO: why do we use next_step? rahther than chain up agents. ?
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
        
        # Route based on current conversation stage #TODO: refactor to use state machine pattern or sequential agent chaining
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
        """Collect user location with real geocoding"""
        # Use real geocoding API to convert address to coordinates
        geocoding_result = self.places_client.geocode(user_message)
        
        if geocoding_result:
            latitude = geocoding_result["latitude"]
            longitude = geocoding_result["longitude"]
            formatted_address = geocoding_result["formatted_address"]
            
            state.set_location(latitude, longitude)
            self.state_store.save_state(state)
            
            return {
                "context_id": state.context_id,
                "message": f"Got it - {formatted_address}. Now, quick question - have you had a long day, or are you still full of energy? "
                          f"Or somewhere in between?",
                "next_step": "collect_energy",
                "location": {
                    "address": formatted_address,
                    "latitude": latitude,
                    "longitude": longitude
                }
            }
        else:
            # If geocoding fails, ask for more specific location
            return {
                "context_id": state.context_id,
                "message": f"I couldn't find that location. Could you please be more specific? (e.g., 'Sydney CBD, Australia' or provide coordinates like '40.7128, -74.0060')",
                "next_step": "collect_location"
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
        """Discover restaurants using real Google Places API"""
        cuisine = state.preferred_cuisine or "Thai"
        
        # Get price level filter based on budget
        budget_to_price_level = {
            1: [1],
            2: [1, 2],
            3: [2, 3],
            4: [3, 4]
        }
        budget = state.budget_level or 2
        price_levels = budget_to_price_level.get(budget, [1, 2, 3])
        
        # Verify location is set
        if not state.location or ("lat" not in state.location and "latitude" not in state.location):
            return {
                "context_id": state.context_id,
                "message": "I need a valid location to search. Could you please provide your location again?",
                "next_step": "collect_location"
            }
        
        # Get coordinates (handle both "lat"/"lng" and "latitude"/"longitude" keys)
        latitude = state.location.get("latitude") or state.location.get("lat")
        longitude = state.location.get("longitude") or state.location.get("lng")
        
        if not latitude or not longitude:
            return {
                "context_id": state.context_id,
                "message": "I need a valid location to search. Could you please provide your location again?",
                "next_step": "collect_location"
            }
        
        # Call real Google Places API
        candidates = self.places_client.nearby_search(
            latitude=latitude,
            longitude=longitude,
            radius_m=state.search_radius_m,
            keyword=cuisine,
            type_filter="restaurant",
            price_level=price_levels,
            open_now=True
        )
        
        # Filter candidates by cuisine preference (post-processing since API doesn't filter by cuisine)
        cuisine_keywords = {
            "Thai": ["thai", "pad thai", "tom yum"],
            "Japanese": ["japanese", "sushi", "ramen", "izakaya", "tonkatsu"],
            "Italian": ["italian", "pizza", "pasta", "trattoria"],
            "Mexican": ["mexican", "taco", "burrito", "cantina"],
            "Indian": ["indian", "curry", "tandoor", "biryani"],
            "Chinese": ["chinese", "dim", "cantonese", "peking"]
        }
        
        cuisine_filters = cuisine_keywords.get(cuisine, [cuisine.lower()])
        
        filtered_candidates = []
        for candidate in candidates:
            name_lower = candidate.get("name", "").lower()
            types = candidate.get("types", [])
            # Check if any cuisine keyword appears in the restaurant name or if types include cuisine-related tags
            if any(keyword in name_lower for keyword in cuisine_filters):
                filtered_candidates.append(candidate)
        
        # If we have filtered results, use them; otherwise log what we found for debugging
        if filtered_candidates:
            candidates = filtered_candidates
        else:
            # If no exact cuisine match, just use all restaurants (fallback)
            # This handles cases where cuisine names don't appear explicitly
            pass
        
        # Limit to top 20 results
        candidates = candidates[:20]
        
        if not candidates:
            return {
                "context_id": state.context_id,
                "message": f"I couldn't find any open {cuisine} restaurants in that area. Let me try a different search...",
                "next_step": "discover_restaurants"
            }
        
        # Add value scores to candidates
        for candidate in candidates:
            candidate["value_score"] = (candidate.get("rating", 3) / 5.0) * 0.7 + (1 - candidate.get("price_level", 2) / 4.0) * 0.3
        
        state.set_candidates(candidates)
        self.state_store.save_state(state)
        
        return {
            "context_id": state.context_id,
            "message": f"Found {len(candidates)} great {cuisine} restaurants! Analyzing reviews...",
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
                "open_until": restaurant.get("opening_hours_snippet", "Check availability"),
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
                    "message": f"Great choice! I'm booking **{selected['name']}** for you. " # TODO: integrate booking API from google maps after checking customer preference
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
        "Melbourne CBD in Australia",
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
