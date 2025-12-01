import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runner.orchestrator_runner import OrchestratorRunner

async def test():
    runner = OrchestratorRunner()
    
    # Start
    result = await runner.start_conversation("user_123", "Hi!")
    context_id = result["context_id"]
    print(f"0. Next Step: {result['next_step']}\n")
    
    inputs = [
        "I'm in Melbourne CBD",
        "Pretty tired",
        "Mid-range",
        "2",
        "Thai",
        "2",
        "2"
    ]
    
    for i, msg in enumerate(inputs, 1):
        result = await runner.process_message(context_id, msg)
        print(f"{i}. Input: '{msg}'")
        print(f"   Next Step: {result.get('next_step')}")
        # Check state
        state = runner.state_store.get_state(context_id)
        print(f"   State: location={bool(state.location)}, energy={state.energy_level}, budget={state.budget_level}, group={state.group_size}, cuisine={state.preferred_cuisine}, candidates={len(state.candidates)}, recommendations={len(state.recommendations)}")
        print()

asyncio.run(test())
