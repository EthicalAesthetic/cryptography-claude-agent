# Setup Guide - Claude Crypto Agent POC

## Quick Start (5 minutes)

### Prerequisites
- Python 3.11 or higher
- AWS Account with Bedrock access
- AWS credentials with Bedrock permissions

### Step 1: Clone/Download Files

Create this directory structure:

```
claude-crypto-agent-poc/
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   └── bedrock_client.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── crypto_tools.py
│   │   ├── pki_tools.py
│   │   └── policy_tools.py
│   ├── policies/
│   │   ├── __init__.py
│   │   └── engine.py
│   └── audit/
│       ├── __init__.py
│       └── logger.py
├── demo.py
├── requirements.txt
├── .env.example
└── README.md
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure AWS Credentials

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials
# Option 1: Use .env file
nano .env

# Option 2: Export environment variables
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-east-1"
```

### Step 4: Create __init__.py Files

```bash
# Create empty __init__.py in all directories
touch src/__init__.py
touch src/agent/__init__.py
touch src/tools/__init__.py
touch src/policies/__init__.py
touch src/audit/__init__.py
```

### Step 5: Run the Demo

```bash
# Run demo
python demo.py
```

## AWS Bedrock Setup

### Enable Claude Model Access

1. Go to AWS Console → Bedrock
2. Navigate to "Model access"
3. Click "Manage model access"
4. Enable: **Claude 3.5 Sonnet**
5. Submit request (usually instant approval)

### Required IAM Permissions

Your AWS user/role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-*"
        }
    ]
}
```

## Usage Examples

### Example 1: Generate TLS Certificate

```
💬 You: I need a TLS certificate for api.example.com

🤖 Agent:
I'll help you generate a TLS server certificate for api.example.com.
Let me:
1. Validate this request against our TLS server policy
2. Generate an RSA-2048 key pair
3. Create a Certificate Signing Request
4. Issue the certificate

[Agent executes tools...]

✅ Certificate issued successfully!
- Serial: A1B2C3D4E5F6
- Valid for: 365 days
- Expires: 2027-01-18
```

### Example 2: Policy Validation

```
💬 You: Can I create a certificate valid for 500 days?

🤖 Agent:
No, that would violate our certificate policy. The maximum validity
period is 397 days per CA/Browser Forum Baseline Requirements.

I can:
1. Issue a certificate for 365 days (recommended)
2. Issue for 397 days (maximum allowed)
3. Set up auto-renewal to extend coverage

Which would you prefer?
```

### Example 3: Key Size Query

```
💬 You: What's the minimum RSA key size allowed?

🤖 Agent:
According to our cryptographic policy:
- Minimum: RSA-2048 bits
- Recommended: RSA-3072 bits
- Maximum: RSA-4096 bits

RSA-1024 is forbidden due to security concerns.
```

## Demo Scenarios

The demo includes 4 built-in scenarios:

1. **Simple TLS Certificate** - Basic certificate issuance
2. **Multiple Domains** - Certificate with SANs
3. **Policy Validation** - Check policy compliance
4. **Information Query** - Ask about policies

## Troubleshooting

### "No module named 'src'"

Make sure you're running from the project root:
```bash
cd claude-crypto-agent-poc
python demo.py
```

### "AWS credentials not found"

Check your .env file or environment variables:
```bash
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### "Model access denied"

Enable Claude model access in AWS Bedrock console.

### "Rate limit exceeded"

AWS Bedrock has rate limits. Wait a moment and try again.

## What This POC Demonstrates

✅ **AI Agent Orchestration** - Claude plans and executes multi-step workflows
✅ **Tool Calling** - Agent uses cryptographic tools intelligently
✅ **Policy Enforcement** - Validates all operations against policies
✅ **Security** - Private keys never exposed
✅ **Audit Trail** - All operations logged to `audit_logs/`

## Limitations (POC)

⚠️ **In-Memory Storage** - Keys stored in memory (use Vault in production)
⚠️ **Self-Signed CA** - Uses mock CA (use Step-CA in production)
⚠️ **No Database** - No persistent certificate inventory
⚠️ **Simple Policies** - Hardcoded rules (use YAML files in production)

## Next Steps for Production

1. **Add HashiCorp Vault** - Secure key storage
2. **Integrate Step-CA** - Real certificate authority
3. **Add PostgreSQL** - Certificate inventory database
4. **Load YAML Policies** - Dynamic policy management
5. **Add Authentication** - User authentication and RBAC
6. **Add Web UI** - User-friendly interface
7. **Add Monitoring** - Metrics and alerts

## File Descriptions

| File | Purpose |
|------|---------|
| `demo.py` | Main entry point, demo scenarios |
| `src/agent/orchestrator.py` | Main agent logic |
| `src/agent/bedrock_client.py` | AWS Bedrock integration |
| `src/tools/registry.py` | Tool management |
| `src/tools/crypto_tools.py` | Key generation, CSR tools |
| `src/tools/pki_tools.py` | Certificate issuance |
| `src/tools/policy_tools.py` | Policy validation |
| `src/policies/engine.py` | Policy engine (stub) |
| `src/audit/logger.py` | Audit logging |

## Cost Estimate

**AWS Bedrock Claude 3.5 Sonnet Pricing:**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Example session (10 operations):**
- ~50,000 tokens total
- Cost: ~$0.75

**Monthly estimate (100 operations/day):**
- ~$22.50/month

## Support

For issues or questions:
1. Check AWS Bedrock console for model access
2. Verify AWS credentials
3. Check `audit_logs/` for operation details
4. Review error messages carefully

## License

MIT License - See LICENSE file

---

**Ready to run!** 🚀

```bash
python demo.py
```