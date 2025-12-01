"""
Test distance confirmation feature
Tests that the system allows users to:
1. Accept the suggested distance
2. Propose an alternative distance
3. Only proceed to budget after distance is confirmed
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from runner.orchestrator_runner import OrchestratorRunner


async def test_distance_confirmation():
    """Test the distance confirmation workflow"""
    print("\n" + "="*70)
    print("TEST: Distance Confirmation Workflow")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Step 1: Start conversation
    print("\n[Step 1] Starting conversation...")
    response = await runner.start_conversation("test_user", "test location")
    context_id = response["context_id"]
    print(f"Context ID: {context_id}")
    print(f"Next Step: {response['next_step']}")
    
    # Step 2: Provide location
    print("\n[Step 2] Providing location...")
    response = await runner.process_message(context_id, "Sydney CBD")
    print(f"Response: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    assert response["next_step"] == "collect_energy", "Should collect energy after location"
    
    # Step 3: Provide energy level (high energy -> 5000m radius)
    print("\n[Step 3] Providing high energy level...")
    response = await runner.process_message(context_id, "Still have some energy")
    print(f"Response: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    print(f"Search Radius: {response.get('search_radius_m')}m")
    assert response["next_step"] == "confirm_distance", "Should ask for distance confirmation"
    assert response.get('search_radius_m') == 5000, "High energy should suggest 5000m"
    
    # Step 4: User rejects distance and proposes custom distance
    print("\n[Step 4] User rejects distance (5000m too far)...")
    response = await runner.process_message(context_id, "Nah, its too far")
    print(f"Response: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    assert response["next_step"] == "confirm_distance", "Should stay in distance confirmation"
    
    # Step 5: User proposes custom distance (1000m)
    print("\n[Step 5] User proposes custom distance (1000m)...")
    response = await runner.process_message(context_id, "1000m is better")
    print(f"Response: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    print(f"Confirmed Distance: {response.get('distance_m')}m")
    assert response["next_step"] == "collect_budget", "Should move to budget after distance confirmed"
    assert response.get('distance_m') == 1000, "Should accept 1000m custom distance"
    
    # Step 6: Provide budget
    print("\n[Step 6] Providing budget preference...")
    response = await runner.process_message(context_id, "casual is good")
    print(f"Response: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    assert response["next_step"] == "collect_group_size", "Should collect group size after budget"
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - Distance confirmation workflow working correctly!")
    print("="*70)


async def test_distance_acceptance():
    """Test that user can accept suggested distance directly"""
    print("\n" + "="*70)
    print("TEST: Direct Distance Acceptance")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Setup
    response = await runner.start_conversation("test_user2", "test")
    context_id = response["context_id"]
    
    await runner.process_message(context_id, "Melbourne CBD")
    
    # Low energy -> 1000m
    print("\n[Step 1] Low energy level (1000m suggested)...")
    response = await runner.process_message(context_id, "Pretty tired")
    print(f"Search Radius: {response.get('search_radius_m')}m")
    assert response["next_step"] == "confirm_distance"
    assert response.get('search_radius_m') == 1000
    
    # User accepts distance immediately
    print("\n[Step 2] User accepts distance with 'yes'...")
    response = await runner.process_message(context_id, "yes that's fine")
    print(f"Response: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    assert response["next_step"] == "collect_budget", "Should move to budget when distance accepted"
    assert response.get('confirmed') == True, "Distance should be confirmed"
    
    print("\n" + "="*70)
    print("✅ DISTANCE ACCEPTANCE TEST PASSED!")
    print("="*70)


async def test_distance_with_km_units():
    """Test that user can propose distance with km units"""
    print("\n" + "="*70)
    print("TEST: Distance with km units")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Setup
    response = await runner.start_conversation("test_user3", "test")
    context_id = response["context_id"]
    
    await runner.process_message(context_id, "Brisbane")
    response = await runner.process_message(context_id, "moderate energy")
    assert response["next_step"] == "confirm_distance"
    
    # User proposes distance with km unit
    print("\n[Step 1] User proposes 2km...")
    response = await runner.process_message(context_id, "How about 2km?")
    print(f"Response: {response['message'][:100]}...")
    print(f"Proposed Distance: {response.get('distance_m')}m")
    assert response.get('distance_m') == 2000, "Should convert 2km to 2000m"
    assert response["next_step"] == "collect_budget"
    
    print("\n" + "="*70)
    print("✅ KM UNITS TEST PASSED!")
    print("="*70)


async def main():
    """Run all tests"""
    try:
        await test_distance_confirmation()
        await test_distance_acceptance()
        await test_distance_with_km_units()
        print("\n" + "="*70)
        print("🎉 ALL DISTANCE CONFIRMATION TESTS PASSED!")
        print("="*70)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
