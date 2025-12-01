"""Main entry point for testing the restaurant recommender system"""

import asyncio
import sys
from runner.orchestrator_runner import OrchestratorRunner


async def main():
    """Main demo function"""
    print("=" * 60)
    print("RESTAURANT RECOMMENDER - MULTI-AGENT SYSTEM DEMO")
    print("=" * 60)
    print()
    
    # Initialize orchestrator
    orchestrator = OrchestratorRunner()
    
    # Start conversation
    print("Starting conversation with user_123...")
    print()
    
    result = await orchestrator.start_conversation("user_123", "Hi, I'm hungry!")
    context_id = result["context_id"]
    
    print(f"Context ID: {context_id}")
    print(f"Environment: {result['environment']}")
    print()
    print(f"Assistant: {result['message']}")
    print()
    
    # Simulate multi-turn conversation with natural language
    conversation_flow = [
        ("user", "I'm in New York"),
        ("user", "Pretty tired after work"),  # Natural language energy: "tired" → 2
        ("user", "Mid-range sounds nice"),     # Natural language budget: "mid-range" → 2
        ("user", "Just me and a friend"),      # Natural language group: "friend" → 2
        ("user", "Thai food would be great"),  # Cuisine preference
        ("user", "Let me see recommendations"), # Request recommendations
        ("user", "1"),                         # Select first recommendation
    ]
    
    for speaker, message in conversation_flow:
        print(f"{speaker.upper()}: {message}")
        print()
        
        result = await orchestrator.process_message(context_id, message)
        
        print(f"Assistant: {result.get('message', result)}")
        print()
        
        # Show next step
        next_step = result.get('next_step')
        if next_step:
            print(f"[Next Step: {next_step}]")
            print()
        
        if next_step == "complete":
            print("=" * 60)
            print("CONVERSATION COMPLETE")
            print("=" * 60)
            break
    
    # Show final state
    print()
    print("=" * 60)
    print("FINAL CONVERSATION STATE:")
    print("=" * 60)
    state = orchestrator.state_store.get_state(context_id)
    if state:
        print(f"User ID: {state.user_id}")
        print(f"Energy Level: {state.energy_level}")
        print(f"Budget Level: {state.budget_level}")
        print(f"Group Size: {state.group_size}")
        print(f"Preferred Cuisine: {state.preferred_cuisine}")
        print(f"Search Radius: {state.search_radius_m}m")
        print(f"Candidates Found: {len(state.candidates)}")
        print(f"Recommendations: {len(state.recommendations)}")
        if state.selected_restaurant:
            print(f"Selected: {state.selected_restaurant.get('name')}")


if __name__ == "__main__":
    asyncio.run(main())
