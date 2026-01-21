#!/usr/bin/env python3
"""
Retrieve and display certificates from the agent's session
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.tools.key_storage import key_storage
from cryptography.hazmat.primitives import serialization


def export_certificate(key_id: str, cert_pem: str, domain: str):
    """Export certificate and key to files"""
    
    # Create output directory
    output_dir = project_root / "certificates"
    output_dir.mkdir(exist_ok=True)
    
    # Get private key
    private_key = key_storage.get_key(key_id)
    
    if not private_key:
        print(f"❌ Key not found: {key_id}")
        print(f"Available keys: {key_storage.list_keys()}")
        return None
    
    # Create filenames
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_domain = domain.replace(".", "_").replace("*", "wildcard")
    
    cert_file = output_dir / f"{safe_domain}_{timestamp}.crt"
    key_file = output_dir / f"{safe_domain}_{timestamp}.key"
    
    # Save certificate
    with open(cert_file, 'w') as f:
        f.write(cert_pem)
    
    # Save private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    with open(key_file, 'w') as f:
        f.write(private_key_pem)
    
    # Set secure permissions (Unix only)
    if hasattr(os, 'chmod'):
        os.chmod(key_file, 0o600)
    
    print(f"✅ Certificate exported successfully!")
    print(f"📄 Certificate: {cert_file.absolute()}")
    print(f"🔑 Private Key: {key_file.absolute()}")
    print()
    print("⚠️  IMPORTANT: Keep your private key secure!")
    print("   - Never share it")
    print("   - Never commit it to git")
    print("   - Store it in a secure location")
    
    return {
        "cert_path": str(cert_file.absolute()),
        "key_path": str(key_file.absolute())
    }


def list_keys():
    """List all stored keys"""
    keys = key_storage.list_keys()
    
    print("=" * 70)
    print("Available Keys in Session")
    print("=" * 70)
    
    if not keys:
        print("No keys found in session.")
        print()
        print("Keys are stored in memory during the agent's session.")
        print("To generate a new key, use the agent to create a certificate.")
    else:
        for i, key_id in enumerate(keys, 1):
            print(f"{i}. {key_id}")
    
    print("=" * 70)
    return keys


def main():
    print()
    print("=" * 70)
    print("Certificate Export Tool")
    print("=" * 70)
    print()
    
    # List available keys
    keys = list_keys()
    
    if not keys:
        print()
        print("💡 Tip: Generate a certificate first using the agent.")
        return
    
    print()
    print("This tool can export certificates with their private keys.")
    print()
    
    # Manual export mode
    print("To export a certificate, you need:")
    print("  1. Key ID (from the list above)")
    print("  2. Certificate PEM (from the agent's response)")
    print("  3. Domain name")
    print()
    
    choice = input("Do you have this information to export? (y/n): ").strip().lower()
    
    if choice == 'y':
        key_id = input("Enter Key ID: ").strip()
        domain = input("Enter domain name: ").strip()
        print()
        print("Paste the certificate PEM (including BEGIN/END lines).")
        print("Press Ctrl+D (Unix) or Ctrl+Z then Enter (Windows) when done:")
        print()
        
        cert_lines = []
        try:
            while True:
                line = input()
                cert_lines.append(line)
        except EOFError:
            pass
        
        cert_pem = "\n".join(cert_lines)
        
        if cert_pem and key_id and domain:
            print()
            export_certificate(key_id, cert_pem, domain)
        else:
            print("❌ Missing required information")
    else:
        print()
        print("📖 How to get certificate information:")
        print()
        print("1. In Claude Desktop, when you generate a certificate,")
        print("   look for the response containing:")
        print("   - Key ID (like 'key_20260121123456')")
        print("   - Certificate PEM (-----BEGIN CERTIFICATE-----...)")
        print()
        print("2. Copy those values and run this script again")
        print()
        print("Or check the agent's response in Claude Desktop and")
        print("look for the certificate details.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()