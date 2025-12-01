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
        
        # Route based on explicit state machine pattern with next_step routing
        # This design is preferred for user-interactive multi-turn conversations over agent chaining
        # See README section "Architecture: next_step Pattern vs. Agent Chaining" for detailed rationale
        if not state.location:
            return await self._collect_location(state, user_message)
        
        elif state.energy_level is None:
            return await self._collect_energy(state, user_message)
        
        elif not hasattr(state, 'distance_confirmed') or not state.distance_confirmed:
            return await self._confirm_distance(state, user_message)
        
        elif state.budget_level is None or state.group_size is None:
            return await self._collect_budget_group(state, user_message)
        
        elif state.preferred_cuisine is None:
            return await self._collect_cuisine(state, user_message)
        
        elif not state.candidates:
            return await self._discover_restaurants(state, user_message)
        
        elif not state.recommendations:
            return await self._compose_recommendations(state, user_message)
        
        else:
            # Handle both restaurant selection and user feedback/changes
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
                              f"Does that search distance work for you, or would you prefer a different range?",
                    "next_step": "confirm_distance",
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
                          f"Is that distance okay for you, or would you prefer a different range?",
                "next_step": "confirm_distance",
                "energy": energy,
                "search_radius_m": state.search_radius_m
            }
        elif any(kw in message_lower for kw in energetic_keywords):
            energy = 4
            state.set_energy_level(energy)
            self.state_store.save_state(state)
            return {
                "context_id": state.context_id,
                "message": f"Awesome! You're ready to explore. I'll expand my search to {state.search_radius_m}m. "
                          f"Does that search range work for you?",
                "next_step": "confirm_distance",
                "energy": energy,
                "search_radius_m": state.search_radius_m
            }
        else:
            # Default to moderate
            energy = 3
            state.set_energy_level(energy)
            self.state_store.save_state(state)
            return {
                "context_id": state.context_id,
                "message": f"Got it - moderate energy. I'll search within {state.search_radius_m}m. "
                          f"Does that search range work for you, or would you prefer a different distance?",
                "next_step": "confirm_distance",
                "energy": energy,
                "search_radius_m": state.search_radius_m
            }
    
    async def _confirm_distance(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """
        Confirm search distance with user. Allow them to:
        1. Accept the suggested distance
        2. Propose a custom distance
        3. Ask questions about it
        """
        message_lower = user_message.lower()
        
        # Check if user accepts the distance
        accept_keywords = ["yes", "ok", "okay", "perfect", "great", "sounds good", "that's fine", 
                          "that works", "i'm good", "is fine", "looks good", "alright"]
        reject_keywords = ["no", "too far", "too close", "farther", "closer", "too much", "reduce", 
                          "increase", "more", "less", "different"]
        
        if any(kw in message_lower for kw in accept_keywords):
            # User accepts the distance
            state.confirm_distance()
            self.state_store.save_state(state)
            return {
                "context_id": state.context_id,
                "message": f"Perfect! I'll search within {state.search_radius_m}m. "
                          f"Now, budget-wise - are you thinking casual and affordable, mid-range comfort, or treating yourself?",
                "next_step": "collect_budget",
                "distance_m": state.search_radius_m,
                "confirmed": True
            }
        
        # Try to extract custom distance if user proposes one
        words = message_lower.split()
        custom_distance = None
        
        # Look for patterns like "1000m", "1 km", "1000 meters"
        for i, word in enumerate(words):
            # Strip punctuation from word for processing
            word_clean = word.strip('.,!?;:')
            
            # Check for numbers followed by distance units
            if word_clean.replace(',', '').isdigit():
                distance_num = int(word_clean.replace(',', ''))
                # Check if next word has a unit
                if i + 1 < len(words):
                    unit_word = words[i + 1].strip('.,!?;:')
                    if 'km' in unit_word or 'kilometer' in unit_word:
                        custom_distance = distance_num * 1000
                        break
                    elif 'm' in unit_word or 'meter' in unit_word:
                        custom_distance = distance_num
                        break
            # Check for patterns like "1000m" or "1km" as single token
            # Important: must check 'km' before 'm' to avoid matching 'm' in other words
            elif 'km' in word_clean or 'kilometer' in word_clean:
                try:
                    num_str = word_clean.replace('km', '').replace('kilometer', '')
                    if num_str and num_str.isdigit():
                        distance_num = int(num_str)
                        custom_distance = distance_num * 1000
                        break
                except ValueError:
                    pass
            # Then check for meter patterns
            elif word_clean.endswith('m') and any(c.isdigit() for c in word_clean):
                try:
                    num_str = word_clean.replace('m', '').strip()
                    if num_str and num_str.isdigit():
                        distance_num = int(num_str)
                        custom_distance = distance_num
                        break
                except ValueError:
                    pass
        
        # Handle explicit rejection or custom distance request
        if any(kw in message_lower for kw in reject_keywords) or custom_distance:
            if custom_distance:
                # Validate custom distance (reasonable bounds: 500m to 25km)
                if 500 <= custom_distance <= 25000:
                    state.confirm_distance(custom_distance)
                    self.state_store.save_state(state)
                    distance_display = f"{custom_distance/1000:.1f}km" if custom_distance >= 1000 else f"{custom_distance}m"
                    return {
                        "context_id": state.context_id,
                        "message": f"Great! I'll search within {distance_display}. "
                                  f"Now, budget-wise - are you thinking casual and affordable, mid-range comfort, or treating yourself?",
                        "next_step": "collect_budget",
                        "distance_m": custom_distance,
                        "confirmed": True
                    }
                else:
                    # Distance out of valid range
                    return {
                        "context_id": state.context_id,
                        "message": f"That distance seems a bit extreme. Let me suggest a few options:\n"
                                  f"- Close by: 500-1000m\n"
                                  f"- Nearby: 1000-3000m\n"
                                  f"- Wider search: 3000-5000m\n\n"
                                  f"Which range works better for you, or would you like a specific distance in meters/km?",
                        "next_step": "confirm_distance",
                        "current_distance_m": state.search_radius_m
                    }
            
            # User rejected but didn't specify a distance
            return {
                "context_id": state.context_id,
                "message": f"I understand - the {state.search_radius_m/1000:.1f}km range might be too much. "
                          f"What distance would you prefer? You can say something like '1km', '2000m', or pick from:\n"
                          f"- Very close: ~500m\n"
                          f"- Close: ~1000m\n"
                          f"- Moderate: ~2000m\n"
                          f"- Wider: ~5000m",
                "next_step": "confirm_distance",
                "current_distance_m": state.search_radius_m
            }
        
        # User didn't clearly accept or reject
        return {
            "context_id": state.context_id,
            "message": f"Just to confirm - does a {state.search_radius_m/1000:.1f}km search radius work for you, "
                      f"or would you prefer a different distance? (Just say 'yes', 'no', or suggest a distance like '1km' or '500m')",
            "next_step": "confirm_distance",
            "current_distance_m": state.search_radius_m
        }
    
    async def _collect_budget_group(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Collect budget and group size with natural language"""
        message_lower = user_message.lower()
        
        # Multi-word budget patterns (checked first)
        budget_patterns = [
            (["mid-range", "midrange", "mid range"], 2),
            (["casual", "budget", "affordable", "cheap"], 1),
            (["upscale", "fancy", "expensive", "special", "splurge"], 3),
            (["moderate", "comfortable", "normal", "regular"], 2),
        ]
        
        # Check multi-word patterns
        budget = None
        for keywords, budget_level in budget_patterns:
            for keyword in keywords:
                if keyword in message_lower:
                    budget = budget_level
                    break
            if budget:
                break
        
        # Fallback: check single keywords and symbols
        if not budget:
            parts = message_lower.split()
            budget_keywords = {
                "cheap": 1, "budget": 1, "$": 1, "affordable": 1, "casual": 1, "quick": 1,
                "mid": 2, "moderate": 2, "$$": 2, "comfortable": 2, "normal": 2, "regular": 2,
                "upscale": 3, "$$$": 3, "nice": 3, "good": 3,
                "fancy": 4, "expensive": 4, "$$$$": 4, "special": 4, "splurge": 4
            }
            
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
        from config.settings import CUISINE_TYPES
        
        message_lower = user_message.lower().strip()
        
        # Only check for cuisine change if message is explicit (contains keywords like "how about", "try", etc.)
        # and is different from current cuisine
        has_change_keywords = any(kw in message_lower for kw in ["how about", "what about", "try", "change to", 
                                                                   "instead", "switch to", "different"])
        
        if has_change_keywords and message_lower:
            for cuisine in CUISINE_TYPES:
                if cuisine.lower() in message_lower and cuisine.lower() != (state.preferred_cuisine or "thai").lower():
                    # User wants to change cuisine
                    state.set_cuisine_preference(cuisine)
                    state.candidates = []  # Reset candidates
                    self.state_store.save_state(state)
                    
                    return {
                        "context_id": state.context_id,
                        "message": f"Great! Let me search for {cuisine} restaurants instead...",
                        "next_step": "discover_restaurants"
                    }
        
        # Check if user is suggesting a specific restaurant name to search for
        # Keywords that indicate user is proposing a restaurant
        if any(kw in message_lower for kw in ["how about", "what about", "maybe", "probably", "could we try", "can we go to", "let's go to"]):
            # Extract the restaurant name (typically after the keyword)
            parts = message_lower.split()
            potential_restaurant = " ".join(user_message.split()).strip()
            
            # Try searching for this specific restaurant
            if state.location:
                latitude = state.location.get("latitude") or state.location.get("lat")
                longitude = state.location.get("longitude") or state.location.get("lng")
                
                if latitude and longitude:
                    # Search for the specific restaurant
                    try:
                        candidates = self.places_client.text_search(
                            query=potential_restaurant,
                            latitude=latitude,
                            longitude=longitude,
                            radius_m=state.search_radius_m
                        )
                        
                        if candidates:
                            state.set_candidates(candidates[:20])
                            self.state_store.save_state(state)
                            
                            return {
                                "context_id": state.context_id,
                                "message": f"Found {len(candidates)} results for '{potential_restaurant}'. Analyzing...",
                                "next_step": "analyze_and_compose",
                                "candidates_count": len(candidates)
                            }
                        else:
                            return {
                                "context_id": state.context_id,
                                "message": f"I couldn't find '{potential_restaurant}' nearby. Would you like me to search for {state.preferred_cuisine} instead, or try a different restaurant name?",
                                "next_step": "discover_restaurants"
                            }
                    except Exception as e:
                        pass  # Fall through to regular discovery
        
        # If we reach here without finding alternatives, do regular discovery
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
                "message": f"I couldn't find any open {cuisine} restaurants in that area. Would you like to:\n"
                          f"- Try a different cuisine (e.g., 'How about Italian?')\n"
                          f"- Search for a specific restaurant (e.g., 'How about KFC?')\n"
                          f"- Expand the search distance\n\n"
                          f"What would you prefer?",
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
        from utils.scoring import rank_restaurants, format_distance
        from config.settings import CUISINE_TYPES
        
        # First check if user wants to change cuisine before composing
        message_lower = user_message.lower().strip()
        if message_lower:
            # Check for cuisine change requests
            has_change_keywords = any(kw in message_lower for kw in ["how about", "what about", "try", "change to", 
                                                                       "instead", "switch to", "different"])
            
            if has_change_keywords:
                for cuisine in CUISINE_TYPES:
                    if cuisine.lower() in message_lower and cuisine.lower() != (state.preferred_cuisine or "thai").lower():
                        # User wants to change cuisine before even seeing recommendations
                        state.set_cuisine_preference(cuisine)
                        state.candidates = []
                        state.recommendations = []
                        self.state_store.save_state(state)
                        
                        return {
                            "context_id": state.context_id,
                            "message": f"Great! Let me search for {cuisine} restaurants instead...",
                            "next_step": "discover_restaurants"
                        }
        
        # Score and rank candidates
        top_3 = rank_restaurants(state.candidates, top_n=3)
        
        recommendations = []
        for i, restaurant in enumerate(top_3, 1):
            distance_km = format_distance(restaurant["distance_m"])
            recommendations.append({
                "rank": i,
                "place_id": restaurant["place_id"],
                "name": restaurant["name"],
                "rating": restaurant["rating"],
                "price_level": restaurant["price_level"],
                "distance_m": restaurant["distance_m"],
                "distance_display": distance_km,
                "open_until": restaurant.get("opening_hours_snippet", "Check availability"),
                "score": round(restaurant.get("composite_score", 0), 2),
                "rationale": f"Excellent {state.preferred_cuisine} option with {restaurant['rating']}★ rating, {distance_km} away"
            })
        
        state.set_recommendations(recommendations)
        self.state_store.save_state(state)
        
        msg = "Here are my top 3 recommendations:\n\n"
        for rec in recommendations:
            msg += f"{rec['rank']}. **{rec['name']}** ({rec['rating']}★) - {rec['distance_display']} away\n"
            msg += f"   {rec['rationale']}\n\n"
        msg += "Which one would you like? (Enter 1, 2, or 3)"
        
        return {
            "context_id": state.context_id,
            "message": msg,
            "next_step": "select_restaurant",
            "recommendations": recommendations
        }
    
    async def _handle_user_choice(self, state: ConversationState, user_message: str) -> Dict[str, Any]:
        """Handle user's restaurant selection or feedback during recommendations"""
        from config.settings import CUISINE_TYPES
        
        message_lower = user_message.lower()
        
        # First, try to parse as a numeric selection (1, 2, or 3)
        try:
            choice_str = user_message.strip().split()[0] if user_message.strip().split() else ""
            choice = int(choice_str)
            
            if 1 <= choice <= len(state.recommendations):
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
            else:
                return {
                    "context_id": state.context_id,
                    "message": f"Please enter a number between 1 and {len(state.recommendations)} to select a restaurant.",
                    "next_step": "select_restaurant"
                }
        except (ValueError, IndexError):
            pass
        
        # Check if user wants to change cuisine
        for cuisine in CUISINE_TYPES:
            if cuisine.lower() in message_lower:
                # User wants a different cuisine - reset recommendations and candidates
                state.set_cuisine_preference(cuisine)
                state.candidates = []
                state.recommendations = []
                self.state_store.save_state(state)
                
                return {
                    "context_id": state.context_id,
                    "message": f"Got it! Let me search for {cuisine} restaurants for you...",
                    "next_step": "discover_restaurants"
                }
        
        # Check if user is proposing a specific restaurant
        if any(kw in message_lower for kw in ["how about", "what about", "maybe", "probably", "could we try", 
                                               "can we go to", "let's go to", "i prefer", "i'd like", "try"]):
            # Extract potential restaurant name
            potential_restaurant = user_message.strip()
            
            # Try searching for this specific restaurant
            if state.location:
                latitude = state.location.get("latitude") or state.location.get("lat")
                longitude = state.location.get("longitude") or state.location.get("lng")
                
                if latitude and longitude:
                    try:
                        candidates = self.places_client.text_search(
                            query=potential_restaurant,
                            latitude=latitude,
                            longitude=longitude,
                            radius_m=state.search_radius_m,
                            # type_filter="restaurant"
                        )
                        
                        if candidates:
                            # Reset recommendations and set new candidates
                            state.set_candidates(candidates[:20])
                            state.recommendations = []
                            self.state_store.save_state(state)
                            
                            return {
                                "context_id": state.context_id,
                                "message": f"Found some results for '{potential_restaurant}'. Let me analyze them...",
                                "next_step": "analyze_and_compose",
                                "candidates_count": len(candidates)
                            }
                        else:
                            return {
                                "context_id": state.context_id,
                                "message": f"I couldn't find '{potential_restaurant}' nearby. Would you like to:\n"
                                          f"- Select from the current recommendations (1, 2, or 3)\n"
                                          f"- Try a different restaurant name\n"
                                          f"- Try a different cuisine",
                                "next_step": "select_restaurant"
                            }
                    except Exception as e:
                        pass  # Fall through to generic response
        
        # Default: didn't understand the input
        return {
            "context_id": state.context_id,
            "message": f"I didn't quite understand. Would you like to:\n"
                      f"- Select a recommendation (enter 1, 2, or 3)\n"
                      f"- Try a different cuisine (e.g., 'How about Italian?')\n"
                      f"- Search for a specific restaurant (e.g., 'How about KFC?')",
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
