"""
Audit Logger - Records all operations for compliance
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit logger for cryptographic operations.
    Simplified for POC - writes to JSON files.
    """
    
    def __init__(self, audit_dir: str = "audit_logs"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized Audit Logger: {self.audit_dir}")
    
    async def log_operation(
        self,
        operation: str,
        correlation_id: str,
        user_query: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        status: str = "success"
    ):
        """
        Log an operation to audit trail.
        
        Args:
            operation: Type of operation
            correlation_id: Unique identifier for this operation
            user_query: Original user request
            result: Operation result
            error: Error message if failed
            status: success or error
        """
        try:
            # Create audit entry
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
                "operation": operation,
                "status": status,
                "user_query": user_query,
                "result": result,
                "error": error
            }
            
            # Write to daily log file
            today = datetime.utcnow().strftime("%Y%m%d")
            log_file = self.audit_dir / f"audit_{today}.jsonl"
            
            with open(log_file, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
            
            logger.info(f"Audit logged: {correlation_id} - {operation} - {status}")
            
        except Exception as e:
            logger.error(f"Failed to write audit log: {str(e)}")
            # Don't raise - audit failures shouldn't break operations


async def create_audit_logger() -> AuditLogger:
    """Factory function to create audit logger"""
    return AuditLogger()
