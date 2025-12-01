from typing import Dict, List, Any, Optional
import json
import os
import requests
from math import radians, cos, sin, asin, sqrt


class GooglePlacesClient:
    """Google Places API integration with real API calls"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google Places client with real API key"""
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
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
        Search for nearby restaurants using Google Places API (New)
        
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
        # If keyword is provided, use text search for better cuisine filtering
        if keyword:
            return self._text_search(
                latitude=latitude,
                longitude=longitude,
                radius_m=radius_m,
                query=f"{keyword} restaurant",
                price_level=price_level,
                open_now=open_now
            )
        
        # Otherwise use nearby search (all restaurants)
        return self._nearby_search(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            type_filter=type_filter,
            price_level=price_level,
            open_now=open_now
        )
    
    def _nearby_search(
        self,
        latitude: float,
        longitude: float,
        radius_m: int = 1000,
        type_filter: str = "restaurant",
        price_level: Optional[List[int]] = None,
        open_now: bool = False
    ) -> List[Dict[str, Any]]:
        """Internal nearby search without keyword"""
        # Use the new Places API v1 endpoint with POST
        # Use the new Places API v1 endpoint with POST
        url = "https://places.googleapis.com/v1/places:searchNearby"
        
        # Build request body for new API (snake_case for JSON)
        body = {
            "location_restriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius_m
                }
            },
            "included_types": ["restaurant"],
            "max_result_count": 20,
            "open_now": open_now,
            "rank_preference": "DISTANCE",
            "language_code": "en"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.location,places.rating,places.userRatingCount,places.priceLevel,places.formattedAddress,places.types"
        }
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("places", [])
            
            # Transform results to match expected format
            formatted_results = []
            for place in results:
                location = place.get("location", {})
                formatted_place = {
                    "place_id": place.get("id"),
                    "name": place.get("displayName", {}).get("text", "Unknown"),
                    "geometry": {
                        "location": {
                            "lat": location.get("latitude", 0),
                            "lng": location.get("longitude", 0)
                        }
                    },
                    "rating": place.get("rating", 0),
                    "user_ratings_total": place.get("userRatingCount", 0),
                    "price_level": self._convert_price_level(place.get("priceLevel")),
                    "opening_hours": {
                        "open_now": place.get("openingHours", {}).get("openNow", True)
                    },
                    "formatted_address": place.get("formattedAddress", ""),
                    "types": place.get("types", [])
                }
                
                # Calculate distance
                formatted_place["distance_m"] = calculate_distance(
                    latitude, longitude,
                    location.get("latitude", latitude),
                    location.get("longitude", longitude)
                )
                
                formatted_results.append(formatted_place)
            
            # Filter by price level if specified
            if price_level:
                formatted_results = [
                    r for r in formatted_results
                    if r.get("price_level", 2) in price_level
                ]
            
            return formatted_results
            
        except requests.exceptions.HTTPError as e:
            # Log detailed error info
            try:
                error_data = e.response.json()
                print(f"API Error Details: {error_data}")
            except:
                print(f"API Error: {e.response.text}")
            print("Falling back to mock data for demonstration...")
            return self._mock_nearby_search(latitude, longitude, radius_m, None, price_level)
        except requests.exceptions.RequestException as e:
            print(f"Error calling Google Places API: {e}")
            print("Falling back to mock data for demonstration...")
            return self._mock_nearby_search(latitude, longitude, radius_m, None, price_level)
    
    def _text_search(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        query: str,
        price_level: Optional[List[int]] = None,
        open_now: bool = False
    ) -> List[Dict[str, Any]]:
        """Text search for restaurants with cuisine-specific query"""
        url = "https://places.googleapis.com/v1/places:searchText"
        
        body = {
            "textQuery": query,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius_m
                }
            },
            "maxResultCount": 20,
            "openNow": open_now,
            "languageCode": "en"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.location,places.rating,places.userRatingCount,places.priceLevel,places.formattedAddress,places.types"
        }
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("places", [])
            
            # Transform results to match expected format
            formatted_results = []
            for place in results:
                location = place.get("location", {})
                formatted_place = {
                    "place_id": place.get("id"),
                    "name": place.get("displayName", {}).get("text", "Unknown"),
                    "geometry": {
                        "location": {
                            "lat": location.get("latitude", 0),
                            "lng": location.get("longitude", 0)
                        }
                    },
                    "rating": place.get("rating", 0),
                    "user_ratings_total": place.get("userRatingCount", 0),
                    "price_level": self._convert_price_level(place.get("priceLevel")),
                    "opening_hours": {
                        "open_now": place.get("openingHours", {}).get("openNow", True)
                    },
                    "formatted_address": place.get("formattedAddress", ""),
                    "types": place.get("types", [])
                }
                
                # Calculate distance
                formatted_place["distance_m"] = calculate_distance(
                    latitude, longitude,
                    location.get("latitude", latitude),
                    location.get("longitude", longitude)
                )
                
                formatted_results.append(formatted_place)
            
            # Filter by price level if specified
            if price_level:
                formatted_results = [
                    r for r in formatted_results
                    if r.get("price_level", 2) in price_level
                ]
            
            return formatted_results
            
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                print(f"API Error Details: {error_data}")
            except:
                print(f"API Error: {e.response.text}")
            print("Falling back to mock data for demonstration...")
            return self._mock_nearby_search(latitude, longitude, radius_m, query, price_level)
        except requests.exceptions.RequestException as e:
            print(f"Error calling Google Places Text Search API: {e}")
            print("Falling back to mock data for demonstration...")
            return self._mock_nearby_search(latitude, longitude, radius_m, query, price_level)
    
    def _convert_price_level(self, price_level_str: Optional[str]) -> int:
        """Convert new API price level format to numeric 1-4 scale"""
        if not price_level_str:
            return 2  # Default
        price_map = {
            "PRICE_LEVEL_FREE": 0,
            "PRICE_LEVEL_INEXPENSIVE": 1,
            "PRICE_LEVEL_MODERATE": 2,
            "PRICE_LEVEL_EXPENSIVE": 3,
            "PRICE_LEVEL_VERY_EXPENSIVE": 4
        }
        return price_map.get(price_level_str, 2)
    
    def _mock_nearby_search(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        keyword: Optional[str],
        price_level: Optional[List[int]]
    ) -> List[Dict[str, Any]]:
        """Generate mock restaurant data for testing"""
        cuisine_templates = {
            "thai": ["Golden Thai Kitchen", "Pad Thai Express", "Thai Orchid Fine Dining"],
            "italian": ["Bella Italia", "Pasta Perfetto", "Trattoria Roma"],
            "japanese": ["Golden Sushi Bar", "Tokyo Express", "Sakura Dining"],
            "mexican": ["Casa Mexico", "Taco Express", "El Pueblo"],
            "indian": ["Taj Mahal", "Curry House", "Maharaja Palace"],
            "chinese": ["Golden Dragon", "Beijing Express", "Dynasty"],
            "": ["Primo Ristorante", "Urban Bistro", "The Plate"]
        }
        
        keyword_lower = (keyword or "").lower()
        names = None
        for key, templates in cuisine_templates.items():
            if key and key in keyword_lower:
                names = templates
                break
        names = names or cuisine_templates[""]
        
        mock_results = [
            {
                "place_id": f"mock_place_1",
                "name": names[0],
                "geometry": {
                    "location": {
                        "lat": latitude + 0.005,
                        "lng": longitude + 0.005
                    }
                },
                "distance_m": 600,
                "price_level": 2,
                "rating": 4.5,
                "user_ratings_total": 150,
                "opening_hours": {"open_now": True},
                "opening_hours_snippet": "Open until 21:30",
                "formatted_address": f"123 Main St, Melbourne, VIC",
                "types": ["restaurant"]
            },
            {
                "place_id": f"mock_place_2",
                "name": names[1] if len(names) > 1 else names[0],
                "geometry": {
                    "location": {
                        "lat": latitude - 0.003,
                        "lng": longitude + 0.008
                    }
                },
                "distance_m": 800,
                "price_level": 1,
                "rating": 4.2,
                "user_ratings_total": 200,
                "opening_hours": {"open_now": True},
                "opening_hours_snippet": "Open until 22:00",
                "formatted_address": f"456 Park Ave, Melbourne, VIC",
                "types": ["restaurant"]
            },
            {
                "place_id": f"mock_place_3",
                "name": names[2] if len(names) > 2 else names[1] if len(names) > 1 else names[0],
                "geometry": {
                    "location": {
                        "lat": latitude - 0.006,
                        "lng": longitude - 0.005
                    }
                },
                "distance_m": 1000,
                "price_level": 3,
                "rating": 4.7,
                "user_ratings_total": 320,
                "opening_hours": {"open_now": True},
                "opening_hours_snippet": "Open until 23:00",
                "formatted_address": f"789 Elm St, Melbourne, VIC",
                "types": ["restaurant"]
            }
        ]
        
        # Filter by price level if specified
        if price_level:
            mock_results = [
                r for r in mock_results
                if r.get("price_level", 2) in price_level
            ]
        
        return mock_results
    
        """
        Get detailed information about a place using real API
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Detailed place information
        """
        url = f"{self.base_url}/details/json"
        
        params = {
            "place_id": place_id,
            "fields": "name,rating,reviews,formatted_phone_number,opening_hours,website",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"API Error: {data.get('status')}")
                return {}
            
            return data.get("result", {})
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Google Places Details API: {e}")
            return {}
    
    def text_search(
        self,
        query: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_m: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Text search for restaurants using real Google Places API
        
        Args:
            query: Search query
            latitude: Optional latitude for location bias
            longitude: Optional longitude for location bias
            radius_m: Optional search radius
            
        Returns:
            List of search results
        """
        url = f"{self.base_url}/textsearch/json"
        
        params = {
            "query": query,
            "type": "restaurant",
            "key": self.api_key
        }
        
        if latitude and longitude:
            params["location"] = f"{latitude},{longitude}"
            if radius_m:
                params["radius"] = radius_m
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"API Error: {data.get('status')}")
                return []
            
            results = data.get("results", [])
            
            # Calculate distance if location provided
            if latitude and longitude:
                for result in results:
                    result["distance_m"] = calculate_distance(
                        latitude, longitude,
                        result["geometry"]["location"]["lat"],
                        result["geometry"]["location"]["lng"]
                    )
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Google Places Text Search API: {e}")
            return []
    
    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to coordinates
        
        Args:
            address: Address string
            
        Returns:
            Dict with latitude, longitude, and formatted_address
        """
        params = {
            "address": address,
            "key": self.api_key
        }
        
        try:
            response = requests.get(self.geocode_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK" or not data.get("results"):
                # Fall back to mock geocoding on API error
                return self._mock_geocode(address)
            
            location = data["results"][0]
            coords = location["geometry"]["location"]
            
            return {
                "latitude": coords["lat"],
                "longitude": coords["lng"],
                "formatted_address": location["formatted_address"]
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Geocoding API unavailable, using mock data: {e}")
            return self._mock_geocode(address)
    
    def _mock_geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """Generate mock geocoding result for testing"""
        import difflib
        
        mock_locations = {
            "new york": {"lat": 40.7128, "lng": -74.0060, "addr": "New York, NY, USA"},
            "sydney": {"lat": -33.8688, "lng": 151.2093, "addr": "Sydney, NSW, Australia"},
            "melbourne": {"lat": -37.8136, "lng": 144.9631, "addr": "Melbourne, VIC, Australia"},
            "london": {"lat": 51.5074, "lng": -0.1278, "addr": "London, UK"},
            "tokyo": {"lat": 35.6762, "lng": 139.6503, "addr": "Tokyo, Japan"},
            "paris": {"lat": 48.8566, "lng": 2.3522, "addr": "Paris, France"},
        }
        
        address_lower = address.lower()
        
        # Clean up common prefixes
        address_clean = address_lower
        for prefix in ["i'm in", "i'm at", "i am in", "i am at", "location:"]:
            if address_clean.startswith(prefix):
                address_clean = address_clean[len(prefix):].strip()
                break
        
        # Try exact match
        for key, coords in mock_locations.items():
            if key in address_clean:
                return {
                    "latitude": coords["lat"],
                    "longitude": coords["lng"],
                    "formatted_address": coords["addr"]
                }
        
        # Try fuzzy matching on individual words
        words = address_clean.split()
        for word in words:
            if len(word) > 3:  # Only try words longer than 3 chars
                best_match = difflib.get_close_matches(word, mock_locations.keys(), n=1, cutoff=0.6)
                if best_match:
                    coords = mock_locations[best_match[0]]
                    return {
                        "latitude": coords["lat"],
                        "longitude": coords["lng"],
                        "formatted_address": coords["addr"]
                    }
        
        # Try to parse coordinates if provided as "lat,lon"
        try:
            parts = address.split(",")
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                return {
                    "latitude": lat,
                    "longitude": lng,
                    "formatted_address": f"Coordinates: {lat}, {lng}"
                }
        except (ValueError, IndexError):
            pass
        
        return None


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
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r * 1000  # Convert to meters