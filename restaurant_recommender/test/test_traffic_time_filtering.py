"""
Test suite for traffic time filtering in restaurant recommendations.

This test suite validates that the orchestrator correctly filters out restaurants
that don't have enough time for users to visit before closing, considering:
- Current time
- Restaurant closing time
- Distance to restaurant
- Travel time (estimated at ~30 km/h average speed)
- Minimum visit time (30 minutes default)
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from runner.orchestrator_runner import OrchestratorRunner
from utils.state_manager import ConversationState, get_state_store


class TestTrafficTimeFiltering:
    """Test cases for traffic time consideration in recommendations"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return OrchestratorRunner()
    
    @pytest.fixture
    def mock_state(self):
        """Create mock conversation state"""
        state_store = get_state_store()
        state = state_store.create_state("test_user")
        state.set_location(-37.8136, 144.9631)  # Melbourne CBD
        state.set_energy_level(3)
        state.confirm_distance(1000)
        state.set_budget(2, 2)
        state.set_cuisine_preference("Thai")
        return state
    
    @pytest.mark.asyncio
    async def test_scenario_1_restaurant_closes_soon(self, orchestrator, mock_state):
        """
        Scenario 1: Current time 10:30 PM, Restaurant closes 11 PM
        - Distance: 5 km
        - Travel time: ~10 minutes
        - Time available: 30 minutes
        - Need: 10 min travel + 30 min visit = 40 minutes
        - Expected: Restaurant filtered out
        """
        # Mock current time as 10:30 PM
        mock_time = datetime.now().replace(hour=22, minute=30, second=0, microsecond=0)
        
        # Create mock restaurant closing at 11 PM (30 min remaining)
        test_restaurant = {
            "place_id": "test_place_1",
            "name": "Thai Restaurant A",
            "rating": 4.5,
            "price_level": 2,
            "distance_m": 5000,  # 5 km away
            "opening_hours_snippet": "Open ⋅ Closes 11 PM",
            "composite_score": 0.85,
            "types": ["restaurant"]
        }
        
        mock_state.set_candidates([test_restaurant])
        
        with patch('runner.orchestrator_runner.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            result = await orchestrator._compose_recommendations(mock_state, "")
        
        # Should show no recommendations due to insufficient time
        assert result["next_step"] == "discover_restaurants"
        assert "Unfortunately, the best matches close too soon" in result["message"]
        assert "Not enough time" in result["message"]
    
    @pytest.mark.asyncio
    async def test_scenario_2_restaurant_has_enough_time(self, orchestrator, mock_state):
        """
        Scenario 2: Current time 6:00 PM, Restaurant closes 11 PM
        - Distance: 5 km
        - Travel time: ~10 minutes
        - Time available: 5 hours
        - Need: 10 min travel + 30 min visit = 40 minutes
        - Expected: Restaurant recommended
        """
        # Mock current time as 6:00 PM
        mock_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Create mock restaurant closing at 11 PM (5 hours remaining)
        test_restaurant = {
            "place_id": "test_place_2",
            "name": "Thai Restaurant B",
            "rating": 4.4,
            "price_level": 2,
            "distance_m": 5000,  # 5 km away
            "opening_hours_snippet": "Open ⋅ Closes 11 PM",
            "composite_score": 0.84,
            "types": ["restaurant"]
        }
        
        mock_state.set_candidates([test_restaurant])
        
        with patch('runner.orchestrator_runner.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            result = await orchestrator._compose_recommendations(mock_state, "")
        
        # Should recommend the restaurant
        assert result["next_step"] == "select_restaurant"
        assert "Here are my top 1 recommendation" in result["message"]
        assert "Thai Restaurant B" in result["message"]
        assert len(result["recommendations"]) == 1
    
    @pytest.mark.asyncio
    async def test_mixed_recommendations_filters_closed_only(self, orchestrator, mock_state):
        """
        Test with 3 restaurants where some have enough time and some don't.
        Should only recommend the ones with sufficient time.
        """
        # Mock current time as 10:00 PM
        mock_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
        
        restaurants = [
            {
                "place_id": "test_place_3a",
                "name": "Close Thai Restaurant",
                "rating": 4.6,
                "price_level": 2,
                "distance_m": 5000,  # 5 km away
                "opening_hours_snippet": "Open ⋅ Closes 10:30 PM",  # Closes in 30 min - NOT ENOUGH
                "composite_score": 0.90,
                "types": ["restaurant"]
            },
            {
                "place_id": "test_place_3b",
                "name": "Open Late Thai Restaurant",
                "rating": 4.3,
                "price_level": 2,
                "distance_m": 3000,  # 3 km away
                "opening_hours_snippet": "Open ⋅ Closes 11:30 PM",  # Closes in 1.5 hours - ENOUGH
                "composite_score": 0.82,
                "types": ["restaurant"]
            },
            {
                "place_id": "test_place_3c",
                "name": "Very Late Thai Restaurant",
                "rating": 4.1,
                "price_level": 2,
                "distance_m": 2000,  # 2 km away
                "opening_hours_snippet": "Open ⋅ Closes Midnight",  # Closes in 2 hours - ENOUGH
                "composite_score": 0.78,
                "types": ["restaurant"]
            }
        ]
        
        mock_state.set_candidates(restaurants)
        
        with patch('runner.orchestrator_runner.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            result = await orchestrator._compose_recommendations(mock_state, "")
        
        # Should only recommend 2 restaurants (not the closing soon one)
        assert result["next_step"] == "select_restaurant"
        assert len(result["recommendations"]) == 2
        assert "Open Late Thai Restaurant" in result["message"]
        assert "Very Late Thai Restaurant" in result["message"]
        assert "Close Thai Restaurant" not in result["message"]
        assert "Unfortunately, the best matches close too soon" in result["message"]
    
    @pytest.mark.asyncio
    async def test_close_distance_short_travel_time(self, orchestrator, mock_state):
        """
        Test restaurant very close by (short travel time).
        Should be recommended even if restaurant closes relatively soon.
        """
        # Mock current time as 10:45 PM
        mock_time = datetime.now().replace(hour=22, minute=45, second=0, microsecond=0)
        
        test_restaurant = {
            "place_id": "test_place_4",
            "name": "Nearby Thai Restaurant",
            "rating": 4.2,
            "price_level": 2,
            "distance_m": 500,  # 0.5 km away (only ~1 minute travel)
            "opening_hours_snippet": "Open ⋅ Closes 11 PM",  # Closes in 15 min
            "composite_score": 0.80,
            "types": ["restaurant"]
        }
        
        mock_state.set_candidates([test_restaurant])
        
        with patch('runner.orchestrator_runner.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            result = await orchestrator._compose_recommendations(mock_state, "")
        
        # Should recommend the restaurant (1 min travel + 30 min visit = 31 min needed, 15 min available)
        # Actually should NOT recommend (15 < 31)
        assert result["next_step"] == "discover_restaurants"
        assert "Not enough time" in result["message"]
    
    @pytest.mark.asyncio
    async def test_far_distance_long_travel_time(self, orchestrator, mock_state):
        """
        Test restaurant far away with significant travel time.
        Should filter out if travel time makes it impossible to visit.
        """
        # Mock current time as 10:00 PM
        mock_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
        
        test_restaurant = {
            "place_id": "test_place_5",
            "name": "Distant Thai Restaurant",
            "rating": 4.7,
            "price_level": 2,
            "distance_m": 30000,  # 30 km away (~60 minutes travel)
            "opening_hours_snippet": "Open ⋅ Closes 11 PM",  # Closes in 1 hour
            "composite_score": 0.88,
            "types": ["restaurant"]
        }
        
        mock_state.set_candidates([test_restaurant])
        
        with patch('runner.orchestrator_runner.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            result = await orchestrator._compose_recommendations(mock_state, "")
        
        # Should NOT recommend (60 min travel + 30 min visit = 90 min needed, only 60 min available)
        assert result["next_step"] == "discover_restaurants"
        assert "Not enough time" in result["message"]


if __name__ == "__main__":
    # Run tests
    import pytest
    pytest.main([__file__, "-v"])
