# Complete File List - Claude Crypto Agent POC

## All Files You Need

### Root Directory Files

```
cryptography-claude-agent/
├── README.md                          ✅ Main documentation
├── COMPLETE_DEPLOYMENT_GUIDE.md       ✅ Deployment guide
├── FILE_LIST.md                       ✅ This file
├── start_demo.py                      ✅ Demo script
├── get_certificates.py                ✅ NEW: Certificate export tool
├── requirements.txt                   ✅ Python dependencies
├── .env                               ⚠️ Create from .env.example
├── .env.example                       ✅ Environment template
└── .gitignore                         ✅ Git ignore rules
```

### Source Code Files

```
src/
├── __init__.py                  ✅ Package init
│
├── agent/
│   ├── __init__.py              ✅ Module init
│   ├── orchestrator.py          ✅ Main agent (with session state)
│   └── bedrock_client.py        ✅ AWS Bedrock (with retry logic)
│
├── tools/
│   ├── __init__.py              ✅ Module init
│   ├── registry.py              ✅ Tool management
│   ├── crypto_tools.py          ✅ Key generation & CSR
│   ├── pki_tools.py             ✅ Certificate operations
│   ├── policy_tools.py          ✅ Policy validation
│   └── key_storage.py           ✅ FIXED: Shared key storage singleton
│
├── policies/
│   ├── __init__.py              ✅ Module init
│   └── engine.py                ✅ Policy engine
│
└── audit/
    ├── __init__.py              ✅ Module init
    └── logger.py                ✅ Audit logging
```

### MCP Server (Claude Desktop Integration)

```
mcp-server/
└── crypto_agent_server.py       ✅ FIXED: MCP server for Claude Desktop
```

### Generated Directories

```
certificates/                     📁 Auto-created: Saved certificates
audit_logs/                       📁 Auto-created: Audit trail
venv/                            📁 Python virtual environment
```

## 🔧 Critical Fixes Applied

### 1. key_storage.py - Singleton Export
**Problem:** `ImportError: cannot import name 'key_storage'`

**Fix Applied:**
```python
# key_storage.py - Added at end of file
key_storage = KeyStorage()  # ← THIS LINE WAS MISSING!

def get_key_storage() -> KeyStorage:
    return key_storage
```

### 2. crypto_agent_server.py - Notification Handling
**Problem:** Protocol validation error with MCP

**Fix Applied:**
```python
elif method == "notifications/initialized":
    # This is a notification - no response needed
    logger.info("Client sent initialized notification")
    return None  # ← Fixed: Don't send response for notifications
```

### 3. orchestrator.py - Session State
**Enhancement:** Tracks keys across tool calls

```python
# Added session state management
self.session_state = {
    'last_key_id': None,
    'last_csr': None
}
```

### 4. bedrock_client.py - Exponential Backoff
**Enhancement:** Handles rate limiting automatically

```python
for attempt in range(max_retries):
    try:
        response = self.client.invoke_model(...)
        break
    except ThrottlingException:
        delay = 2 ** attempt  # 2s, 4s, 8s
        await asyncio.sleep(delay)
```

## Quick Setup Commands

### Linux/Mac

```bash
# Create project directory
mkdir -p cryptography-claude-agent
cd cryptography-claude-agent

# Create source directories
mkdir -p src/{agent,tools,policies,audit}
mkdir -p mcp-server
mkdir -p certificates
mkdir -p audit_logs

# Create empty __init__.py files
touch src/__init__.py
touch src/agent/__init__.py
touch src/tools/__init__.py
touch src/policies/__init__.py
touch src/audit/__init__.py

echo "✅ Directory structure created!"
```

### Windows (PowerShell)

```powershell
# Create project directory
New-Item -ItemType Directory -Path cryptography-claude-agent
cd cryptography-claude-agent

# Create source directories
New-Item -ItemType Directory -Path src\agent
New-Item -ItemType Directory -Path src\tools
New-Item -ItemType Directory -Path src\policies
New-Item -ItemType Directory -Path src\audit
New-Item -ItemType Directory -Path mcp-server
New-Item -ItemType Directory -Path certificates
New-Item -ItemType Directory -Path audit_logs

# Create empty __init__.py files
New-Item -ItemType File -Path src\__init__.py
New-Item -ItemType File -Path src\agent\__init__.py
New-Item -ItemType File -Path src\tools\__init__.py
New-Item -ItemType File -Path src\policies\__init__.py
New-Item -ItemType File -Path src\audit\__init__.py

Write-Host "✅ Directory structure created!"
```

## File Contents (Key Files)

### 1. src/__init__.py
```python
"""Claude Cryptographic Agent"""
__version__ = "0.1.0-poc"
```

### 2. All other __init__.py files
```python
"""Module init"""
```
(Can be empty or contain just a docstring)

