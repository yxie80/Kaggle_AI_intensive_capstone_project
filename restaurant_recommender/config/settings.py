from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchConfig:
    """Configuration for restaurant search parameters"""
    default_radius_m: int = 3000
    max_results: int = 20
    min_rating: float = 3.5
    supported_price_levels: List[int] = field(default_factory=lambda: [1, 2, 3, 4])


@dataclass
class ScoringWeights:
    """Weights for restaurant scoring algorithm"""
    rating_weight: float = 0.4
    distance_weight: float = 0.25
    value_weight: float = 0.2
    open_weight: float = 0.15
    
    def __post_init__(self):
        total = self.rating_weight + self.distance_weight + self.value_weight + self.open_weight
        if abs(total - 1.0) > 0.01:
            # Normalize weights
            self.rating_weight /= total
            self.distance_weight /= total
            self.value_weight /= total
            self.open_weight /= total


@dataclass
class ConversationConfig:
    """Configuration for conversation flow"""
    max_suggestions: int = 3
    enable_profiling: bool = True
    enable_consent: bool = True
    retention_days: int = 365


# Default configurations
DEFAULT_SEARCH_CONFIG = SearchConfig()
DEFAULT_SCORING_WEIGHTS = ScoringWeights()
DEFAULT_CONVERSATION_CONFIG = ConversationConfig()

# Cuisine types available
CUISINE_TYPES = [
    "Thai",
    "Japanese",
    "Italian",
    "Mexican",
    "Indian",
    "Chinese",
    "Vietnamese",
    "Korean",
    "French",
    "Mediterranean",
    "American",
    "Brazilian",
]

# Energy level to radius mapping
ENERGY_RADIUS_MAPPING = {
    1: 1000,
    2: 1000,
    3: 3000,
    4: 5000,
    5: 5000,
}

# Budget level descriptions and estimates
BUDGET_LEVELS = {
    1: {"desc": "cheap", "pp_estimate": "10-15"},
    2: {"desc": "mid", "pp_estimate": "20-35"},
    3: {"desc": "upscale", "pp_estimate": "40-75"},
    4: {"desc": "fancy", "pp_estimate": "80+"},
}
