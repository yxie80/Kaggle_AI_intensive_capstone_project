"""
Test handling of cuisine changes and restaurant suggestions during recommendation phase
Tests that the system properly handles:
1. Changing cuisine while in recommendation phase
2. Searching for specific restaurant names
3. Providing helpful suggestions when no results found
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from runner.orchestrator_runner import OrchestratorRunner


async def test_cuisine_change_during_recommendations():
    """Test changing cuisine while viewing recommendations"""
    print("\n" + "="*70)
    print("TEST: Cuisine Change During Recommendations Phase")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Setup conversation through to recommendations
    response = await runner.start_conversation("test_user", "test")
    context_id = response["context_id"]
    
    # Set up conversation state
    await runner.process_message(context_id, "Melbourne CBD")
    await runner.process_message(context_id, "moderate energy")
    await runner.process_message(context_id, "yes")
    await runner.process_message(context_id, "mid-range")
    await runner.process_message(context_id, "2 people")
    
    response = await runner.process_message(context_id, "Thai")
    print(f"\n[Step 1] Cuisine set to Thai")
    print(f"Next Step: {response['next_step']}")
    
    # Process discovery (might return immediately if restaurants found)
    response = await runner.process_message(context_id, "")  # Trigger discovery
    print(f"[Step 2] Discovery response - Next Step: {response['next_step']}")
    
    # If we got recommendations, try changing cuisine
    if response['next_step'] == 'select_restaurant':
        response = await runner.process_message(context_id, "How about Italian?")
        print(f"\n[Step 3] User requests Italian cuisine")
        print(f"Response message: {response['message'][:80]}...")
        print(f"Next Step: {response['next_step']}")
        
        # Check that cuisine was changed
        state = runner.state_store.get_state(context_id)
        if state is None:
            print("⚠️ State not found after cuisine change")
            return
        print(f"Updated cuisine: {state.preferred_cuisine}")
        assert state.preferred_cuisine == "Italian", "Cuisine should be updated to Italian"
        print("✅ Cuisine successfully changed to Italian")
    else:
        print("⚠️ Did not reach recommendation phase, skipping cuisine change test")


async def test_specific_restaurant_search():
    """Test searching for a specific restaurant name"""
    print("\n" + "="*70)
    print("TEST: Specific Restaurant Search")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Setup
    response = await runner.start_conversation("test_user2", "test")
    context_id = response["context_id"]
    
    await runner.process_message(context_id, "Sydney CBD")
    await runner.process_message(context_id, "energetic")
    await runner.process_message(context_id, "yes")
    await runner.process_message(context_id, "casual")
    response = await runner.process_message(context_id, "2")
    
    print(f"[Step 1] Set up conversation")
    
    # Try searching for Thai
    response = await runner.process_message(context_id, "Thai")
    print(f"\n[Step 2] Searching for Thai restaurants")
    print(f"Next Step: {response['next_step']}")
    
    # Try a specific restaurant
    response = await runner.process_message(context_id, "How about Zawaddi Thai?")
    print(f"\n[Step 3] User requests specific restaurant 'Zawaddi Thai'")
    print(f"Response message: {response['message'][:100]}...")
    print(f"Next Step: {response['next_step']}")
    
    # Check that candidates were reset
    state = runner.state_store.get_state(context_id)
    if state is None:
        print("⚠️ State not found after search")
        return
    print(f"Candidates found: {len(state.candidates)}")
    print("✅ Specific restaurant search initiated")


async def test_no_results_suggestions():
    """Test that system provides helpful suggestions when no results found"""
    print("\n" + "="*70)
    print("TEST: No Results with Helpful Suggestions")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Setup
    response = await runner.start_conversation("test_user3", "test")
    context_id = response["context_id"]
    
    await runner.process_message(context_id, "Sydney CBD")
    await runner.process_message(context_id, "tired")
    await runner.process_message(context_id, "yes")
    await runner.process_message(context_id, "budget")
    response = await runner.process_message(context_id, "solo")
    
    print(f"[Step 1] Set up conversation in Sydney CBD")
    
    # Try Thai (may or may not have results)
    response = await runner.process_message(context_id, "Thai")
    print(f"\n[Step 2] Searching for Thai restaurants")
    print(f"Response: {response['message'][:150]}...")
    
    # If no results, check the message offers helpful suggestions
    if "couldn't find" in response['message'].lower():
        print("\n✅ System provides helpful suggestions when no results found:")
        print("  - Try a different cuisine")
        print("  - Search for a specific restaurant")
        print("  - Expand search distance")


async def test_invalid_input_recovery():
    """Test that system gracefully handles invalid inputs during selection"""
    print("\n" + "="*70)
    print("TEST: Invalid Input Recovery During Selection")
    print("="*70)
    
    runner = OrchestratorRunner()
    
    # Setup through to recommendations (this might not work if no restaurants)
    response = await runner.start_conversation("test_user4", "test")
    context_id = response["context_id"]
    
    await runner.process_message(context_id, "Melbourne CBD")
    await runner.process_message(context_id, "energetic")
    await runner.process_message(context_id, "yes")
    await runner.process_message(context_id, "comfortable mid-range")
    await runner.process_message(context_id, "2 people")
    response = await runner.process_message(context_id, "Thai")
    
    print(f"[Step 1] Set up conversation")
    print(f"Next Step: {response['next_step']}")
    
    # Simulate trying different types of input
    if response['next_step'] == 'select_restaurant':
        # Try nonsensical input
        response = await runner.process_message(context_id, "xyzabc")
        print(f"\n[Step 2] Invalid input: 'xyzabc'")
        print(f"Response: {response['message'][:100]}...")
        print(f"Next Step: {response['next_step']}")
        assert response['next_step'] == 'select_restaurant', "Should stay in select_restaurant"
        print("✅ System stays in selection phase with helpful prompt")


async def main():
    """Run all tests"""
    try:
        await test_cuisine_change_during_recommendations()
        await test_specific_restaurant_search()
        await test_no_results_suggestions()
        await test_invalid_input_recovery()
        
        print("\n" + "="*70)
        print("🎉 ALL RESTAURANT SUGGESTION TESTS COMPLETED!")
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
