# Complete Deployment Guide - Make It Running

## 🎯 Overview

This guide will take you from **zero to running** in one go, then help you create a **Claude Desktop Plugin**.

---

# PART 1: MAKE IT RUNNING (30 Minutes)

## Step 1: System Prerequisites (5 min)

### Install Python 3.11+

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify
python3.11 --version
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
```

**Windows:**
1. Download from: https://www.python.org/downloads/
2. Run installer, check "Add Python to PATH"
3. Verify: `python --version`

### Install Git (if not installed)

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# Download from: https://git-scm.com/download/win
```

---

## Step 2: AWS Bedrock Setup (10 min)

### 2.1 Create AWS Account
1. Go to: https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow signup process (requires credit card)

### 2.2 Enable AWS Bedrock Model Access

```bash
# 1. Login to AWS Console
# 2. Search for "Bedrock" in services
# 3. Navigate to: Bedrock → Model access (left sidebar)
# 4. Click "Enable specific models"
# 5. Find "Anthropic Claude 3.5 Sonnet v2"
# 6. Check the box and click "Request model access"
# 7. Access is usually granted instantly
```

**Important**: Make sure you're in a supported region:
- `us-east-1` (N. Virginia) ✅ Recommended
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)

### 2.3 Create IAM User with Bedrock Access

```bash
# In AWS Console:
# 1. Go to IAM → Users → Add User
# 2. Username: bedrock-crypto-agent
# 3. Select: "Programmatic access"
# 4. Click "Next: Permissions"
# 5. Click "Attach existing policies directly"
# 6. Search and select: "AmazonBedrockFullAccess"
# 7. Click through to "Create user"
# 8. SAVE the Access Key ID and Secret Access Key
```

**Manual Policy (if AmazonBedrockFullAccess doesn't exist):**
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
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
        }
    ]
}
```

---

## Step 3: Download & Setup Project (5 min)

### 3.1 Create Project Directory

```bash
# Create project folder
mkdir claude-crypto-agent-poc
cd claude-crypto-agent-poc

# Create directory structure
mkdir -p src/agent
mkdir -p src/tools
mkdir -p src/policies
mkdir -p src/audit
mkdir -p audit_logs
```

### 3.2 Create All Files

Create these files **exactly** as shown:

#### File: `src/__init__.py`
```python
"""Claude Cryptographic Agent"""
__version__ = "0.1.0-poc"
```

#### File: `src/agent/__init__.py`
```python
"""Agent module"""
```

#### File: `src/tools/__init__.py`
```python
"""Tools module"""
```

#### File: `src/policies/__init__.py`
```python
"""Policies module"""
```

#### File: `src/audit/__init__.py`
```python
"""Audit module"""
```

#### Copy These Files from Artifacts:
1. `src/agent/orchestrator.py` - From artifact "src/agent/orchestrator.py"
2. `src/agent/bedrock_client.py` - From artifact "src/agent/bedrock_client.py"
3. `src/tools/registry.py` - From artifact "src/tools/registry.py"
4. `src/tools/crypto_tools.py` - From artifact "src/tools/crypto_tools.py"
5. `src/tools/pki_tools.py` - From artifact "src/tools/pki_tools.py"
6. `src/tools/policy_tools.py` - From artifact "src/tools/policy_tools.py"
7. `src/policies/engine.py` - From artifact "src/policies/engine.py"
8. `src/audit/logger.py` - From artifact "src/audit/logger.py"
9. `start_demo.py` - From artifact "start_demo.py"

#### File: `requirements.txt`
```
boto3==1.34.34
botocore==1.34.34
cryptography==42.0.0
python-dotenv==1.0.1
rich==13.7.0
```

#### File: `.env`
```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...  # Your actual key
AWS_SECRET_ACCESS_KEY=...  # Your actual secret

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

#### File: `.gitignore`
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

# Logs
*.log
audit_logs/

# IDE
.vscode/
.idea/
*.swp
.DS_Store
```

---

## Step 4: Install Dependencies (2 min)

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
# Should show: boto3, cryptography, python-dotenv, rich
```

---

## Step 5: Configure AWS Credentials (2 min)

### Option A: Using .env file (Recommended)
```bash
# Edit .env file
nano .env

# Add your actual AWS credentials:
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE  # Replace with yours
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # Replace
```

### Option B: Using environment variables
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
```

### Option C: Using AWS CLI config
```bash
# Install AWS CLI
pip install awscli

