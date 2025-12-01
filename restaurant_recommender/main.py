import asyncio
import sys
from runner.orchestrator_runner import OrchestratorRunner


async def main():
    """Main interactive CLI demo function"""
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
    
    # Interactive multi-turn conversation with user input
    while True:
        try:
            # Get user input from command line
            user_input = input("You: ").strip()
            
            if not user_input:
                print("(Please enter something)")
                continue
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\nThank you for using the Restaurant Recommender!")
                break
            
            print()
            result = await orchestrator.process_message(context_id, user_input)
            
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
                print()
                
                # Show final state
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
                
                # Ask if user wants another conversation
                print()
                try:
                    again = input("Would you like to start another conversation? (yes/no): ").strip().lower()
                    if again in ["yes", "y"]:
                        print("\n" + "=" * 60)
                        print("STARTING NEW CONVERSATION")
                        print("=" * 60)
                        print()
                        result = await orchestrator.start_conversation("user_" + str(hash(user_input))[-6:], "Hi, I'm hungry!")
                        context_id = result["context_id"]
                        print(f"Context ID: {context_id}")
                        print()
                        print(f"Assistant: {result['message']}")
                        print()
                    else:
                        break
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            print("\n\nThank you for using the Restaurant Recommender!")
            break
        except EOFError:
            print("\n\nThank you for using the Restaurant Recommender!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(main())
