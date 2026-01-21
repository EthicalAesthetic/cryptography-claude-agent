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
✅ **Claude Desktop Integration** - Use as MCP plugin in Claude Desktop app  
✅ **Local Certificate Storage** - All certificates saved to disk automatically

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- AWS Account with Bedrock access
- AWS credentials
- Claude Desktop (optional, for MCP integration)

### Installation

```bash
# 1. Clone or download the project
cd cryptography-claude-agent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 5. Run demo
python start_demo.py
```

## 📁 Project Structure

```
cryptography-claude-agent/
├── src/
│   ├── agent/
│   │   ├── orchestrator.py      # Main agent logic with session state
│   │   └── bedrock_client.py    # AWS Bedrock with retry logic
│   ├── tools/
│   │   ├── registry.py          # Tool management
│   │   ├── crypto_tools.py      # Key generation, CSR
│   │   ├── pki_tools.py         # Certificate issuance
│   │   ├── policy_tools.py      # Policy validation
│   │   └── key_storage.py       # Shared key storage (singleton)
│   ├── policies/
│   │   └── engine.py            # Policy engine
│   └── audit/
│       └── logger.py            # Audit logging
├── mcp-server/
│   └── crypto_agent_server.py   # MCP server for Claude Desktop
├── certificates/                 # Generated certificates saved here
├── audit_logs/                   # Audit trail
├── start_demo.py                # Interactive demo
├── get_certificates.py          # Certificate export tool
└── requirements.txt             # Dependencies
```

## 💬 Example Interactions

### Generate TLS Certificate

```
💬 You: Generate a TLS certificate for api.example.com

🤖 Agent: I'll help you create a TLS server certificate for api.example.com.

Executing workflow:
Step 1/3: Generating RSA-2048 key pair...
✓ Key generated: key_20260121140530

Step 2/3: Creating Certificate Signing Request...
✓ CSR created for api.example.com

Step 3/3: Issuing certificate...
✓ Certificate issued successfully!

📄 Certificate Details:
- Domain: api.example.com
- Serial: 1A2B3C4D5E6F
- Algorithm: RSA-2048
- Valid for: 365 days
- Expires: 2027-01-21
- Status: Active

💾 Certificate saved to:
   certificates/api.example.com_1A2B3C4D5E6F.pem

⚠️ Private key stored securely in session.
   Use get_certificates.py to export if needed.
```

### List Stored Certificates

```
💬 You: List all my certificates

🤖 Agent: I found 3 certificates in storage:

1. api.example.com
   Serial: 1A2B3C4D5E6F
   Expires: 2027-01-21
   File: certificates/api.example.com_1A2B3C4D5E6F.pem
   Status: ✓ Valid

2. test.example.com
   Serial: 9F8E7D6C5B4A
   Expires: 2027-01-15
   File: certificates/test.example.com_9F8E7D6C5B4A.pem
   Status: ✓ Valid

3. dev.example.com
   Serial: 3A2B1C0D9E8F
   Expires: 2026-12-20
   File: certificates/dev.example.com_3A2B1C0D9E8F.pem
   Status: ⚠️ Expires in 45 days
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

Would you like me to generate a certificate with 365 days validity?
```

## 🔧 Available Tools

The agent has access to these tools:

| Tool | Purpose | Example |
|------|---------|---------|
| `generate_key_pair` | Create RSA/ECDSA keys | RSA-2048, ECDSA P-256 |
| `create_csr` | Generate certificate request | Subject DN + SANs |
| `issue_certificate` | Sign and issue certificate | TLS, code signing |
| `validate_policy` | Check policy compliance | Validity, key size |
| `get_certificate_info` | Parse certificate details | Expiry, serial number |
| `list_certificates` | List all stored certificates | View inventory |
| `export_certificate` | Export cert and key to files | PEM format |

## 🖥️ Using with Claude Desktop

### Setup MCP Plugin

1. **Install Claude Desktop** from https://claude.ai/download