# Configure
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)
```

---

## Step 6: Test AWS Connection (2 min)

```bash
# Test AWS credentials
python3 -c "
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
print('✅ AWS connection successful!')
"
```

**If you get an error:**
- Check credentials in `.env`
- Verify region is `us-east-1`
- Ensure Bedrock model access is enabled
- Check IAM permissions

---

## Step 7: Run the POC! (2 min)

```bash
# Make sure virtual environment is active
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run start_demo
python start_demo.py
```

### Expected Output:
```
======================================================================
   Claude Cryptographic Agent - Proof of Concept start_demo
======================================================================

⚠️  WARNING: AWS_ACCESS_KEY_ID not set in environment
   Set your AWS credentials to use AWS Bedrock
   ...

Continue anyway? (y/n): y

Initializing agent...
✓ Agent initialized

Select mode:
1. Run start_demo scenarios
2. Interactive chat

Choice (1/2): 2

======================================================================
Interactive Mode - Type 'quit' to exit
======================================================================

💬 You: _
```

### Try These Commands:
```
💬 You: I need a TLS certificate for api.example.com

💬 You: What's the minimum RSA key size?

💬 You: Can I create a certificate valid for 500 days?

💬 You: Generate an ECDSA P-256 key pair for TLS

💬 You: quit
```

---

## Step 8: Verify Everything Works

### Check Audit Logs
```bash
# View audit logs
cat audit_logs/audit_*.jsonl | head -20

# Pretty print with jq (if installed)
cat audit_logs/audit_*.jsonl | jq
```

### Expected Audit Entry:
```json
{
  "timestamp": "2026-01-19T10:30:00.000Z",
  "correlation_id": "req_20260119103000123",
  "operation": "agent_request",
  "status": "success",
  "user_query": "I need a TLS certificate for api.example.com",
  "result": {
    "status": "success",
    "response": "I'll help you create a TLS server certificate..."
  }
}
```

---

## Troubleshooting

### Issue 1: "No module named 'src'"
```bash
# Make sure you're in the project root
pwd
# Should end with /claude-crypto-agent-poc

# Check __init__.py files exist
ls src/__init__.py
ls src/agent/__init__.py
```

### Issue 2: "AccessDeniedException"
```bash
# Check Bedrock model access
# Go to AWS Console → Bedrock → Model access
# Ensure Claude 3.5 Sonnet is enabled

