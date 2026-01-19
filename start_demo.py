"""
Fixed demo launcher - Works with Python 3.13
"""
import asyncio
import os
import sys
from pathlib import Path

# Ensure project directory is in path
project_dir = Path(__file__).parent.absolute()
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

print(f"Project directory: {project_dir}")
print(f"Python version: {sys.version}")

# Import with error handling
try:
    print("Importing bedrock_client...")
    from src.agent.bedrock_client import BedrockClient
    print("✓ bedrock_client imported")
    
    print("Importing tool registry...")
    from src.tools.registry import ToolRegistry
    print("✓ registry imported")
    
    print("Importing policy engine...")
    from src.policies.engine import PolicyEngine
    print("✓ policy engine imported")
    
    print("Importing audit logger...")
    from src.audit.logger import AuditLogger
    print("✓ audit logger imported")
    
    print("Importing orchestrator...")
    from src.agent.orchestrator import CryptoAgent
    print("✓ orchestrator imported")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print(f"\nChecking file exists:")
    print(f"  bedrock_client.py: {(project_dir / 'src' / 'agent' / 'bedrock_client.py').exists()}")
    print(f"  orchestrator.py: {(project_dir / 'src' / 'agent' / 'orchestrator.py').exists()}")
    sys.exit(1)


async def create_agent():
    """Create agent instance"""
    bedrock = BedrockClient(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or "",
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or ""
    )
    
    tools = ToolRegistry()
    policies = PolicyEngine()
    audit = AuditLogger()
    
    return CryptoAgent(
        bedrock_client=bedrock,
        tool_registry=tools,
        policy_engine=policies,
        audit_logger=audit
    )


async def main():
    """Run demo"""
    
    print("\n" + "=" * 70)
    print("   Claude Cryptographic Agent - Proof of Concept Demo")
    print("=" * 70)
    print()
    
    # Load .env file if exists
    env_file = project_dir / '.env'
    if env_file.exists():
        print("Loading .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✓ Environment loaded\n")
    
    # Check for AWS credentials
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        print("⚠️  WARNING: AWS_ACCESS_KEY_ID not set")
        print()
        print("To use AWS Bedrock, set credentials in .env file:")
        print("  AWS_ACCESS_KEY_ID=your_key")
        print("  AWS_SECRET_ACCESS_KEY=your_secret")
        print("  AWS_REGION=us-east-1")
        print()
        response = input("Continue anyway for testing? (y/n): ")
        if response.lower() != 'y':
            return
    
    print("Initializing agent...")
    try:
        agent = await create_agent()
        print("✓ Agent initialized\n")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Interactive mode
    print("=" * 70)
    print("Interactive Mode - Type 'quit' to exit")
    print("=" * 70)
    print()
    print("Example commands:")
    print("  • I need a TLS certificate for api.example.com")
    print("  • What's the minimum RSA key size?")
    print("  • Can I create a certificate valid for 500 days?")
    print("  • Generate an ECDSA P-256 key pair")
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
            print("Processing...")
            result = await agent.process_request(user_input)
            
            if result['status'] == 'success':
                print(f"\n🤖 Agent:\n{result['response']}\n")
                print(f"✓ Correlation ID: {result['correlation_id']}")
            else:
                print(f"\n❌ Error: {result.get('error')}\n")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")