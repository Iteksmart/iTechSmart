"""
Security utilities: encryption, hashing, JWT, password generation.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import pyotp
from .config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# JWT tokens
def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# Vault encryption (zero-knowledge)
class VaultEncryption:
    """Zero-knowledge vault encryption."""

    @staticmethod
    def derive_key(master_password: str, salt: bytes) -> bytes:
        """Derive encryption key from master password."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

    @staticmethod
    def encrypt_vault(data: str, master_password: str, salt: bytes) -> str:
        """Encrypt vault data with master password."""
        key = VaultEncryption.derive_key(master_password, salt)
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    @staticmethod
    def decrypt_vault(encrypted_data: str, master_password: str, salt: bytes) -> str:
        """Decrypt vault data with master password."""
        key = VaultEncryption.derive_key(master_password, salt)
        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()

    @staticmethod
    def generate_salt() -> bytes:
        """Generate random salt."""
        return secrets.token_bytes(32)


# Password encryption (AES-256)
class PasswordEncryption:
    """AES-256 password encryption."""

    def __init__(self):
        self.key = settings.VAULT_ENCRYPTION_KEY.encode()[:32]
        self.fernet = Fernet(base64.urlsafe_b64encode(self.key))

    def encrypt(self, password: str) -> str:
        """Encrypt password."""
        encrypted = self.fernet.encrypt(password.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_password: str) -> str:
        """Decrypt password."""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()


password_encryption = PasswordEncryption()


# Password generation
def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = True,
) -> str:
    """Generate secure random password."""
    chars = ""

    if use_lowercase:
        chars += string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        # Remove ambiguous characters
        ambiguous = "il1Lo0O"
        chars = "".join(c for c in chars if c not in ambiguous)

    if not chars:
        raise ValueError("At least one character type must be selected")

    # Ensure at least one character from each selected type
    password = []
    if use_lowercase:
        password.append(secrets.choice(string.ascii_lowercase))
    if use_uppercase:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

    # Fill remaining length
    for _ in range(length - len(password)):
        password.append(secrets.choice(chars))

    # Shuffle
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


# Password strength analysis
def analyze_password_strength(password: str) -> Dict[str, Any]:
    """Analyze password strength."""
    score = 0
    feedback = []

    # Length check
    length = len(password)
    if length < 8:
        feedback.append("Password is too short (minimum 8 characters)")
    elif length < 12:
        score += 1
        feedback.append("Consider using a longer password (12+ characters)")
    elif length < 16:
        score += 2
    else:
        score += 3

    # Character variety
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    variety = sum([has_lower, has_upper, has_digit, has_symbol])
    score += variety

    if not has_lower:
        feedback.append("Add lowercase letters")
    if not has_upper:
        feedback.append("Add uppercase letters")
    if not has_digit:
        feedback.append("Add numbers")
    if not has_symbol:
        feedback.append("Add symbols")

    # Common patterns
    common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
    if password.lower() in common_passwords:
        score = 0
        feedback.append("This is a commonly used password")

    # Sequential characters
    if any(
        password[i : i + 3].isdigit() and int(password[i : i + 3]) in range(100, 1000)
        for i in range(len(password) - 2)
    ):
        score -= 1
        feedback.append("Avoid sequential numbers")

    # Determine strength level
    if score <= 2:
        strength = "weak"
        color = "red"
    elif score <= 4:
        strength = "fair"
        color = "orange"
    elif score <= 6:
        strength = "good"
        color = "yellow"
    else:
        strength = "strong"
        color = "green"

    return {
        "score": max(0, min(score, 10)),
        "strength": strength,
        "color": color,
        "feedback": feedback if feedback else ["Password looks good!"],
    }


# 2FA
def generate_totp_secret() -> str:
    """Generate TOTP secret for 2FA."""
    return pyotp.random_base32()


def verify_totp(secret: str, token: str) -> bool:
    """Verify TOTP token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def get_totp_uri(secret: str, email: str) -> str:
    """Get TOTP URI for QR code."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email, issuer_name="iTechSmart PassPort"
    )


# API key generation
def generate_api_key() -> str:
    """Generate secure API key."""
    return f"psp_{secrets.token_urlsafe(32)}"


# Hash API key for storage
def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()
