"""
PKI Tools - Certificate issuance, validation, etc.
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtensionOID

logger = logging.getLogger(__name__)


class IssueCertificateTool:
    """Tool for issuing certificates (simulated CA)"""
    
    name = "issue_certificate"
    description = "Issue a certificate by signing a CSR. Returns the signed certificate."
    
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
                            "csr_pem": {
                                "type": "string",
                                "description": "Certificate Signing Request in PEM format"
                            },
                            "validity_days": {
                                "type": "integer",
                                "description": "Certificate validity period in days (default: 365, max: 397)",
                                "default": 365
                            },
                            "certificate_type": {
                                "type": "string",
                                "description": "Type of certificate",
                                "enum": ["tls_server", "tls_client", "code_signing"]
                            }
                        },
                        "required": ["csr_pem", "certificate_type"]
                    }
                }
            }
        }
    
    async def execute(
        self,
        csr_pem: str,
        certificate_type: str,
        validity_days: int = 365
    ) -> Dict[str, Any]:
        """
        Issue a certificate by signing the CSR.
        
        NOTE: This is a simplified CA for POC.
        In production, this would call Step-CA or similar.
        """
        try:
            # Validate validity period
            if validity_days > 397:
                raise ValueError("Validity period cannot exceed 397 days (CA/Browser Forum requirement)")
            
            # Parse CSR
            csr = x509.load_pem_x509_csr(csr_pem.encode())
            
            # Create a self-signed CA for POC (in production, use Step-CA)
            ca_key, ca_cert = self._get_or_create_ca()
            
            # Build certificate
            subject = csr.subject
            
            # Create certificate builder
            cert_builder = x509.CertificateBuilder()
            cert_builder = cert_builder.subject_name(subject)
            cert_builder = cert_builder.issuer_name(ca_cert.subject)
            cert_builder = cert_builder.public_key(csr.public_key())
            
            # Set serial number
            serial = x509.random_serial_number()
            cert_builder = cert_builder.serial_number(serial)
            
            # Set validity
            not_before = datetime.utcnow()
            not_after = not_before + timedelta(days=validity_days)
            cert_builder = cert_builder.not_valid_before(not_before)
            cert_builder = cert_builder.not_valid_after(not_after)
            
            # Add extensions based on certificate type
            cert_builder = self._add_extensions(cert_builder, certificate_type, csr)
            
            # Sign certificate
            certificate = cert_builder.sign(ca_key, hashes.SHA256())
            
            # Convert to PEM
            cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
            
            # Get certificate info
            serial_hex = format(serial, 'X')
            
            logger.info(f"Issued {certificate_type} certificate: {serial_hex}")
            
            return {
                "certificate_pem": cert_pem,
                "serial_number": serial_hex,
                "subject": subject.rfc4514_string(),
                "issuer": ca_cert.subject.rfc4514_string(),
                "not_before": not_before.isoformat(),
                "not_after": not_after.isoformat(),
                "validity_days": validity_days,
                "certificate_type": certificate_type,
                "status": "success",
                "message": f"Certificate issued successfully. Valid for {validity_days} days."
            }
            
        except Exception as e:
            logger.error(f"Certificate issuance failed: {str(e)}")
            raise
    
    def _add_extensions(self, builder, cert_type: str, csr):
        """Add X.509 extensions based on certificate type"""
        
        # Basic Constraints - not a CA
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        )
        
        # Key Usage based on type
        if cert_type == "tls_server":
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=True
            )
        
        elif cert_type == "tls_client":
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            builder = builder.add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=True
            )
        
        # Copy SANs from CSR if present
        try:
            san_ext = csr.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            builder = builder.add_extension(san_ext.value, critical=False)
        except x509.ExtensionNotFound:
            pass
        
        return builder
    
    def _get_or_create_ca(self):
        """
        Get or create a CA key and certificate for signing.
        POC implementation - in production, use Step-CA.
        """
        if not hasattr(self, '_ca_key'):
            # Generate CA key
            self._ca_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create CA certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "POC Certificate Authority"),
                x509.NameAttribute(NameOID.COMMON_NAME, "POC CA"),
            ])
            
            ca_cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(self._ca_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.utcnow())
                .not_valid_after(datetime.utcnow() + timedelta(days=3650))
                .add_extension(
                    x509.BasicConstraints(ca=True, path_length=None),
                    critical=True,
                )
                .sign(self._ca_key, hashes.SHA256())
            )
            
            self._ca_cert = ca_cert
            logger.info("Created POC CA certificate")
        
        return self._ca_key, self._ca_cert


class GetCertificateInfoTool:
    """Tool for retrieving certificate information"""
    
    name = "get_certificate_info"
    description = "Get information about a certificate from its PEM format."
    
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
                            "certificate_pem": {
                                "type": "string",
                                "description": "Certificate in PEM format"
                            }
                        },
                        "required": ["certificate_pem"]
                    }
                }
            }
        }
    
    async def execute(self, certificate_pem: str) -> Dict[str, Any]:
        """Get certificate information"""
        try:
            # Parse certificate
            cert = x509.load_pem_x509_certificate(certificate_pem.encode())
            
            # Extract information
            serial = format(cert.serial_number, 'X')
            subject = cert.subject.rfc4514_string()
            issuer = cert.issuer.subject.rfc4514_string()
            
            # Get SANs if present
            sans = []
            try:
                san_ext = cert.extensions.get_extension_for_oid(
                    ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                sans = [str(name) for name in san_ext.value]
            except x509.ExtensionNotFound:
                pass
            
            # Check expiry
            now = datetime.utcnow()
            is_expired = now > cert.not_valid_after
            days_until_expiry = (cert.not_valid_after - now).days
            
            return {
                "serial_number": serial,
                "subject": subject,
                "issuer": issuer,
                "not_before": cert.not_valid_before.isoformat(),
                "not_after": cert.not_valid_after.isoformat(),
                "is_expired": is_expired,
                "days_until_expiry": days_until_expiry,
                "sans": sans,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse certificate: {str(e)}")
            raise
