def connection():
    # Create test_bedrock.py
    import boto3
    import json
    import os

# Load environment
    from pathlib import Path
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    client = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

    print("Testing AWS Bedrock connection...")

    try:
        response = client.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {"role": "user", "content": "Say 'Hello from Bedrock!'"}
            ]
        })
    )
    
        result = json.loads(response['body'].read())
        print("✓ Bedrock connection successful!")
        print(f"Response: {result['content'][0]['text']}")
    
    except Exception as e:
        print(f"✗ Bedrock connection failed: {e}")

connection()