"""Google Places API integration (mock implementation for demo)"""

from typing import Dict, List, Any, Optional
import json


class GooglePlacesClient:
    """Mock Google Places client for demonstration"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google Places client"""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def nearby_search(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 1000,
        keyword: Optional[str] = None,
        type_filter: str = "restaurant",
        price_level: Optional[List[int]] = None,
        open_now: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for nearby restaurants
        
        Args:
            latitude: Latitude of search center
            longitude: Longitude of search center
            radius_m: Search radius in meters
            keyword: Search keyword (cuisine type)
            type_filter: Place type filter
            price_level: Price level filter (1-4)
            open_now: Filter for currently open places
            
        Returns:
            List of place results
        """
        # This is a mock implementation
        # In production, this would call the actual Google Places API
        
        mock_results = [
            {
                "place_id": "ChIJN1blbB1WwoARxbB_cC5HCQU",
                "name": "Golden Thai Kitchen",
                "latitude": latitude + 0.01,
                "longitude": longitude + 0.01,
                "rating": 4.5,
                "user_ratings_total": 120,
                "price_level": 2,
                "types": ["restaurant", "food", "point_of_interest", "establishment"],
                "opening_hours": {
                    "open_now": True,
                    "periods": [{"close": {"day": 4, "time": "2200"}, "open": {"day": 4, "time": "1100"}}],
                    "weekday_text": ["Monday: 11:00 AM – 10:00 PM"]
                },
                "formatted_address": "123 Thai Ave, New York, NY",
                "formatted_phone_number": "(555) 123-4567"
            },
            {
                "place_id": "ChIJ1234567890",
                "name": "Pad Thai Express",
                "latitude": latitude - 0.005,
                "longitude": longitude + 0.015,
                "rating": 4.2,
                "user_ratings_total": 200,
                "price_level": 1,
                "types": ["restaurant", "food", "point_of_interest", "establishment"],
                "opening_hours": {
                    "open_now": True,
                    "periods": [{"close": {"day": 4, "time": "2300"}, "open": {"day": 4, "time": "1000"}}],
                    "weekday_text": ["Monday: 10:00 AM – 11:00 PM"]
                },
                "formatted_address": "456 Pad Thai St, New York, NY",
                "formatted_phone_number": "(555) 234-5678"
            },
            {
                "place_id": "ChIJ_abcdef123456",
                "name": "Thai Orchid Fine Dining",
                "latitude": latitude - 0.008,
                "longitude": longitude - 0.01,
                "rating": 4.7,
                "user_ratings_total": 300,
                "price_level": 3,
                "types": ["restaurant", "food", "point_of_interest", "establishment"],
                "opening_hours": {
                    "open_now": True,
                    "periods": [{"close": {"day": 4, "time": "2330"}, "open": {"day": 4, "time": "1700"}}],
                    "weekday_text": ["Monday: 5:00 PM – 11:30 PM"]
                },
                "formatted_address": "789 Orchid Ln, New York, NY",
                "formatted_phone_number": "(555) 345-6789"
            }
        ]
        
        # Filter by price level if specified
        if price_level:
            mock_results = [
                r for r in mock_results
                if r.get("price_level", 2) in price_level
            ]
        
        # Filter by open_now if specified
        if open_now:
            mock_results = [
                r for r in mock_results
                if r.get("opening_hours", {}).get("open_now", True)
            ]
        
        return mock_results
    
    def place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Detailed place information
        """
        # Mock implementation
        return {
            "place_id": place_id,
            "name": "Restaurant Name",
            "rating": 4.5,
            "reviews": [
                {
                    "author_name": "John Doe",
                    "rating": 5,
                    "text": "Great food and service!",
                    "time": 1234567890
                },
                {
                    "author_name": "Jane Smith",
                    "rating": 4,
                    "text": "Good food, a bit pricey",
                    "time": 1234567900
                }
            ]
        }
    
    def text_search(
        self,
        query: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_m: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Text search for restaurants
        
        Args:
            query: Search query
            latitude: Optional latitude for location bias
            longitude: Optional longitude for location bias
            radius_m: Optional search radius
            
        Returns:
            List of search results
        """
        # Mock implementation
        return self.nearby_search(
            latitude or 40.7128,
            longitude or -74.0060,
            radius_m or 5000,
            keyword=query
        )


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two coordinates (Haversine formula)
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in meters
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of earth in meters
    
    return c * r