### 3. requirements.txt
```
boto3==1.34.34
botocore==1.34.34
cryptography==42.0.0
python-dotenv==1.0.1
rich==13.7.0
```

### 4. .env (Create this from .env.example)
```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...  # Your actual key
AWS_SECRET_ACCESS_KEY=...  # Your actual secret

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 5. .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# Logs & Certificates
*.log
audit_logs/
certificates/
*.pem
*.key
*.crt
*.csr

# IDE
.vscode/
.idea/
*.swp
.DS_Store
```


1. ✅ **Create directory structure** (commands above)
2. ✅ **Copy Python files** from artifacts or source
3. ✅ **Create __init__.py files** (empty or with docstring)
4. ✅ **Copy configuration files** (.env.example, requirements.txt)
5. ✅ **Create virtual environment** (`python -m venv venv`)
6. ✅ **Activate venv** (`source venv/bin/activate`)
7. ✅ **Install dependencies** (`pip install -r requirements.txt`)
8. ✅ **Configure AWS** (copy .env.example to .env, add credentials)
9. ✅ **Run demo** (`python start_demo.py`)

## File Sizes (Approximate)

| File | Lines | Size | Status |
|------|-------|------|--------|
| orchestrator.py | 220 | 8 KB | ✅ Enhanced with session state |
| bedrock_client.py | 180 | 6 KB | ✅ Enhanced with retry logic |
| key_storage.py | 80 | 3 KB | ✅ FIXED - singleton export added |
| crypto_tools.py | 200 | 7 KB | ✅ Uses shared storage |
| pki_tools.py | 240 | 8 KB | ✅ Working |
| policy_tools.py | 120 | 4 KB | ✅ Working |
| registry.py | 60 | 2 KB | ✅ Working |
| engine.py | 20 | 1 KB | ✅ Working |
| logger.py | 70 | 2 KB | ✅ Working |
| crypto_agent_server.py | 200 | 7 KB | ✅ FIXED - notification handling |
| start_demo.py | 150 | 5 KB | ✅ Working |
| get_certificates.py | 120 | 4 KB | ✅ NEW |
| **Total** | **~1810** | **~62 KB** | |

## Dependencies Overview

From `requirements.txt`:

```
boto3              # AWS SDK (Bedrock)
botocore           # AWS core
cryptography       # Crypto operations
python-dotenv      # Environment variables
rich               # Pretty output (optional)
```

Total install size: ~50 MB

## What Gets Generated

When you run the POC, these are auto-created:

```
audit_logs/
└── audit_20260121.jsonl    # Daily audit log

certificates/
├── api_example_com_20260121_140530.crt  # Certificate
└── api_example_com_20260121_140530.key  # Private key

mcp_server.log              # MCP server logs
```

## Testing Your Setup

After creating all files:

```bash
# 1. Check Python version
python --version  # Should be 3.11+

# 2. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test imports
python -c "from src.tools.key_storage import key_storage; print('✅ key_storage import OK')"

# 5. Test AWS connection
python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✅ AWS OK')"

# 6. Run demo
python start_demo.py
```

## Troubleshooting

### "No module named 'src'"
```bash
# Make sure you're in project root
pwd  # Should end with /cryptography-claude-agent

# Check __init__.py files exist
ls src/__init__.py src/agent/__init__.py
```

### "ImportError: cannot import name 'key_storage'"
```bash
# Check if the fix is applied
grep "key_storage = KeyStorage()" src/tools/key_storage.py

# Should return:
# key_storage = KeyStorage()

# If not found, add this line at the end of key_storage.py:
echo "key_storage = KeyStorage()" >> src/tools/key_storage.py
```

### "Server disconnected" (MCP)
```bash
# Check MCP server logs
cat mcp_server.log

# Test server manually
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python mcp-server/crypto_agent_server.py
```

### AWS/Bedrock errors
```bash
# Check credentials
cat .env

# Verify model access in AWS Console:
# Bedrock → Model access → Claude 3.5 Sonnet (should be "Access granted")
```

## New Files Summary

### Added in This Version


1. **get_certificates.py** - Export certificates with private keys
2. **key_storage.py fix** - Added singleton export
3. **crypto_agent_server.py fix** - Fixed notification handling
4. **Enhanced orchestrator.py** - Session state management
5. **Enhanced bedrock_client.py** - Exponential backoff

## Quick Reference

```bash
# Complete setup in one go
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with AWS credentials
python start_demo.py
```

## Next Steps After Setup


1. ✅ Run `python start_demo.py` - Test the agent
2. ✅ Check `audit_logs/` - View operation logs
3. ✅ Check `certificates/` - See generated certificates
4. ✅ Configure Claude Desktop MCP - Use in Claude app
5. ✅ Run `python get_certificates.py` - Export certificates

---

**Everything updated with fixes and enhancements!** 🎉