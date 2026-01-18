# AI-Powered Cryptographic Management Agent

> An intelligent agent system using Claude AI to automate PKI certificate lifecycle management with policy enforcement and complete auditability.

## 🎯 Problem Statement

Modern digital infrastructures rely on Public Key Infrastructure (PKI) for secure communications, but managing cryptographic assets faces critical challenges:

- **Manual processes** lead to certificate expiration outages (30% of service disruptions)
- **Inconsistent policy enforcement** creates security vulnerabilities
- **Complex workflows** require deep cryptographic expertise
- **Poor auditability** hinders compliance with SOC2, PCI-DSS, ISO27001

## 💡 Solution

An AI agent powered by Claude (via AWS Bedrock) that intelligently orchestrates cryptographic operations while enforcing organizational policies and maintaining complete audit trails.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                  (CLI / REST API / Web UI)                   │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  Claude Agent (AWS Bedrock)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Request Analysis & Intent Understanding          │  │
│  │  2. Policy Retrieval & Validation                    │  │
│  │  3. Multi-Step Workflow Planning                     │  │
│  │  4. Tool Selection & Execution                       │  │
│  │  5. Result Verification & Audit Logging              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Tool Framework                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Crypto    │  │     PKI     │  │   Policy    │         │
│  │   Tools     │  │    Tools    │  │   Engine    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                  │
│  ┌──────▼────────────────▼────────────────▼──────┐         │
│  │  • generate_key_pair                           │         │
│  │  • create_csr                                  │         │
│  │  • issue_certificate                           │         │
│  │  • renew_certificate                           │         │
│  │  • revoke_certificate                          │         │
│  │  • validate_policy                             │         │
│  │  • audit_log                                   │         │
│  └────────────────────────────────────────────────┘         │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Vault   │  │PostgreSQL│  │ Step-CA  │  │  Redis   │   │
│  │ (Keys)   │  │(Metadata)│  │  (PKI)   │  │ (Cache)  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Agent Workflow

### Example: TLS Certificate Issuance

```
User Request: "Generate a TLS certificate for api.example.com"

┌─────────────────────────────────────────────────────────┐
│ Step 1: Claude Analyzes Request                        │
│ - Intent: Issue TLS server certificate                 │
│ - Domain: api.example.com                              │
│ - Certificate Type: TLS Server Authentication          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ Step 2: Policy Validation                              │
│ - Retrieves: tls_server_policy.yaml                    │
│ - Validates: Domain ownership, naming conventions      │
│ - Determines: RSA-2048, 365 days validity required     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ Step 3: Multi-Step Plan                                │
│ 1. generate_key_pair(algorithm=RSA, size=2048)         │
│ 2. create_csr(cn=api.example.com, sans=[...])         │
│ 3. issue_certificate(csr, validity=365)                │
│ 4. validate_certificate(cert)                          │
│ 5. audit_log(operation, result)                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ Step 4: Tool Execution                                 │
│ ✓ Key generated in Vault (key_abc123)                 │
│ ✓ CSR created with proper extensions                  │
│ ✓ Certificate signed by CA                            │
│ ✓ Chain validated                                     │
│ ✓ Audit logged                                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ Step 5: Return Result                                  │
│ Certificate: api.example.com                           │
│ Serial: 1A:2B:3C:4D:5E:6F                             │
│ Expires: 2027-01-18                                    │
│ Status: Active                                         │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Core Components

### 1. Claude Agent (Orchestrator)

**Responsibilities:**
- Parse natural language requests
- Understand cryptographic intent
- Plan multi-step workflows
- Invoke tools in correct sequence
- Handle errors and rollbacks

**Technology:** AWS Bedrock (Claude 3.5 Sonnet)

### 2. Tool Framework

**Available Tools:**

| Tool | Purpose | Example |
|------|---------|---------|
| `generate_key_pair` | Create asymmetric keys | RSA-2048, ECDSA P-256 |
| `create_csr` | Generate certificate request | Subject DN + SANs |
| `issue_certificate` | Sign CSR via CA | TLS, code signing |
| `renew_certificate` | Renew expiring cert | Auto-renewal at 30 days |
| `revoke_certificate` | Revoke compromised cert | CRL/OCSP update |
| `validate_policy` | Check compliance | Policy enforcement |

### 3. Policy Engine

**Policy Structure:**
```yaml
policy_name: "TLS_Server_Certificate_Policy"
version: "1.0"

key_requirements:
  algorithms:
    - name: "RSA"
      min_size: 2048
    - name: "ECDSA"
      curves: ["P-256", "P-384"]

