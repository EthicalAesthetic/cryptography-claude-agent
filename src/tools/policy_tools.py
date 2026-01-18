"""
Policy Tools - Policy validation and compliance checking
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ValidatePolicyTool:
    """Tool for validating operations against policies"""
    
    name = "validate_policy"
    description = "Validate if a cryptographic operation complies with organizational policies."
    
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
                            "operation": {
                                "type": "string",
                                "description": "Type of operation to validate",
                                "enum": ["key_generation", "certificate_issuance", "certificate_renewal"]
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters to validate",
                                "properties": {
                                    "algorithm": {"type": "string"},
                                    "key_size": {"type": "integer"},
                                    "validity_days": {"type": "integer"},
                                    "certificate_type": {"type": "string"}
                                }
                            }
                        },
                        "required": ["operation", "parameters"]
                    }
                }
            }
        }
    
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate operation against policy.
        
        This is a simplified POC version.
        In production, this would load actual YAML policies.
        """
        try:
            violations = []
            warnings = []
            
            # Validate based on operation type
            if operation == "key_generation":
                violations.extend(self._validate_key_generation(parameters))
            
            elif operation == "certificate_issuance":
                violations.extend(self._validate_certificate_issuance(parameters))
            
            # Determine compliance
            is_compliant = len(violations) == 0
            
            result = {
                "operation": operation,
                "compliant": is_compliant,
                "violations": violations,
                "warnings": warnings,
                "policy_version": "1.0",
                "status": "success"
            }
            
            if is_compliant:
                result["message"] = f"✓ Operation complies with policy"
            else:
                result["message"] = f"✗ Policy violations found: {len(violations)}"
            
            logger.info(f"Policy validation: {operation} - {'PASS' if is_compliant else 'FAIL'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Policy validation failed: {str(e)}")
            raise
    
    def _validate_key_generation(self, params: Dict) -> list:
        """Validate key generation parameters"""
        violations = []
        
        algorithm = params.get("algorithm", "")
        key_size = params.get("key_size")
        
        # RSA validation
        if algorithm == "RSA":
            if not key_size:
                violations.append("RSA key_size is required")
            elif key_size < 2048:
                violations.append(f"RSA key size {key_size} is below minimum 2048 bits")
            elif key_size > 4096:
                violations.append(f"RSA key size {key_size} exceeds maximum 4096 bits")
        
        # ECDSA validation
        elif algorithm == "ECDSA":
            curve = params.get("curve", "")
            allowed_curves = ["P-256", "P-384", "P-521"]
            if curve and curve not in allowed_curves:
                violations.append(f"ECDSA curve {curve} not allowed. Use: {', '.join(allowed_curves)}")
        
        # Check for forbidden algorithms
        forbidden = ["DSA", "RSA-1024"]
        if algorithm in forbidden:
            violations.append(f"Algorithm {algorithm} is forbidden by policy")
        
        return violations
    
    def _validate_certificate_issuance(self, params: Dict) -> list:
        """Validate certificate issuance parameters"""
        violations = []
        
        validity_days = params.get("validity_days")
        cert_type = params.get("certificate_type", "")
        
        # Validity period validation
        if validity_days:
            if validity_days > 397:
                violations.append(
                    f"Validity period {validity_days} days exceeds maximum 397 days "
                    "(CA/Browser Forum Baseline Requirements)"
                )
            elif validity_days < 30:
                violations.append(f"Validity period {validity_days} days is below minimum 30 days")
        
        # Certificate type validation
        allowed_types = ["tls_server", "tls_client", "code_signing", "email"]
        if cert_type and cert_type not in allowed_types:
            violations.append(f"Certificate type {cert_type} not recognized")
        
        return violations
