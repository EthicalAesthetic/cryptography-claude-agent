# Claude Cryptographic Agent - Proof of Concept

> A working AI agent using Claude (AWS Bedrock) to automate PKI certificate operations with policy enforcement.

## 🎯 What This POC Demonstrates

This is a **minimal, working implementation** that shows:

✅ **AI Agent with Tool Calling** - Claude intelligently uses cryptographic tools  
✅ **Multi-Step Workflows** - Agent plans and executes complex operations  
✅ **Policy Enforcement** - Validates operations against security policies  
✅ **Cryptographic Operations** - Real key generation and certificate issuance  
✅ **Audit Logging** - Complete trail of all operations  
✅ **Natural Language Interface** - Talk to the agent in plain English  

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- AWS Account with Bedrock access
- AWS credentials

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 3. Create __init__.py files
touch src/__init__.py src/{agent,tools,policies,audit}/__init__.py

# 4. Run demo
python start_demo.py
```

## 📁 Project Structure

```
claude-crypto-agent-poc/
├── src/
│   ├── agent/
│   │   ├── orchestrator.py      # Main agent logic
│   │   └── bedrock_client.py    # AWS Bedrock integration
│   ├── tools/
│   │   ├── registry.py          # Tool management
│   │   ├── crypto_tools.py      # Key generation, CSR
│   │   ├── pki_tools.py         # Certificate issuance
│   │   └── policy_tools.py      # Policy validation
│   ├── policies/
│   │   └── engine.py            # Policy engine
│   └── audit/
│       └── logger.py            # Audit logging
├── start_start_demo.py                       # Demo script
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## 💬 Example Interactions

### Generate TLS Certificate

```
💬 You: I need a TLS certificate for api.example.com

🤖 Agent: I'll help you create a TLS server certificate for api.example.com.

Let me execute the following steps:
1. Validate request against TLS server policy
2. Generate RSA-2048 key pair
3. Create Certificate Signing Request (CSR)
4. Issue the certificate

[Executing tools...]

✅ Certificate issued successfully!

Details:
- Domain: api.example.com
- Serial: 1A2B3C4D5E6F
- Algorithm: RSA-2048
- Valid for: 365 days
- Expires: 2027-01-18
- Status: Active

The private key has been stored securely and the certificate
is ready for use.
```

### Policy Validation

```
💬 You: Can I create a certificate valid for 2 years?

🤖 Agent: No, a 2-year (730 days) validity period would violate
our certificate policy.

According to CA/Browser Forum Baseline Requirements, the maximum
allowed validity is 397 days.

Options:
1. Issue certificate for 365 days (recommended)
2. Issue certificate for 397 days (maximum allowed)
3. Set up auto-renewal for extended coverage

Which would you prefer?
```

### Information Query

```
💬 You: What's the minimum RSA key size?

🤖 Agent: Based on our cryptographic policy:

RSA Key Size Requirements:
- Minimum: 2048 bits
- Recommended: 3072 bits  
- Maximum: 4096 bits

RSA-1024 is forbidden due to insufficient security.

For most TLS certificates, RSA-2048 is sufficient and provides
a good balance of security and performance.
```

## 🛠️ How It Works

### Architecture

```
User Query
    ↓
Claude Agent (AWS Bedrock)
    ↓
Tool Framework
    ├── generate_key_pair
    ├── create_csr
    ├── issue_certificate
    ├── validate_policy
    └── get_certificate_info
    ↓
Operations Executed
    ↓
Results + Audit Log
```

### Agent Workflow

1. **User Request** - Natural language query
2. **Intent Analysis** - Claude understands what's needed
3. **Policy Check** - Validates against security policies
4. **Tool Selection** - Chooses appropriate tools
5. **Execution** - Runs cryptographic operations
6. **Verification** - Checks results
7. **Response** - Returns human-readable output
8. **Audit** - Logs everything for compliance

## 🔧 Available Tools

The agent has access to these tools:

| Tool | Purpose | Example |
|------|---------|---------|
| `generate_key_pair` | Create RSA/ECDSA keys | RSA-2048, ECDSA P-256 |
| `create_csr` | Generate certificate request | Subject DN + SANs |
| `issue_certificate` | Sign and issue certificate | TLS, code signing |
| `validate_policy` | Check policy compliance | Validity, key size |
| `get_certificate_info` | Parse certificate details | Expiry, serial number |

## 🔒 Security Features

### Private Key Protection
- Keys generated in memory (Vault integration ready)
- Private keys **NEVER** returned to agent
- Agent only receives key references (key_id)

### Policy Enforcement
- Pre-execution validation
- Hardcoded security rules:
  - RSA minimum 2048 bits
  - Max certificate validity 397 days
  - Forbidden: RSA-1024, MD5, SHA1

