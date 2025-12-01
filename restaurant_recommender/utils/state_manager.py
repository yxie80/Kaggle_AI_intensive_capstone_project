"""State management for conversation flow"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
import uuid


@dataclass
class ConversationState:
    """Manages the state of a restaurant recommendation conversation"""
    
    context_id: str
    user_id: str
    
    # User inputs collected
    location: Optional[Dict[str, float]] = None  # {lat, lng}
    energy_level: Optional[int] = None
    budget_level: Optional[int] = None
    group_size: Optional[int] = None
    preferred_cuisine: Optional[str] = None
    preferred_dish: Optional[str] = None
    
    # System generated data
    search_radius_m: int = 3000
    candidates: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    selected_restaurant: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    consent_given: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return asdict(self)
    
    def update_timestamp(self) -> None:
        """Update last_updated timestamp"""
        self.last_updated = datetime.now().isoformat()
    
    def set_location(self, lat: float, lng: float) -> None:
        """Set user location"""
        self.location = {"lat": lat, "lng": lng}
        self.update_timestamp()
    
    def set_energy_level(self, energy: int) -> None:
        """Set energy level and compute search radius"""
        self.energy_level = energy
        energy_radius = {1: 1000, 2: 1000, 3: 3000, 4: 5000, 5: 5000}
        self.search_radius_m = energy_radius.get(energy, 3000)
        self.update_timestamp()
    
    def set_budget(self, budget_level: int, group_size: int) -> None:
        """Set budget level and group size"""
        self.budget_level = budget_level
        self.group_size = group_size
        self.update_timestamp()
    
    def set_cuisine_preference(self, cuisine: str, dish: Optional[str] = None) -> None:
        """Set preferred cuisine and optional dish"""
        self.preferred_cuisine = cuisine
        self.preferred_dish = dish
        self.update_timestamp()
    
    def set_candidates(self, candidates: list) -> None:
        """Set candidate restaurants from discovery"""
        self.candidates = candidates
        self.update_timestamp()
    
    def set_recommendations(self, recommendations: list) -> None:
        """Set final recommendations"""
        self.recommendations = recommendations
        self.update_timestamp()
    
    def select_restaurant(self, restaurant: Dict[str, Any]) -> None:
        """User selects a restaurant"""
        self.selected_restaurant = restaurant
        self.update_timestamp()
    
    def is_complete(self) -> bool:
        """Check if conversation has enough info for recommendations"""
        return all([
            self.location,
            self.energy_level,
            self.budget_level,
            self.group_size,
            self.preferred_cuisine
        ])


class StateStore:
    """In-memory state store (for demonstration; use DB in production)"""
    
    def __init__(self):
        self.states: Dict[str, ConversationState] = {}
    
    def create_state(self, user_id: str) -> ConversationState:
        """Create new conversation state"""
        context_id = str(uuid.uuid4())
        state = ConversationState(
            context_id=context_id,
            user_id=user_id
        )
        self.states[context_id] = state
        return state
    
    def get_state(self, context_id: str) -> Optional[ConversationState]:
        """Retrieve conversation state"""
        return self.states.get(context_id)
    
    def save_state(self, state: ConversationState) -> None:
        """Save/update conversation state"""
        self.states[state.context_id] = state
    
    def delete_state(self, context_id: str) -> None:
        """Delete conversation state"""
        if context_id in self.states:
            del self.states[context_id]
    
    def list_user_states(self, user_id: str) -> list:
        """List all states for a user"""
        return [
            state for state in self.states.values()
            if state.user_id == user_id
        ]


# Global state store instance
_state_store = StateStore()


def get_state_store() -> StateStore:
    """Get the global state store"""
    return _state_store
