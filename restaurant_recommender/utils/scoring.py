"""Restaurant scoring and ranking utilities"""

from typing import Dict, List, Any, Optional
from config.settings import DEFAULT_SCORING_WEIGHTS
import math


def normalize_distance(distance_m: int, max_distance_m: int = 10000) -> float:
    """
    Normalize distance to 0-1 scale (closer = higher score)
    
    Args:
        distance_m: Distance in meters
        max_distance_m: Maximum distance threshold
        
    Returns:
        Normalized distance score 0-1
    """
    if distance_m >= max_distance_m:
        return 0.0
    return 1.0 - (distance_m / max_distance_m)


def normalize_rating(rating: float, max_rating: float = 5.0) -> float:
    """
    Normalize rating to 0-1 scale
    
    Args:
        rating: Restaurant rating
        max_rating: Maximum possible rating
        
    Returns:
        Normalized rating score 0-1
    """
    return min(rating / max_rating, 1.0)


def compute_composite_score(
    restaurant: Dict[str, Any],
    max_distance_m: int = 10000,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Compute composite restaurant score
    
    Args:
        restaurant: Restaurant data dict with rating, distance_m, value_score, open_now
        max_distance_m: Maximum distance threshold
        weights: Custom scoring weights
        
    Returns:
        Composite score 0-1
    """
    if weights is None:
        weights = {
            'rating': DEFAULT_SCORING_WEIGHTS.rating_weight,
            'distance': DEFAULT_SCORING_WEIGHTS.distance_weight,
            'value': DEFAULT_SCORING_WEIGHTS.value_weight,
            'open': DEFAULT_SCORING_WEIGHTS.open_weight,
        }
    
    score = 0.0
    
    # Rating component
    if 'rating' in restaurant and restaurant['rating']:
        norm_rating = normalize_rating(restaurant['rating'])
        score += weights.get('rating', 0.4) * norm_rating
    
    # Distance component
    if 'distance_m' in restaurant:
        norm_distance = normalize_distance(restaurant['distance_m'], max_distance_m)
        score += weights.get('distance', 0.25) * norm_distance
    
    # Value component
    if 'value_score' in restaurant:
        score += weights.get('value', 0.2) * restaurant['value_score']
    
    # Open now component (boolean boost)
    if restaurant.get('open_now', False):
        score += weights.get('open', 0.15) * 1.0
    
    return min(score, 1.0)


def rank_restaurants(
    restaurants: List[Dict[str, Any]],
    max_distance_m: int = 10000,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Rank and select top restaurants
    
    Args:
        restaurants: List of restaurant data
        max_distance_m: Maximum distance threshold for scoring
        top_n: Number of top restaurants to return
        
    Returns:
        Ranked list of top N restaurants with scores
    """
    # Compute scores for all restaurants
    for restaurant in restaurants:
        restaurant['composite_score'] = compute_composite_score(
            restaurant,
            max_distance_m=max_distance_m
        )
    
    # Sort by composite score descending
    ranked = sorted(restaurants, key=lambda x: x['composite_score'], reverse=True)
    
    # Return top N
    return ranked[:top_n]


def filter_restaurants_by_budget(
    restaurants: List[Dict[str, Any]],
    budget_level: int
) -> List[Dict[str, Any]]:
    """
    Filter restaurants by budget level
    
    Args:
        restaurants: List of restaurant data
        budget_level: Budget level 1-4
        
    Returns:
        Filtered list of restaurants matching budget
    """
    return [
        r for r in restaurants
        if r.get('price_level', 2) <= budget_level
    ]


def filter_restaurants_by_open(
    restaurants: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter to only open restaurants
    
    Args:
        restaurants: List of restaurant data
        
    Returns:
        Filtered list of open restaurants
    """
    return [r for r in restaurants if r.get('open_now', False)]