### Audit Trail
- Every operation logged to `audit_logs/`
- JSON format for compliance
- Includes: timestamp, operation, result, status

## 📊 Demo Scenarios

Run `python start_start_demo.py` to see:

1. **Simple TLS Certificate** - Basic certificate issuance
2. **Multiple Domains** - Certificate with SANs
3. **Policy Validation** - Compliance checking
4. **Information Queries** - Ask about policies

Or use **Interactive Mode** to chat freely with the agent.

## 🔍 What Gets Logged

Every operation creates an audit entry:

```json
{
  "timestamp": "2026-01-18T10:30:00.000Z",
  "correlation_id": "req_20260118103000123",
  "operation": "agent_request",
  "status": "success",
  "user_query": "I need a TLS certificate for api.example.com",
  "result": {
    "response": "Certificate issued successfully...",
    "tools_used": ["validate_policy", "generate_key_pair", "create_csr", "issue_certificate"]
  }
}
```

## 🎓 Key Concepts Demonstrated

### 1. Agent Orchestration
Claude plans multi-step workflows without explicit programming:
```
User: "Certificate for api.example.com"
↓
Agent Plans:
  Step 1: Validate policy
  Step 2: Generate key
  Step 3: Create CSR
  Step 4: Issue certificate
  Step 5: Return result
```

### 2. Tool Calling
Agent decides which tools to use and in what order:
```python
# Agent calls tools based on context
validate_policy(operation="certificate_issuance", ...)
generate_key_pair(algorithm="RSA", key_size=2048, ...)
create_csr(key_id="key_123", common_name="api.example.com", ...)
issue_certificate(csr_pem="...", validity_days=365, ...)
```

### 3. Policy-Driven Operations
All operations validated against policies:
```python
if validity_days > 397:
    return "Violates CA/Browser Forum requirements"
if key_size < 2048:
    return "Below minimum security standard"
```

## ⚠️ POC Limitations

This is a **proof of concept**. For production:

| POC | Production Needed |
|-----|------------------|
| In-memory keys | HashiCorp Vault |
| Mock CA | Step-CA or AWS Private CA |
| No database | PostgreSQL for inventory |
| Hardcoded policies | YAML policy files |
| No auth | User authentication + RBAC |
| File logging | Centralized logging (ELK) |

## 💰 Cost Estimate

**AWS Bedrock Pricing (Claude 3.5 Sonnet):**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Example costs:**
- Single operation: ~$0.05
- 100 operations: ~$5.00
- 1000 operations/month: ~$50

## 🚧 Extending This POC

### Add Vault Integration

```python
# Replace in crypto_tools.py
class VaultKeyStorage:
    def store_key(self, key_id, private_key):
        # Store in Vault instead of memory
        vault_client.secrets.kv.v2.create_or_update_secret(
            path=f'keys/{key_id}',
            secret={'private_key': serialize(private_key)}
        )
```

### Add Real CA (Step-CA)

```python
# Replace in pki_tools.py
async def issue_certificate(self, csr_pem):
    # Call Step-CA instead of self-signing
    response = await step_ca_client.sign(
        csr=csr_pem,
        provisioner="crypto-agent"
    )
    return response['certificate']
```

### Load YAML Policies

```python
# Enhance policy engine
class PolicyEngine:
    def load_policies(self, policy_dir):
        for policy_file in Path(policy_dir).glob('*.yaml'):
            policy = yaml.safe_load(policy_file.read_text())
            self.policies[policy['policy_id']] = policy
```

## 📚 Learning Resources

- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **Claude API**: https://docs.anthropic.com/
- **Tool Calling**: https://docs.anthropic.com/claude/docs/tool-use
- **Python Cryptography**: https://cryptography.io/

## 🤝 Contributing

This is a POC. For the full production version, see the main repository.

## 📄 License

MIT License

## 🙋 FAQ

**Q: Do I need a real Certificate Authority?**  
A: No, the POC includes a mock CA for demonstration.

**Q: Are the keys secure?**  
A: For POC, keys are in memory. Production should use Vault/HSM.

**Q: Can I use this in production?**  
A: No, this is a POC. See "POC Limitations" above.

**Q: How much does it cost to run?**  
A: ~$5 for 100 certificate operations (AWS Bedrock costs).

**Q: What models can I use?**  
A: Claude 3.5 Sonnet recommended. Other Claude models work too.

## 🎉 Success Criteria

After running the demo, you should see:

✅ Agent successfully processes natural language requests  
✅ Tools are called in correct sequence  
✅ Certificates are generated and issued  
✅ Policy violations are caught and explained  
✅ Audit logs created in `audit_logs/`  

---

**Ready to see AI-powered PKI automation in action?**

```bash
python start_start_demo.py
```

---

Built with ❤️ using Claude AI and AWS Bedrock