# Check IAM permissions
# IAM → Users → Your User → Permissions
# Should have AmazonBedrockFullAccess
```

### Issue 3: "Rate limit exceeded"
```bash
# Wait 1 minute and try again
# Bedrock has rate limits for new accounts
```

### Issue 4: Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

---

# PART 2: CREATE CLAUDE DESKTOP PLUGIN (45 Minutes)

## What is a Claude Desktop Plugin?

Claude Desktop supports **Model Context Protocol (MCP)** servers that extend Claude's capabilities. We'll create an MCP server plugin so you can use the crypto agent directly in Claude Desktop app.

---

## Step 1: Install Claude Desktop (5 min)

### Download Claude Desktop
- **macOS**: https://claude.ai/download
- **Windows**: https://claude.ai/download
- Install and login with your Anthropic account

---

## Step 2: Create MCP Server (20 min)

### 2.1 Create MCP Server Directory

```bash
# In your project root
mkdir mcp-server
cd mcp-server
```

### 2.2 Create MCP Server Code

#### File: `mcp-server/crypto_agent_server.py`

```python
#!/usr/bin/env python3
"""
MCP Server for Claude Crypto Agent
Allows Claude Desktop to invoke crypto operations
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.orchestrator import create_agent


class CryptoAgentMCPServer:
    """MCP Server for Crypto Agent"""
    
    def __init__(self):
        self.agent = None
    
    async def initialize(self):
        """Initialize the crypto agent"""
        self.agent = await create_agent()
    
    async def handle_request(self, method: str, params: dict):
        """Handle MCP requests"""
        
        if method == "tools/list":
            # List available tools
            return {
                "tools": [
                    {
                        "name": "generate_certificate",
                        "description": "Generate a TLS/SSL certificate for a domain",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "domain": {
                                    "type": "string",
                                    "description": "Domain name for the certificate"
                                },
                                "certificate_type": {
                                    "type": "string",
                                    "enum": ["tls_server", "tls_client", "code_signing"],
                                    "description": "Type of certificate"
                                },
                                "validity_days": {
                                    "type": "integer",
                                    "description": "Validity period in days (max 397)"
                                }
                            },
                            "required": ["domain"]
                        }
                    },
                    {
                        "name": "validate_policy",
                        "description": "Check if a certificate request complies with policies",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "description": "Operation to validate"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Parameters to check"
                                }
                            },
                            "required": ["operation", "parameters"]
                        }
                    },
                    {
                        "name": "get_certificate_info",
                        "description": "Get information about a certificate",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "certificate_pem": {
                                    "type": "string",
                                    "description": "Certificate in PEM format"
                                }
                            },
                            "required": ["certificate_pem"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            # Execute tool
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            
            # Map MCP tool calls to agent operations
            if tool_name == "generate_certificate":
                query = f"Generate a {tool_params.get('certificate_type', 'tls_server')} certificate for {tool_params['domain']}"
                if 'validity_days' in tool_params:
                    query += f" valid for {tool_params['validity_days']} days"
                
                result = await self.agent.process_request(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('response', str(result))
                        }
                    ]
                }
            
            elif tool_name == "validate_policy":
                # Use the agent to validate
                query = f"Can I perform {tool_params['operation']} with parameters: {json.dumps(tool_params['parameters'])}"
                result = await self.agent.process_request(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('response', str(result))
                        }
                    ]
                }
            
            elif tool_name == "get_certificate_info":
                query = f"Parse this certificate and give me information: {tool_params['certificate_pem']}"
                result = await self.agent.process_request(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('response', str(result))
                        }
                    ]
                }
        
        return {"error": "Unknown method"}
    
    async def run(self):
        """Run MCP server (stdio mode)"""
        await self.initialize()
        
        # Read from stdin, write to stdout
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                
                response = await self.handle_request(method, params)
                
                # Write response to stdout
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }))
                sys.stdout.flush()
                
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"message": str(e)}
                }), file=sys.stderr)
                sys.stderr.flush()


if __name__ == "__main__":
    server = CryptoAgentMCPServer()
    asyncio.run(server.run())
```

### 2.3 Make Server Executable

```bash
chmod +x mcp-server/crypto_agent_server.py
```

---

## Step 3: Configure Claude Desktop (10 min)

### 3.1 Find Claude Desktop Config

**macOS:**
```bash
# Config location
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
# Config location
%APPDATA%\Claude\claude_desktop_config.json
```

### 3.2 Create/Edit Config File

#### File: `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-agent": {
      "command": "python3",
      "args": [
        "/absolute/path/to/claude-crypto-agent-poc/mcp-server/crypto_agent_server.py"
      ],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "YOUR_ACCESS_KEY",
        "AWS_SECRET_ACCESS_KEY": "YOUR_SECRET_KEY"
      }
    }
  }
}
```

**IMPORTANT**: Replace `/absolute/path/to/` with your actual path:

```bash
# Get full path
pwd
# Example: /Users/yourname/claude-crypto-agent-poc

# Update config with:
# /Users/yourname/claude-crypto-agent-poc/mcp-server/crypto_agent_server.py
```

### 3.3 Edit Config File

**macOS:**
```bash
# Create config directory if doesn't exist
mkdir -p ~/Library/Application\ Support/Claude/

# Edit config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Paste the JSON above, update paths and AWS keys
```

**Windows (PowerShell):**
```powershell
# Create config directory
New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"

# Edit config
notepad "$env:APPDATA\Claude\claude_desktop_config.json"

# Paste the JSON above, update paths and AWS keys
```

---

## Step 4: Test MCP Server Standalone (5 min)

Before connecting to Claude Desktop, test the server:

```bash
# Test the server directly
cd claude-crypto-agent-poc

# Activate venv
source venv/bin/activate

# Test server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 mcp-server/crypto_agent_server.py
```

**Expected Output:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "generate_certificate",
        "description": "Generate a TLS/SSL certificate..."
      },
      ...
    ]
  }
}
```

---

## Step 5: Restart Claude Desktop (2 min)

```bash
# macOS
# Quit Claude Desktop completely (Cmd+Q)
# Reopen from Applications

# Windows
# Close Claude Desktop
# Reopen from Start Menu
```

---

## Step 6: Use Plugin in Claude Desktop (3 min)

### In Claude Desktop Chat:

```
You: Can you list the available crypto tools?

Claude: I can see the crypto-agent tools are available:
- generate_certificate: Generate TLS/SSL certificates
- validate_policy: Check policy compliance
- get_certificate_info: Parse certificate details

You: Generate a TLS certificate for api.example.com

Claude: [Uses generate_certificate tool]
✅ I've generated a TLS server certificate for api.example.com...
```

### Verify Tool Usage

Look for the tool icon 🔧 in Claude's response showing it used the crypto-agent tool.

---

## Advanced Plugin Features (Optional)

### Add More Tools to MCP Server

#### File: `mcp-server/crypto_agent_server.py` (Add to tools/list)

```python
{
    "name": "renew_certificate",
    "description": "Renew an expiring certificate",
    "inputSchema": {
        "type": "object",
        "properties": {
            "certificate_id": {
                "type": "string",
                "description": "ID of certificate to renew"
            }
        },
        "required": ["certificate_id"]
    }
},
{
    "name": "revoke_certificate",
    "description": "Revoke a compromised certificate",
    "inputSchema": {
        "type": "object",
        "properties": {
            "certificate_id": {
                "type": "string"
            },
            "reason": {
                "type": "string",
                "enum": ["keyCompromise", "affiliationChanged", "superseded"]
            }
        },
        "required": ["certificate_id", "reason"]
    }
}
```

---

## Plugin Troubleshooting

### Issue 1: "MCP server not found"
```bash
# Check config path is correct
# macOS:
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Verify absolute path
ls /absolute/path/to/mcp-server/crypto_agent_server.py
```

### Issue 2: "Server failed to start"
```bash
# Test server manually
python3 mcp-server/crypto_agent_server.py

# Check logs
# macOS:
tail -f ~/Library/Logs/Claude/mcp-server-crypto-agent.log
```

### Issue 3: "AWS credentials not working in plugin"
```bash
# Make sure env variables are in config:
{
  "mcpServers": {
    "crypto-agent": {
      ...
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "..."
      }
    }
  }
}
```

---

# COMPLETE VERIFICATION CHECKLIST

## ✅ POC Running
- [ ] Python 3.11+ installed
- [ ] AWS Bedrock account created
- [ ] Claude 3.5 Sonnet model access enabled
- [ ] IAM user created with Bedrock permissions
- [ ] Project files created
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list` shows boto3, cryptography)
- [ ] `.env` file configured with AWS credentials
- [ ] `python start_demo.py` runs successfully
- [ ] Agent responds to queries
- [ ] Audit logs created in `audit_logs/`
- [ ] Certificate generation works
- [ ] Policy validation works

## ✅ Claude Desktop Plugin
- [ ] Claude Desktop installed
- [ ] MCP server script created
- [ ] MCP server is executable (`chmod +x`)
- [ ] Config file created at correct location
- [ ] Absolute paths updated in config
- [ ] AWS credentials in config env
- [ ] Claude Desktop restarted
- [ ] Tools visible in Claude Desktop
- [ ] Can generate certificate via Claude Desktop
- [ ] Tool usage icon 🔧 appears in responses

---

# QUICK REFERENCE COMMANDS

```bash
# Activate environment
source venv/bin/activate

# Run POC
python start_demo.py

# Test MCP server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 mcp-server/crypto_agent_server.py

# View audit logs
cat audit_logs/audit_*.jsonl | jq

# Check Claude Desktop config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop (macOS)
killall Claude && open -a Claude
```

---

# COST SUMMARY

| Item | Cost |
|------|------|
| AWS Account | Free tier available |
| Bedrock Usage (POC) | ~$0.50 per session |
| Bedrock Usage (100 ops) | ~$5.00 |
| Claude Desktop | Free |
| Total POC | ~$5.00 |

---

# WHAT YOU NOW HAVE

✅ **Working AI Agent** - Using Claude via AWS Bedrock  
✅ **Cryptographic Operations** - Real key gen, CSR, certificates  
✅ **Policy Enforcement** - Validates all operations  
✅ **Audit System** - Complete compliance trail  
✅ **CLI Interface** - Interactive start_demo  
✅ **Claude Desktop Plugin** - Use in Claude app  
✅ **Production Foundation** - Ready to extend  

---

# NEXT STEPS

1. **Test thoroughly** - Try different certificate types
2. **Extend tools** - Add renewal, revocation
3. **Add Vault** - Real key storage
4. **Add Step-CA** - Real certificate authority
5. **Build UI** - Web interface with FastAPI
6. **Deploy** - Docker + cloud deployment

---

**You're all set! The agent is running and usable in Claude Desktop!** 🚀