"""
iTechSmart Suite - License Management System
Handles license validation, trial periods, and feature restrictions
"""

import os
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import uuid


class LicenseManager:
    """Manages license keys, validation, and trial periods"""

    # License types
    LICENSE_TRIAL = "trial"
    LICENSE_BASIC = "basic"
    LICENSE_PROFESSIONAL = "professional"
    LICENSE_ENTERPRISE = "enterprise"
    LICENSE_UNLIMITED = "unlimited"

    # Trial period (30 days)
    TRIAL_DAYS = 30

    def __init__(self, license_file: str = "license.dat"):
        self.license_file = license_file
        self.secret_key = self._get_secret_key()
        self.cipher = self._init_cipher()

    def _get_secret_key(self) -> bytes:
        """Get or generate secret key for encryption"""
        # In production, this should be securely stored
        return b"iTechSmart-Suite-License-Key-2025-Secure"

    def _init_cipher(self) -> Fernet:
        """Initialize Fernet cipher for encryption"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"itechsmart_salt",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
        return Fernet(key)

    def generate_license_key(
        self,
        license_type: str,
        customer_name: str,
        customer_email: str,
        products: list = None,
        expiry_days: int = None,
    ) -> str:
        """Generate a new license key"""

        if products is None:
            products = ["all"]  # All products by default

        # Calculate expiry date
        if expiry_days:
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        else:
            expiry_date = None  # Perpetual license

        # Create license data
        license_data = {
            "license_id": str(uuid.uuid4()),
            "license_type": license_type,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "products": products,
            "issued_date": datetime.now().isoformat(),
            "expiry_date": expiry_date,
            "machine_id": None,  # Will be set on activation
            "activated": False,
            "activation_date": None,
        }

        # Encrypt and encode
        json_data = json.dumps(license_data)
        encrypted = self.cipher.encrypt(json_data.encode())
        license_key = base64.urlsafe_b64encode(encrypted).decode()

        return license_key

    def validate_license_key(self, license_key: str) -> Tuple[bool, Dict, str]:
        """
        Validate a license key
        Returns: (is_valid, license_data, error_message)
        """
        try:
            # Decode and decrypt
            encrypted = base64.urlsafe_b64decode(license_key.encode())
            decrypted = self.cipher.decrypt(encrypted)
            license_data = json.loads(decrypted.decode())

            # Check expiry
            if license_data.get("expiry_date"):
                expiry = datetime.fromisoformat(license_data["expiry_date"])
                if datetime.now() > expiry:
                    return False, license_data, "License has expired"

            # Check if activated
            if not license_data.get("activated"):
                return True, license_data, "License valid but not activated"

            # Check machine ID
            current_machine_id = self._get_machine_id()
            if license_data.get("machine_id") != current_machine_id:
                return False, license_data, "License not valid for this machine"

            return True, license_data, "License valid"

        except Exception as e:
            return False, {}, f"Invalid license key: {str(e)}"

    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """Activate a license key on this machine"""
        is_valid, license_data, message = self.validate_license_key(license_key)

        if not is_valid and "not activated" not in message:
            return False, message

        # Set machine ID and activation
        license_data["machine_id"] = self._get_machine_id()
        license_data["activated"] = True
        license_data["activation_date"] = datetime.now().isoformat()

        # Re-encrypt and save
        json_data = json.dumps(license_data)
        encrypted = self.cipher.encrypt(json_data.encode())
        new_license_key = base64.urlsafe_b64encode(encrypted).decode()

        # Save to file
        self._save_license(new_license_key)

        return True, "License activated successfully"

    def create_trial_license(self) -> Tuple[bool, str, str]:
        """Create a trial license for this machine"""
        # Check if trial already exists
        if os.path.exists(self.license_file):
            is_valid, license_data, message = self.load_license()
            if is_valid and license_data.get("license_type") == self.LICENSE_TRIAL:
                return False, "", "Trial license already exists"

        # Generate trial license
        license_key = self.generate_license_key(
            license_type=self.LICENSE_TRIAL,
            customer_name="Trial User",
            customer_email="trial@itechsmart.dev",
            products=["all"],
            expiry_days=self.TRIAL_DAYS,
        )

        # Activate immediately
        success, message = self.activate_license(license_key)

        if success:
            return (
                True,
                license_key,
                f"Trial license created (valid for {self.TRIAL_DAYS} days)",
            )
        else:
            return False, "", message

    def load_license(self) -> Tuple[bool, Dict, str]:
        """Load and validate license from file"""
        if not os.path.exists(self.license_file):
            return False, {}, "No license file found"

        try:
            with open(self.license_file, "r") as f:
                license_key = f.read().strip()

            return self.validate_license_key(license_key)

        except Exception as e:
            return False, {}, f"Error loading license: {str(e)}"

    def _save_license(self, license_key: str):
        """Save license key to file"""
        with open(self.license_file, "w") as f:
            f.write(license_key)

    def _get_machine_id(self) -> str:
        """Get unique machine identifier"""
        # Use MAC address and hostname
        import platform
        import socket

        hostname = socket.gethostname()
        mac = ":".join(
            [
                "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                for elements in range(0, 2 * 6, 2)
            ][::-1]
        )

        machine_string = f"{hostname}:{mac}:{platform.system()}"
        return hashlib.sha256(machine_string.encode()).hexdigest()

    def get_license_info(self) -> Dict:
        """Get current license information"""
        is_valid, license_data, message = self.load_license()

        if not is_valid:
            return {
                "status": "invalid",
                "message": message,
                "license_type": None,
                "days_remaining": 0,
            }

        # Calculate days remaining
        days_remaining = None
        if license_data.get("expiry_date"):
            expiry = datetime.fromisoformat(license_data["expiry_date"])
            days_remaining = (expiry - datetime.now()).days

        return {
            "status": "valid",
            "message": message,
            "license_type": license_data.get("license_type"),
            "customer_name": license_data.get("customer_name"),
            "customer_email": license_data.get("customer_email"),
            "products": license_data.get("products"),
            "issued_date": license_data.get("issued_date"),
            "expiry_date": license_data.get("expiry_date"),
            "days_remaining": days_remaining,
            "is_trial": license_data.get("license_type") == self.LICENSE_TRIAL,
        }

    def check_product_access(self, product_name: str) -> bool:
        """Check if license allows access to specific product"""
        is_valid, license_data, _ = self.load_license()

        if not is_valid:
            return False

        products = license_data.get("products", [])
        return "all" in products or product_name in products

    def get_feature_restrictions(self) -> Dict:
        """Get feature restrictions based on license type"""
        info = self.get_license_info()
        license_type = info.get("license_type")

        restrictions = {
            self.LICENSE_TRIAL: {
                "max_users": 5,
                "max_projects": 10,
                "api_calls_per_day": 1000,
                "storage_gb": 10,
                "support_level": "community",
                "advanced_features": False,
            },
            self.LICENSE_BASIC: {
                "max_users": 25,
                "max_projects": 50,
                "api_calls_per_day": 10000,
                "storage_gb": 100,
                "support_level": "email",
                "advanced_features": False,
            },
            self.LICENSE_PROFESSIONAL: {
                "max_users": 100,
                "max_projects": 200,
                "api_calls_per_day": 50000,
                "storage_gb": 500,
                "support_level": "priority",
                "advanced_features": True,
            },
            self.LICENSE_ENTERPRISE: {
                "max_users": 1000,
                "max_projects": -1,  # Unlimited
                "api_calls_per_day": -1,  # Unlimited
                "storage_gb": -1,  # Unlimited
                "support_level": "24/7",
                "advanced_features": True,
            },
            self.LICENSE_UNLIMITED: {
                "max_users": -1,
                "max_projects": -1,
                "api_calls_per_day": -1,
                "storage_gb": -1,
                "support_level": "dedicated",
                "advanced_features": True,
            },
        }

        return restrictions.get(license_type, restrictions[self.LICENSE_TRIAL])


# CLI interface for license management
if __name__ == "__main__":
    import sys

    manager = LicenseManager()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python license_manager.py generate <type> <name> <email> [days]")
        print("  python license_manager.py activate <license_key>")
        print("  python license_manager.py validate")
        print("  python license_manager.py trial")
        print("  python license_manager.py info")
        sys.exit(1)

    command = sys.argv[1]

    if command == "generate":
        if len(sys.argv) < 5:
            print(
                "Usage: python license_manager.py generate <type> <name> <email> [days]"
            )
            sys.exit(1)

        license_type = sys.argv[2]
        name = sys.argv[3]
        email = sys.argv[4]
        days = int(sys.argv[5]) if len(sys.argv) > 5 else None

        key = manager.generate_license_key(license_type, name, email, expiry_days=days)
        print(f"Generated license key:\n{key}")

    elif command == "activate":
        if len(sys.argv) < 3:
            print("Usage: python license_manager.py activate <license_key>")
            sys.exit(1)

        license_key = sys.argv[2]
        success, message = manager.activate_license(license_key)
        print(message)

    elif command == "validate":
        is_valid, license_data, message = manager.load_license()
        print(f"Valid: {is_valid}")
        print(f"Message: {message}")
        if is_valid:
            print(f"License Data: {json.dumps(license_data, indent=2)}")

    elif command == "trial":
        success, key, message = manager.create_trial_license()
        print(message)
        if success:
            print(f"Trial License Key: {key}")

    elif command == "info":
        info = manager.get_license_info()
        print(json.dumps(info, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