2. **Configure MCP Server**

   Edit Claude Desktop config:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "crypto-agent": {
         "command": "C:\\Users\\YourName\\Desktop\\cryptography-claude-agent\\venv\\Scripts\\python.exe",
         "args": [
           "C:\\Users\\YourName\\Desktop\\cryptography-claude-agent\\mcp-server\\crypto_agent_server.py"
         ],
         "env": {
           "AWS_REGION": "us-east-1",
           "AWS_ACCESS_KEY_ID": "your_key",
           "AWS_SECRET_ACCESS_KEY": "your_secret"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Use in Chat**
   ```
   Generate a TLS certificate for test.example.com
   ```

   Claude will use the crypto-agent tool and return the certificate!

## 🔒 Security Features

### Private Key Protection
- Keys generated in memory using singleton storage pattern
- Private keys **NEVER** returned to Claude
- Agent only receives key references (key_id)
- Keys persist during session, cleared on shutdown
- Production: Integrate HashiCorp Vault

### Certificate Storage
- **Automatic local storage** - All certificates saved to `certificates/` directory
- Filename format: `{domain}_{serial}.pem`
- Special characters sanitized (wildcards, slashes)
- File path returned in agent response
- Easy backup and retrieval

### Policy Enforcement
- Pre-execution validation
- Hardcoded security rules:
  - RSA minimum 2048 bits
  - Max certificate validity 397 days
  - Forbidden: RSA-1024, MD5, SHA1
  - ECDSA curves: P-256, P-384, P-521 only

### Audit Trail
- Every operation logged to `audit_logs/`
- JSON format for compliance
- Includes: timestamp, operation, result, status, correlation_id

### Session State Management
- Agent tracks generated keys across tool calls
- Multi-step workflows maintain context
- Exponential backoff for AWS Bedrock rate limiting

## 📊 Demo Scenarios

Run `python start_demo.py` to see:

1. **Simple TLS Certificate** - Basic certificate issuance
2. **Multiple Domains** - Certificate with SANs
3. **Policy Validation** - Compliance checking
4. **Information Queries** - Ask about policies
5. **List Certificates** - View stored certificates

Or use **Interactive Mode** to chat freely with the agent.

## 📝 What Gets Logged

Every operation creates an audit entry in `audit_logs/`:

```json
{
  "timestamp": "2026-01-21T14:05:30.000Z",
  "correlation_id": "req_20260121140530123",
  "operation": "agent_request",
  "status": "success",
  "user_query": "Generate a TLS certificate for api.example.com",
  "result": {
    "response": "Certificate issued successfully...",
    "tools_used": ["generate_key_pair", "create_csr", "issue_certificate"],
    "certificate_path": "certificates/api.example.com_1A2B3C4D5E6F.pem"
  }
}
```

## 🎓 Key Concepts Demonstrated

### 1. Agent Orchestration with Session State
Claude maintains context across multiple tool calls:
```python
# Agent tracks generated keys
session_state = {
    'last_key_id': 'key_20260121140530',
    'last_csr': 'available'
}

# Workflow:
1. Generate key → store key_id in session
2. Create CSR → use key_id from session
3. Issue cert → use CSR from previous step
4. Save cert → automatically to certificates/ folder
```

### 2. Shared Key Storage Singleton
Prevents "key not found" errors:
```python
# key_storage.py uses singleton pattern
key_storage = KeyStorage()  # Global instance

# Tools access the same storage
generate_key_pair → key_storage.store_key()
create_csr → key_storage.get_key()  # Gets same key
```

### 3. Automatic Certificate Persistence
All certificates are automatically saved:
```python
# In IssueCertificateTool.execute()
cert_filename = f"{CERT_DIR}/{safe_cn}_{serial_hex}.pem"
with open(cert_filename, 'w') as f:
    f.write(cert_pem)

# Returns path in response
return {
    "certificate_pem": cert_pem,
    "file_path": cert_filename,
    ...
}
```

### 4. Exponential Backoff for Rate Limiting
Handles AWS Bedrock throttling gracefully:
```python
for attempt in range(3):
    try:
        response = bedrock.invoke_model(...)
        break
    except ThrottlingException:
        delay = 2 ** attempt  # 2s, 4s, 8s
        await asyncio.sleep(delay)
```

## ⚠️ POC Limitations

This is a **proof of concept**. For production:

| POC | Production Needed |
|-----|------------------|
| In-memory keys (session) | HashiCorp Vault / AWS KMS |
| Mock CA (self-signed) | Step-CA or AWS Private CA |
| File-based cert storage | Database inventory (PostgreSQL) |
| Hardcoded policies | YAML policy files |
| No auth | User authentication + RBAC |
| File logging | Centralized logging (ELK) |
| No monitoring | Prometheus + Grafana |
| No backup | Automated cert backup/rotation |

## 💰 Cost Estimate

**AWS Bedrock Pricing (Claude 3.5 Sonnet):**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Example costs:**
- Single certificate generation: ~$0.05
- 100 operations: ~$5.00
- 1000 operations/month: ~$50

**Free tier:** AWS Bedrock offers free tier for first 2 months

## 🛠️ Troubleshooting

### Common Issues

#### "Key not found" Error
**Fix:** Updated! The singleton pattern in `key_storage.py` now prevents this.

```python
# Fixed in key_storage.py
key_storage = KeyStorage()  # This line was missing before!
```

#### Certificates Not Being Saved
**Fix:** Updated `pki_tools.py` now automatically saves all certificates.

```bash
# Check if certificates folder exists and has files
ls -la certificates/

# Should see files like:
# api.example.com_1A2B3C4D5E6F.pem
# test.example.com_9F8E7D6C5B4A.pem
```

#### AWS Bedrock Rate Limiting
**Fix:** Exponential backoff now handles this automatically.

```python
# Retries with delays: 2s, 4s, 8s
Throttled by Bedrock (attempt 1/3). Waiting 2s...
```

#### Import Errors
```bash
# Make sure all __init__.py files exist
ls src/__init__.py
ls src/agent/__init__.py
ls src/tools/__init__.py
ls src/policies/__init__.py
ls src/audit/__init__.py
```

#### MCP Server Won't Connect
```bash
# Check the log file
cat mcp_server.log

# Test server manually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python mcp-server/crypto_agent_server.py
```

## 📚 Additional Tools

### Export Certificates
```bash
# Run the export script
python get_certificates.py

# Lists available keys in session
# Helps you export certificates with private keys
```

### View Stored Certificates
```bash
# List all certificates in storage
ls -lh certificates/

# View certificate details
openssl x509 -in certificates/api.example.com_1A2B3C4D5E6F.pem -text -noout
```

### View Logs
```bash
# View audit logs
cat audit_logs/audit_*.jsonl | jq

# View MCP server logs
cat mcp_server.log
```

## 🚧 Extending This POC

### Add Vault Integration

```python
# Replace in crypto_tools.py
from hvac import Client

vault_client = Client(url='http://vault:8200')

class VaultKeyStorage:
    def store_key(self, key_id, private_key):
        vault_client.secrets.kv.v2.create_or_update_secret(
            path=f'keys/{key_id}',
            secret={'private_key': serialize(private_key)}
        )
```

### Add Real CA (Step-CA)

```python
# Replace in pki_tools.py
async def issue_certificate(self, csr_pem):
    response = requests.post(
        'https://step-ca:9000/sign',
        json={'csr': csr_pem},
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()['certificate']
```

### Add Database for Certificate Inventory

```python
# Add to pki_tools.py
import sqlite3

def save_certificate_metadata(serial, domain, expiry, file_path):
    conn = sqlite3.connect('certificates.db')
    conn.execute('''
        INSERT INTO certificates (serial, domain, expiry, file_path, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (serial, domain, expiry, file_path, datetime.now()))
    conn.commit()
    conn.close()
```

## 📖 Learning Resources

- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **Claude API**: https://docs.anthropic.com/
- **Tool Calling**: https://docs.anthropic.com/claude/docs/tool-use
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Python Cryptography**: https://cryptography.io/

## 🤝 Contributing

This is a POC demonstrating the concept. For production use:
1. Fork the repository
2. Add Vault integration
3. Implement proper CA
4. Add authentication
5. Add database for cert inventory
6. Implement backup and rotation
7. Deploy to production

## 📄 License

MIT License

## 🙋 FAQ

**Q: Where are the certificates saved?**  
A: In the `certificates/` folder in your project directory. Files are automatically named like `domain_name_SERIAL.pem`.

**Q: How do I find my certificates?**  
A: Use the `list_certificates` tool by asking the agent "list all my certificates" or check the `certificates/` folder directly.

**Q: How do I get the private key?**  
A: Use `python get_certificates.py` - private keys are stored in session memory during runtime.

**Q: Are the keys secure?**  
A: For POC, keys are in memory during session and cleared on exit. Production should use Vault/HSM.

**Q: Can I use this in production?**  
A: Not as-is. See "POC Limitations" and implement Vault, real CA, database, auth, etc.

**Q: Why does it say "key not found"?**  
A: This is fixed! Make sure you have the updated `key_storage.py` with the singleton export.

**Q: What if I hit rate limits?**  
A: The agent now has exponential backoff built-in. Just wait a moment between requests.

**Q: Can I backup my certificates?**  
A: Yes! The `certificates/` folder contains all issued certificates. Just copy/backup this folder regularly.

**Q: What format are the certificates in?**  
A: All certificates are in PEM format (`.pem` files), which is the standard format for X.509 certificates.

## 🎉 Success Criteria

After running the demo, you should see:

✅ Agent successfully processes natural language requests  
✅ Tools are called in correct sequence  
✅ Keys persist across tool calls (no "key not found" errors)  
✅ **Certificates are automatically generated and saved to `certificates/` folder**  
✅ **You can list stored certificates using the agent**  
✅ Policy violations are caught and explained  
✅ Audit logs created in `audit_logs/`  
✅ Exponential backoff handles rate limiting  
✅ MCP server works in Claude Desktop (if configured)  
✅ **Certificate files are properly named and accessible**

## 🔍 Verify Installation

After generating a certificate, verify everything works:

```bash
# 1. Check if certificate was created
ls -l certificates/

# 2. Verify certificate is valid
openssl x509 -in certificates/*.pem -text -noout

# 3. Check audit logs
cat audit_logs/*.jsonl | tail -n 5

# 4. Ask agent to list certificates
python start_demo.py
# Then type: "list all my certificates"
```

---

**Ready to see AI-powered PKI automation in action?**

```bash
python start_demo.py
```

**Example commands to try:**
- "Generate a TLS certificate for api.example.com"
- "List all my certificates"
- "Can I create a 5-year certificate?"
- "Show me certificate info for my latest cert"

---

Built with ❤️ using Claude AI and AWS Bedrock
