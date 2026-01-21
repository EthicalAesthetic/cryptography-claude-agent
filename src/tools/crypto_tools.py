"""
Cryptographic Tools - Key generation, CSR creation, etc.
Fixed with shared key storage
"""
import logging
from typing import Dict, Any
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID

from src.tools.key_storage import key_storage  # Import shared storage

import os
from pathlib import Path

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
        """Generate a key pair with shared storage"""
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
            
            # Generate key_id
            key_id = f"key_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Store in shared storage
            key_storage.store_key(key_id, private_key)
            
            logger.info(f"Generated {algorithm_display} key pair: {key_id}")
            
            return {
                "key_id": key_id,
                "algorithm": algorithm_display,
                "public_key_pem": public_key_pem,
                "usage": usage,
                "created_at": datetime.utcnow().isoformat(),
                "status": "success",
                "message": f"✓ {algorithm_display} key pair generated successfully. Private key stored securely with ID: {key_id}"
            }
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise


class CreateCSRTool:
    """Tool for creating Certificate Signing Requests"""
    
    name = "create_csr"
    description = "Create a Certificate Signing Request (CSR) for certificate issuance. Requires a key_id from generate_key_pair."
    
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
                                "description": "ID of the private key to use (from generate_key_pair)"
                            },
                            "common_name": {
                                "type": "string",
                                "description": "Common Name (CN) - usually the domain name"
                            },
                            "organization": {
                                "type": "string",
                                "description": "Organization name",
                                "default": "Example Org"
                            },
                            "country": {
                                "type": "string",
                                "description": "Two-letter country code",
                                "default": "US"
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
        """Create a Certificate Signing Request using shared storage"""
        try:
            # Retrieve key from shared storage
            private_key = key_storage.get_key(key_id)
            
            if not private_key:
                available_keys = key_storage.list_keys()
                raise ValueError(
                    f"Key not found: {key_id}. "
                    f"Available keys: {available_keys if available_keys else 'None'}. "
                    f"Please generate a key first using generate_key_pair."
                )
            
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
            
            logger.info(f"Created CSR for: {common_name} using key: {key_id}")
            
            return {
                "csr_pem": csr_pem,
                "subject": {
                    "common_name": common_name,
                    "organization": organization,
                    "country": country
                },
                "sans": sans or [],
                "key_id": key_id,
                "status": "success",
                "message": f"✓ CSR created successfully for {common_name}"
            }
            
        except Exception as e:
            logger.error(f"CSR creation failed: {str(e)}")
            raise


"""
Add this to your crypto_tools.py file to enable certificate export
"""

class ExportCertificateTool:
    """Tool for exporting generated certificates and keys"""
    
    name = "export_certificate"
    description = "Export the most recently generated certificate and private key to files"
    
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
                                "description": "Key ID to export (from generate_key_pair)"
                            },
                            "certificate_pem": {
                                "type": "string",
                                "description": "Certificate in PEM format"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Domain name for the certificate"
                            },
                            "output_path": {
                                "type": "string",
                                "description": "Output directory path (optional)",
                                "default": "./certificates"
                            }
                        },
                        "required": ["key_id", "certificate_pem", "domain"]
                    }
                }
            }
        }
    
    async def execute(
        self,
        key_id: str,
        certificate_pem: str,
        domain: str,
        output_path: str = "./certificates"
    ) -> Dict[str, Any]:
        """Export certificate and private key to files"""
        try:
            from pathlib import Path
            from datetime import datetime
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get private key from storage
            private_key = key_storage.get_key(key_id)
            
            if not private_key:
                raise ValueError(f"Key not found: {key_id}")
            
            # Create filenames
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_domain = domain.replace(".", "_").replace("*", "wildcard")
            
            cert_file = output_dir / f"{safe_domain}_{timestamp}.crt"
            key_file = output_dir / f"{safe_domain}_{timestamp}.key"
            
            # Save certificate
            with open(cert_file, 'w') as f:
                f.write(certificate_pem)
            
            # Save private key
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
            
            with open(key_file, 'w') as f:
                f.write(private_key_pem)
            
            # Set secure permissions on private key (Unix only)
            if hasattr(os, 'chmod'):
                os.chmod(key_file, 0o600)
            
            logger.info(f"Exported certificate to: {cert_file}")
            logger.info(f"Exported private key to: {key_file}")
            
            return {
                "certificate_path": str(cert_file.absolute()),
                "key_path": str(key_file.absolute()),
                "domain": domain,
                "status": "success",
                "message": (
                    f"✅ Certificate and key exported successfully!\n\n"
                    f"📄 Certificate: {cert_file.absolute()}\n"
                    f"🔑 Private Key: {key_file.absolute()}\n\n"
                    f"⚠️ Keep the private key secure! Never share it or commit it to version control."
                )
            }
            
        except Exception as e:
            logger.error(f"Certificate export failed: {str(e)}")
            raise



