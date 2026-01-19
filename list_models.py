"""
List available Bedrock models in your account
"""
import boto3
import os
from pathlib import Path

# Load .env
env_file = Path('.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

client = boto3.client(
    'bedrock',
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

print("Fetching available models...\n")

try:
    # List foundation models
    response = client.list_foundation_models()
    
    print("Available Claude models:")
    for model in response['modelSummaries']:
        if 'claude' in model['modelId'].lower():
            print(f"\n  Model ID: {model['modelId']}")
            print(f"  Name: {model['modelName']}")
            print(f"  Provider: {model['providerName']}")
    
    # List inference profiles
    print("\n\nAvailable Inference Profiles:")
    try:
        profiles = client.list_inference_profiles()
        for profile in profiles.get('inferenceProfileSummaries', []):
            if 'claude' in profile.get('inferenceProfileName', '').lower():
                print(f"\n  Profile ID: {profile.get('inferenceProfileId')}")
                print(f"  Name: {profile.get('inferenceProfileName')}")
    except Exception as e:
        print(f"  (Could not list inference profiles: {e})")
    
except Exception as e:
    print(f"Error: {e}")