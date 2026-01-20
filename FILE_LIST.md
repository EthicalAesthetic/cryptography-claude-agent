# Complete File List - Claude Crypto Agent POC

## All Files You Need to Create

### Root Directory Files

```
claude-crypto-agent-poc/
├── README.md                          ✅ Main documentation
├── SETUP_GUIDE.md                     ✅ Setup instructions
├── FILE_LIST.md                       ✅ This file
├── start_demo.py                      ✅ Demo script
├── requirements.txt                   ✅ Python dependencies
└── .env.example                       ✅ Environment template
```

### Source Code Files

```
src/
├── __init__.py                  ⬜ Create empty file 
│
├── agent/
│   ├── __init__.py              ⬜ Create empty file
│   ├── orchestrator.py          ✅ Main agent logic
│   └── bedrock_client.py        ✅ AWS Bedrock client
│
├── tools/
│   ├── __init__.py              ⬜ Create empty file
│   ├── registry.py              ✅ Tool management
│   ├── crypto_tools.py          ✅ Key generation & CSR
│   ├── pki_tools.py             ✅ Certificate operations
│   └── policy_tools.py          ✅ Policy validation
│
├── policies/
│   ├── __init__.py              ⬜ Create empty file
│   └── engine.py                ✅ Policy engine
│
└── audit/
    ├── __init__.py              ⬜ Create empty file
    └── logger.py                ✅ Audit logging
```

## Quick Setup Commands

### Linux/Mac

```bash
# Create project directory
mkdir -p claude-crypto-agent-poc
cd claude-crypto-agent-poc

# Create source directories
mkdir -p src/{agent,tools,policies,audit}

# Create empty __init__.py files
touch src/__init__.py
touch src/agent/__init__.py
touch src/tools/__init__.py
touch src/policies/__init__.py
touch src/audit/__init__.py

# Create audit logs directory
mkdir audit_logs

echo "✅ Directory structure created!"
```

### Windows (PowerShell)

```powershell
# Create project directory
New-Item -ItemType Directory -Path claude-crypto-agent-poc
cd claude-crypto-agent-poc

# Create source directories
New-Item -ItemType Directory -Path src\agent
New-Item -ItemType Directory -Path src\tools
New-Item -ItemType Directory -Path src\policies
New-Item -ItemType Directory -Path src\audit

# Create empty __init__.py files
New-Item -ItemType File -Path src\__init__.py
New-Item -ItemType File -Path src\agent\__init__.py
New-Item -ItemType File -Path src\tools\__init__.py
New-Item -ItemType File -Path src\policies\__init__.py
New-Item -ItemType File -Path src\audit\__init__.py

# Create audit logs directory
New-Item -ItemType Directory -Path audit_logs

Write-Host "✅ Directory structure created!"
```

## File Contents

### 1. src/__init__.py
```python
"""Claude Cryptographic Agent"""
__version__ = "0.1.0-poc"
```

### 2. src/agent/__init__.py
```python
"""Agent module"""
```

### 3. src/tools/__init__.py
```python
"""Tools module"""
```

### 4. src/policies/__init__.py
```python
"""Policies module"""
```

### 5. src/audit/__init__.py
```python
"""Audit module"""
```

## Verification Checklist

After creating all files, verify with:

### Linux/Mac
```bash
# Check directory structure
tree -L 3

# Expected output:
# .
# ├── README.md
# ├── SETUP_GUIDE.md
# ├── start_demo.py
# ├── requirements.txt
# ├── .env.example
# └── src
#     ├── __init__.py
#     ├── agent
#     │   ├── __init__.py
#     │   ├── orchestrator.py
#     │   └── bedrock_client.py
#     ├── tools
#     │   ├── __init__.py
#     │   ├── registry.py
#     │   ├── crypto_tools.py
#     │   ├── pki_tools.py
#     │   └── policy_tools.py
#     ├── policies
#     │   ├── __init__.py
#     │   └── engine.py
#     └── audit
#         ├── __init__.py
#         └── logger.py
```

### Windows
```powershell
# Check directory structure
Get-ChildItem -Recurse -Depth 2 | Select-Object FullName
```

## Installation Order

1. **Create directory structure** (commands above)
2. **Copy Python files** from artifacts
3. **Create __init__.py files** (empty or with version info)
4. **Copy configuration files** (.env.example, requirements.txt)
5. **Install dependencies** (`pip install -r requirements.txt`)
6. **Configure AWS** (edit .env)
7. **Run demo** (`python start_demo.py`)

## File Sizes (Approximate)

| File | Lines | Size |
|------|-------|------|
| orchestrator.py | 180 | 6 KB |
| bedrock_client.py | 100 | 3 KB |
| registry.py | 60 | 2 KB |
| crypto_tools.py | 200 | 7 KB |
| pki_tools.py | 240 | 8 KB |
| policy_tools.py | 120 | 4 KB |
| engine.py | 20 | 1 KB |
| logger.py | 70 | 2 KB |
| start_demo.py | 150 | 5 KB |
| **Total** | **~1140** | **~38 KB** |

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

When you run the POC, these will be created:

```
audit_logs/
└── audit_20260118.jsonl    # Daily audit log

# Example audit entry:
{
  "timestamp": "2026-01-18T10:30:00.000Z",
  "correlation_id": "req_20260118103000",
  "operation": "agent_request",
  "status": "success"
}
```

## Testing Your Setup

After creating all files:

```bash
# 1. Check Python version
python --version  # Should be 3.11+

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify imports
python -c "import boto3; import cryptography; print('✅ All imports OK')"

# 4. Check AWS credentials
python -c "import os; print('✅ AWS key set' if os.getenv('AWS_ACCESS_KEY_ID') else '❌ Set AWS credentials')"

# 5. Run demo
python start_demo.py
```

## Troubleshooting

### "No module named 'src'"
```bash
# Make sure you have __init__.py files
ls src/__init__.py src/agent/__init__.py
# Run from project root
pwd  # Should end with /claude-crypto-agent-poc
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### AWS errors
```bash
# Check credentials
cat .env  # Or: echo $AWS_ACCESS_KEY_ID
# Make sure model access is enabled in AWS Bedrock console
```

## Next Steps

After setup:

1. ✅ Run `python start_demo.py` - See it in action
2. ✅ Check `audit_logs/` - View operation logs
3. ✅ Try interactive mode - Chat with agent
4. ✅ Read the code - Understand how it works
5. ✅ Extend it - Add your own tools/features

## Quick Reference

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with AWS credentials

# Run
python start_demo.py

# Check logs
cat audit_logs/audit_*.jsonl | jq
```

---

# New Files

- To test if the AWS bedrock connection is implemented 
```bash
python test_bedrock.py
```
- To list all the existing models in the AWS Bedrock account
```bash
python list_models.py
```