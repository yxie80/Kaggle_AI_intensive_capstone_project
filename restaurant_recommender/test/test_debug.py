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
    print(f"0. Started: {result['next_step']}\n")
    
    inputs = [
        "I'm in Melbourne CBD",
        "Pretty tired",
        "Mid-range",
        "2",
        "Thai",
        "2"
    ]
    
    for i, msg in enumerate(inputs, 1):
        result = await runner.process_message(context_id, msg)
        print(f"{i}. Input: '{msg}'")
        print(f"   Next Step: {result['next_step']}")
        print(f"   Message: {result['message'][:80]}...")
        print()

asyncio.run(test())
