"""
Demo Script - Test the Crypto Agent POC
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.orchestrator import create_agent


async def main():
    """Run demo scenarios"""
    
    print("=" * 70)
    print("   Claude Cryptographic Agent - Proof of Concept Demo")
    print("=" * 70)
    print()
    
    # Check for AWS credentials
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        print("⚠️  WARNING: AWS_ACCESS_KEY_ID not set in environment")
        print("   Set your AWS credentials to use AWS Bedrock")
        print("   export AWS_ACCESS_KEY_ID=your_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    print("Initializing agent...")
    agent = await create_agent()
    print("✓ Agent initialized\n")
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Scenario 1: Simple TLS Certificate Request",
            "query": "I need a TLS server certificate for api.example.com"
        },
        {
            "name": "Scenario 2: Certificate with Multiple Domains",
            "query": "Generate a TLS certificate for www.example.com with SANs: example.com, api.example.com"
        },
        {
            "name": "Scenario 3: Policy Validation",
            "query": "Can I generate a certificate valid for 500 days?"
        },
        {
            "name": "Scenario 4: Key Generation Query",
            "query": "What's the minimum key size for RSA keys?"
        }
    ]
    
    # Interactive mode or demo mode
    print("Select mode:")
    print("1. Run demo scenarios")
    print("2. Interactive chat")
    choice = input("\nChoice (1/2): ").strip()
    
    if choice == "1":
        # Demo mode
        for i, scenario in enumerate(scenarios, 1):
            print("\n" + "=" * 70)
            print(f"{scenario['name']}")
            print("=" * 70)
            print(f"\n💬 User: {scenario['query']}\n")
            
            try:
                result = await agent.process_request(scenario['query'])
                
                if result['status'] == 'success':
                    print(f"🤖 Agent:\n{result['response']}\n")
                    print(f"✓ Correlation ID: {result['correlation_id']}")
                else:
                    print(f"❌ Error: {result.get('error')}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            if i < len(scenarios):
                input("\nPress Enter to continue to next scenario...")
    
    elif choice == "2":
        # Interactive mode
        print("\n" + "=" * 70)
        print("Interactive Mode - Type 'quit' to exit")
        print("=" * 70)
        print()
        
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                print()
                result = await agent.process_request(user_input)
                
                if result['status'] == 'success':
                    print(f"🤖 Agent:\n{result['response']}\n")
                else:
                    print(f"❌ Error: {result.get('error')}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}\n")
    
    print("\n" + "=" * 70)
    print("Demo completed. Check 'audit_logs/' for audit trail.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
