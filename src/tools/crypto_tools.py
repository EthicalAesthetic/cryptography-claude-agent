"""
Cryptographic Tools - Key generation, CSR creation, etc.
"""
import logging
from typing import Dict, Any
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID

logger = logging.getLogger(__name__)


class GenerateKeyPairTool:
    """Tool for generating asymmetric key pairs"""
    
    name = "generate_key_pair"
    description = "Generate an asymmetric cryptographic key pair (RSA or ECDSA). Private key is stored securely, only public key is returned."
    
    def to_bedrock_format(self) -> Dict:
        """Convert to Bedrock tool format"""
        return {
            "toolSpec": {
                "name": self.name,
                "description": self.description,
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "algorithm": {
                                "type": "string",
                                "description": "Algorithm: RSA or ECDSA",
                                "enum": ["RSA", "ECDSA"]
                            },
                            "key_size": {
                                "type": "integer",
                                "description": "Key size for RSA (2048, 3072, 4096)",
                                "enum": [2048, 3072, 4096]
                            },
                            "curve": {
                                "type": "string",
                                "description": "Curve for ECDSA (P-256, P-384, P-521)",
                                "enum": ["P-256", "P-384", "P-521"]
                            },
                            "usage": {
                                "type": "string",
                                "description": "Key usage: tls_server, tls_client, code_signing",
                                "enum": ["tls_server", "tls_client", "code_signing"]
                            }
                        },
                        "required": ["algorithm", "usage"]
                    }
                }
            }
        }
    
    async def execute(
        self,
        algorithm: str,
        usage: str,
        key_size: int = None,
        curve: str = None
    ) -> Dict[str, Any]:
        """
        Generate a key pair.
        
        NOTE: In production, this would use Vault.
        For POC, we generate in memory and only return public key.
        """
        try:
            # Generate key based on algorithm
            if algorithm == "RSA":
                if not key_size:
                    key_size = 2048
                
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size
                )
                algorithm_display = f"RSA-{key_size}"
                
            elif algorithm == "ECDSA":
                if not curve:
                    curve = "P-256"
                
                # Map curve names to cryptography curves
                curve_map = {
                    "P-256": ec.SECP256R1(),
                    "P-384": ec.SECP384R1(),
                    "P-521": ec.SECP521R1()
                }
                
                private_key = ec.generate_private_key(curve_map[curve])
                algorithm_display = f"ECDSA-{curve}"
            
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Get public key in PEM format
            public_key_pem = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
            
            # Generate a mock key_id (in production, this would be Vault's key ID)
            key_id = f"key_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Store private key in memory (POC only - use Vault in production)
            # This is just for demonstration
            self._store_private_key(key_id, private_key)
            
            logger.info(f"Generated {algorithm_display} key pair: {key_id}")
            
            return {
                "key_id": key_id,
                "algorithm": algorithm_display,
                "public_key_pem": public_key_pem,
                "usage": usage,
                "created_at": datetime.utcnow().isoformat(),
                "status": "success",
                "message": f"{algorithm_display} key pair generated successfully. Private key stored securely."
            }
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise
    
    def _store_private_key(self, key_id: str, private_key):
        """
        Store private key (POC implementation).
        In production, this would call Vault API.
        """
        # For POC, store in a simple in-memory dict
        if not hasattr(self, '_key_storage'):
            self._key_storage = {}
        self._key_storage[key_id] = private_key
        logger.debug(f"Stored private key: {key_id}")


class CreateCSRTool:
    """Tool for creating Certificate Signing Requests"""
    
    name = "create_csr"
    description = "Create a Certificate Signing Request (CSR) for certificate issuance."
    
    def to_bedrock_format(self) -> Dict:
        """Convert to Bedrock tool format"""
        return {
            "toolSpec": {
                "name": self.name,
                "description": self.description,
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "key_id": {
                                "type": "string",
                                "description": "ID of the private key to use for signing the CSR"
                            },
                            "common_name": {
                                "type": "string",
                                "description": "Common Name (CN) - usually the domain name"
                            },
                            "organization": {
                                "type": "string",
                                "description": "Organization name"
                            },
                            "country": {
                                "type": "string",
                                "description": "Two-letter country code"
                            },
                            "sans": {
                                "type": "array",
                                "description": "Subject Alternative Names (additional domains)",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["key_id", "common_name"]
                    }
                }
            }
        }
    
    async def execute(
        self,
        key_id: str,
        common_name: str,
        organization: str = "Example Org",
        country: str = "US",
        sans: list = None
    ) -> Dict[str, Any]:
        """
        Create a Certificate Signing Request.
        """
        try:
            # In POC, retrieve key from memory (in production, use Vault)
            private_key = self._get_private_key(key_id)
            
            # Build subject name
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])
            
            # Build CSR
            builder = x509.CertificateSigningRequestBuilder()
            builder = builder.subject_name(subject)
            
            # Add SANs if provided
            if sans:
                san_list = [x509.DNSName(name) for name in sans]
                builder = builder.add_extension(
                    x509.SubjectAlternativeName(san_list),
                    critical=False
                )
            
            # Sign CSR
            csr = builder.sign(private_key, hashes.SHA256())
            
            # Convert to PEM
            csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode('utf-8')
            
            logger.info(f"Created CSR for: {common_name}")
            
            return {
                "csr_pem": csr_pem,
                "subject": {
                    "common_name": common_name,
                    "organization": organization,
                    "country": country
                },
                "sans": sans or [],
                "status": "success",
                "message": f"CSR created successfully for {common_name}"
            }
            
        except Exception as e:
            logger.error(f"CSR creation failed: {str(e)}")
            raise
    
    def _get_private_key(self, key_id: str):
        """
        Retrieve private key (POC implementation).
        In production, this would call Vault API.
        """
        # Access the key storage from GenerateKeyPairTool
        # This is a hack for POC - in production, use Vault
        from src.tools.crypto_tools import GenerateKeyPairTool
        tool = GenerateKeyPairTool()
        if hasattr(tool, '_key_storage') and key_id in tool._key_storage:
            return tool._key_storage[key_id]
        
        raise ValueError(f"Key not found: {key_id}. Please generate a key first.")