certificate:
  max_validity_days: 397
  required_extensions:
    - keyUsage: [digitalSignature, keyEncipherment]
    - extendedKeyUsage: [serverAuth]
```

**Enforcement:**
- Pre-execution validation (before key generation)
- Runtime checks (during certificate issuance)
- Post-execution verification (after completion)

### 4. Infrastructure

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Vault** | Secure key storage | HashiCorp Vault |
| **Step-CA** | Certificate Authority | Smallstep Step-CA |
| **PostgreSQL** | Certificate inventory | PostgreSQL 15 |
| **Redis** | Caching & queuing | Redis 7 |

## 🔒 Security Guardrails

### Critical Safety Measures

1. **Private Keys Never Exposed**
   - Keys generated directly in Vault
   - Claude only receives key_id (reference)
   - No private key material in memory or logs

2. **Policy-First Enforcement**
   - All operations validated against policies
   - Non-compliant requests rejected with explanation
   - Policy violations logged for audit

3. **Approved Algorithms Only**
   ```python
   APPROVED_ALGORITHMS = {
       "RSA": [2048, 3072, 4096],
       "ECDSA": ["P-256", "P-384", "P-521"],
       "EdDSA": ["Ed25519"]
   }
   
   FORBIDDEN_ALGORITHMS = ["RSA-1024", "MD5", "SHA1"]
   ```

4. **Complete Audit Trail**
   - Every operation logged with full context
   - Policy validation results recorded
   - Immutable audit logs (7-year retention)

## 📊 Data Flow

### Certificate Issuance Flow

```
┌──────────┐
│   User   │
└────┬─────┘
     │ "Issue TLS cert for api.example.com"
     ▼
┌─────────────────┐
│  Claude Agent   │──→ Analyze intent
└────┬────────────┘
     │
     ├──→ Query Policy: "tls_server_policy"
     │   ✓ RSA-2048 minimum
     │   ✓ 365 days max validity
     │   ✓ serverAuth EKU required
     │
     ├──→ Tool: generate_key_pair
     │   └──→ Vault: Create RSA-2048 → key_xyz
     │
     ├──→ Tool: create_csr
     │   └──→ Build CSR with extensions
     │
     ├──→ Tool: issue_certificate
     │   └──→ Step-CA: Sign CSR → cert_abc
     │
     └──→ Tool: audit_log
         └──→ PostgreSQL: Log operation
```

## 🎯 Use Cases

### 1. Automated Certificate Renewal

**Problem:** Certificates expire, causing outages

**Solution:**
```
Scheduled Agent Task (daily):
├─ Query certificates expiring in 30 days
├─ For each certificate:
│  ├─ Claude plans renewal workflow
│  ├─ Generates new CSR (optionally new key)
│  ├─ Issues replacement certificate
│  └─ Notifies administrators
└─ Update inventory and audit log
```

### 2. Policy Exception Handling

**Scenario:** User requests 2-year certificate (policy: max 397 days)

**Agent Response:**
```
Claude: "The requested validity of 730 days exceeds the maximum 
        allowed 397 days per tls_server_policy v1.0 
        (CA/Browser Forum compliance).
        
        Options:
        1. Issue certificate with 397 days validity
        2. Request policy exception approval
        3. Use shorter validity with auto-renewal
        
        Recommendation: Option 3 (365 days + auto-renewal)"
```

### 3. Emergency Revocation

**Scenario:** Private key compromise

**Workflow:**
```
User: "Emergency: Revoke cert_prod_123, key compromised"

