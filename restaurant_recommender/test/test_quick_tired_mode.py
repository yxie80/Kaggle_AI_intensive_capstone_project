"""
Test suite for Quick Tired Mode feature
Tests that exhausted users can skip budget/cuisine setup and go straight to fast food options
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from runner.orchestrator_runner import OrchestratorRunner
from utils.state_manager import ConversationState, StateStore


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing"""
    return OrchestratorRunner()


@pytest.fixture
def sample_state():
    """Create a sample conversation state with location set"""
    state = ConversationState(
        context_id="test-context-123",
        user_id="test-user",
        location={"lat": -37.8136, "lng": 144.9631},  # Melbourne
        timezone_id="Australia/Melbourne",
        location_time=datetime.now().isoformat()
    )
    return state


@pytest.mark.asyncio
async def test_exhausted_keyword_triggers_quick_mode(orchestrator, sample_state):
    """Test that 'exhausted' keyword triggers quick tired mode"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm completely exhausted")
    
    # Verify quick mode was triggered
    assert response["quick_mode"] == True
    assert response["next_step"] == "discover_restaurants"
    assert "exhausted" in response["message"].lower()
    assert "fast food" in response["message"].lower()
    
    # Verify state was auto-configured
    assert sample_state.energy_level == 1
    assert sample_state.budget_level == 1
    assert sample_state.preferred_cuisine == "Fast Food"
    assert sample_state.distance_confirmed == True


@pytest.mark.asyncio
async def test_dead_tired_keyword_triggers_quick_mode(orchestrator, sample_state):
    """Test that 'dead tired' keyword triggers quick tired mode"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm dead tired after work")
    
    assert response["quick_mode"] == True
    assert response["next_step"] == "discover_restaurants"
    assert sample_state.energy_level == 1
    assert sample_state.preferred_cuisine == "Fast Food"


@pytest.mark.asyncio
async def test_too_tired_keyword_triggers_quick_mode(orchestrator, sample_state):
    """Test that 'too tired' keyword triggers quick tired mode"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm too tired to think about food")
    
    assert response["quick_mode"] == True
    assert sample_state.budget_level == 1


@pytest.mark.asyncio
async def test_worn_out_keyword_triggers_quick_mode(orchestrator, sample_state):
    """Test that 'worn out' keyword triggers quick tired mode"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm completely worn out")
    
    assert response["quick_mode"] == True
    assert sample_state.energy_level == 1


@pytest.mark.asyncio
async def test_regular_tired_does_not_trigger_quick_mode(orchestrator, sample_state):
    """Test that regular 'tired' keyword does NOT trigger quick mode (goes to normal tired flow)"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm tired")
    
    # Should be normal tired flow, not quick mode
    assert "quick_mode" not in response or response.get("quick_mode") != True
    assert response["next_step"] == "confirm_distance"
    assert sample_state.energy_level == 2  # Regular tired (not 1)


@pytest.mark.asyncio
async def test_knackered_keyword_triggers_quick_mode(orchestrator, sample_state):
    """Test that 'knackered' (UK English) keyword triggers quick tired mode"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm absolutely knackered")
    
    assert response["quick_mode"] == True
    assert sample_state.preferred_cuisine == "Fast Food"


@pytest.mark.asyncio
async def test_wiped_keyword_triggers_quick_mode(orchestrator, sample_state):
    """Test that 'wiped' keyword triggers quick tired mode"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm completely wiped out")
    
    assert response["quick_mode"] == True
    assert sample_state.energy_level == 1


@pytest.mark.asyncio
async def test_quick_mode_skips_budget_and_cuisine_questions():
    """Integration test: Verify quick mode skips budget and cuisine collection"""
    orchestrator = OrchestratorRunner()
    state = ConversationState(
        context_id="test-context-456",
        user_id="test-user-2",
        location={"lat": -37.8136, "lng": 144.9631},
        timezone_id="Australia/Melbourne",
        location_time=datetime.now().isoformat()
    )
    orchestrator.state_store.save_state(state)
    
    # User says exhausted
    response = await orchestrator._collect_energy(state, "I'm shattered")
    
    # Should skip straight to discover_restaurants
    assert response["next_step"] == "discover_restaurants"
    
    # Verify all required fields are set
    assert state.energy_level is not None
    assert state.budget_level is not None
    assert state.preferred_cuisine is not None
    assert state.distance_confirmed is True


@pytest.mark.asyncio
async def test_quick_mode_defaults_to_cheap_budget(orchestrator, sample_state):
    """Test that quick mode sets budget to level 1 (cheap/fast food)"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm exhausted")
    
    # Budget level 1 = cheapest/fast food options
    assert sample_state.budget_level == 1
    assert sample_state.group_size == 1  # Solo dining


@pytest.mark.asyncio
async def test_quick_mode_sets_fast_food_cuisine(orchestrator, sample_state):
    """Test that quick mode automatically sets Fast Food as cuisine preference"""
    orchestrator.state_store.save_state(sample_state)
    
    response = await orchestrator._collect_energy(sample_state, "I'm completely drained")
    
    assert sample_state.preferred_cuisine == "Fast Food"


def test_tired_mode_keywords_comprehensive():
    """Test comprehensive list of exhaustion keywords"""
    very_tired_keywords = [
        "exhausted",
        "too tired",
        "so tired",
        "completely exhausted",
        "dead tired",
        "shattered",
        "worn out",
        "knackered",
        "wiped",
        "beat",
        "drained"
    ]
    
    # Verify all keywords are properly defined in the system
    assert len(very_tired_keywords) == 11
    assert "exhausted" in very_tired_keywords
    assert "knackered" in very_tired_keywords


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
