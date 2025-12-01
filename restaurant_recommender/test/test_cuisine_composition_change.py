#!/usr/bin/env python
"""Test demonstrating cuisine change during composition phase"""
import asyncio
import sys
sys.path.insert(0, '.')
from runner.orchestrator_runner import OrchestratorRunner


async def test_cuisine_change_during_composition():
    """Test that users can change cuisine even during recommendations composition"""
    print("=" * 70)
    print("TEST: Cuisine Change During Recommendations Composition")
    print("=" * 70)
    
    o = OrchestratorRunner()
    
    # Setup: Complete conversation up to recommendations
    r = await o.start_conversation('test_composition_change', 'Hi')
    context_id = r['context_id']
    
    # Collect basic info
    await o.process_message(context_id, 'Melbourne CBD')
    await o.process_message(context_id, '4')  # Energy: energetic
    await o.process_message(context_id, 'yes')  # Distance confirmed
    await o.process_message(context_id, 'mid-range')  # Budget
    await o.process_message(context_id, '2')  # Group size
    
    # Collect Thai cuisine
    print("\n[Step 1] Discovering Thai restaurants...")
    r = await o.process_message(context_id, 'Thai')
    assert r['next_step'] == 'analyze_and_compose'
    print(f"  ✓ Found Thai restaurants, ready to compose")
    
    # NOW: User changes mind about cuisine BEFORE seeing recommendations
    print("\n[Step 2] User changes cuisine to Italian (during composition phase)...")
    r = await o.process_message(context_id, 'How about Italian?')
    print(f"  Response: {r['message']}")
    print(f"  Next step: {r['next_step']}")
    assert r['next_step'] == 'discover_restaurants'
    print(f"  ✓ Cuisine change detected and processed")
    
    state = o.state_store.get_state(context_id)
    assert state is not None, "State should not be None"
    assert state.preferred_cuisine == 'Italian'
    print(f"  ✓ Cuisine updated to: {state.preferred_cuisine}")
    
    # Continue discovery
    print("\n[Step 3] Discovering Italian restaurants...")
    r = await o.process_message(context_id, '')
    print(f"  Message: {r['message'][:60]}...")
    assert 'Italian' in r['message']
    print(f"  ✓ Found Italian restaurants")
    
    # Compose recommendations
    print("\n[Step 4] Composing Italian recommendations...")
    r = await o.process_message(context_id, '')
    print(f"  Showing top recommendations:")
    lines = r['message'].split('\n')
    for line in lines[:6]:
        if line.strip():
            print(f"    {line}")
    
    assert 'recommend' in r['message'].lower()
    print(f"  ✓ Italian recommendations successfully composed")
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS: User can change cuisine during composition phase!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_cuisine_change_during_composition())