Agent:
├─ Verifies certificate exists
├─ Confirms revocation reason: keyCompromise
├─ Executes revocation via Step-CA
├─ Updates CRL and OCSP
├─ Logs security incident
└─ Recommends: "Issue replacement with new key?"
```

## 🚀 Advantages of AI Agent Approach

### vs. Traditional PKI Management Tools

| Aspect | Traditional Tools | AI Agent (Claude) |
|--------|------------------|-------------------|
| **Interface** | Complex CLI/GUI | Natural language |
| **Workflow** | Manual configuration | Intelligent planning |
| **Policy** | Hard-coded rules | Context-aware interpretation |
| **Learning** | Static | Adapts to patterns |
| **Errors** | Cryptic messages | Plain English explanations |
| **Expertise** | Requires PKI knowledge | Guides non-experts |

### Key Benefits

✅ **Reduced Human Error** - AI validates every operation<br>
✅ **24/7 Operations** - Automated monitoring and renewal<br>
✅ **Policy Compliance** - Enforced at every step<br>
✅ **Faster Operations** - Minutes instead of hours<br>
✅ **Better Auditability** - Complete context captured<br>
✅ **Lower Training Costs** - Natural language interface<br>

## 📈 Performance Metrics

**Target Performance (1000 users):**

| Metric | Target | Notes |
|--------|--------|-------|
| Certificate Issuance | < 5 seconds | End-to-end |
| API Response Time | < 100ms (p95) | For simple queries |
| Throughput | 100 certs/minute | Parallel processing |
| Availability | 99.9% | < 9 hours downtime/year |
| Audit Lag | < 1 second | Real-time logging |

## 🛡️ Compliance & Standards

### Cryptographic Standards
- ✅ **NIST SP 800-57** - Key management recommendations
- ✅ **RFC 5280** - X.509 certificates
- ✅ **RFC 6125** - Certificate validation
- ✅ **CA/Browser Forum** - Baseline Requirements

### Compliance Frameworks
- ✅ **SOC 2** - Audit logging and access controls
- ✅ **PCI-DSS** - Cryptographic key management
- ✅ **ISO 27001** - Information security management

## 💻 Technology Stack

```yaml
Agent Framework:
  - AWS Bedrock (Claude 3.5 Sonnet)
  - Python 3.11+
  - FastAPI (REST API)

PKI Infrastructure:
  - HashiCorp Vault 1.15 (Key storage)
  - Smallstep Step-CA (Certificate Authority)
  - OpenSSL (Cryptographic operations)

Data Layer:
  - PostgreSQL 15 (Certificate inventory)
  - Redis 7 (Caching)

Deployment:
  - Docker & Docker Compose
  - On-premises deployment
```

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- AWS Account (Bedrock access)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/claude-crypto-agent.git
cd claude-crypto-agent

# Configure environment
cp .env.example .env
# Edit .env with AWS credentials

# Start infrastructure
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Initialize system
./scripts/init-vault.sh
./scripts/init-step-ca.sh

# Start agent
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### First Certificate

```bash
# Using CLI
crypto-agent cert issue \
  --cn api.example.com \
  --type tls_server \
  --validity 365

# Using natural language
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Generate a TLS certificate for api.example.com"}'
```

## 📁 Project Structure

```
claude-crypto-agent/
├── src/
│   ├── agent/              # Claude agent core
│   │   ├── orchestrator.py
│   │   ├── bedrock_client.py
│   │   └── prompts.py
│   ├── tools/              # Tool implementations
│   │   ├── crypto/
│   │   ├── pki/
│   │   └── policy/
│   ├── policies/           # Policy engine
│   ├── api/                # REST API
│   └── storage/            # Vault, database clients
├── config/
│   └── policies/           # YAML policy definitions
├── tests/                  # Test suite
├── scripts/                # Setup scripts
└── deployment/
    └── docker/             # Docker configurations
```

## 🔮 Future Enhancements

### Planned Features
- **Multi-Agent System** - Specialized agents for complex workflows
- **GraphRAG** - Intelligent policy retrieval with learning
- **ACME Protocol** - Let's Encrypt integration
- **Post-Quantum Crypto** - PQC algorithm support (NIST PQC standards)
- **Certificate Transparency** - CT log integration
- **Hardware Security Modules** - HSM support for key storage

## 📚 Documentation

- **[Architecture Details](docs/ARCHITECTURE.md)** - Deep dive into system design
- **[API Reference](docs/API.md)** - REST API documentation
- **[Policy Guide](docs/POLICIES.md)** - Creating custom policies
- **[Security Best Practices](docs/SECURITY.md)** - Hardening guide


---

## Quick Reference

### Common Commands

```bash
# Issue certificate
crypto-agent cert issue --cn example.com --type tls_server

# Renew certificate
crypto-agent cert renew --cert-id cert_123

# Revoke certificate
crypto-agent cert revoke --cert-id cert_123 --reason keyCompromise

# List expiring certificates
crypto-agent cert list --expiring-in 30

# Check policy compliance
crypto-agent policy validate --cert-id cert_123
```

### Agent Capabilities

✅ Generate RSA/ECDSA key pairs <br>
✅ Create Certificate Signing Requests<br>
✅ Issue certificates (TLS, code signing, email)<br>
✅ Renew certificates automatically<br>
✅ Revoke compromised certificates<br>
✅ Validate certificate chains<br>
✅ Enforce cryptographic policies<br>
✅ Generate compliance reports<br>
✅ Natural language interaction