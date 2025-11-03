"""
AES-256 encryption utilities for sensitive data protection.
Used for data at rest encryption in the database.
"""
from cryptography.fernet import Fernet
from flask import current_app
from typing import Optional


def encrypt_data(data: str) -> Optional[str]:
    """
    Encrypt data using AES-256 (via Fernet).

    Args:
        data: Plain text to encrypt

    Returns:
        Encrypted string or None if encryption fails
    """
    if not data:
        return None

    try:
        key = current_app.config['DB_ENCRYPTION_KEY']
        if not key:
            current_app.logger.warning("DB_ENCRYPTION_KEY not configured, data not encrypted")
            return data

        f = Fernet(key.encode())
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        current_app.logger.error(f"Encryption error: {str(e)}")
        return None


def decrypt_data(encrypted_data: str) -> Optional[str]:
    """
    Decrypt data using AES-256 (via Fernet).

    Args:
        encrypted_data: Encrypted string

    Returns:
        Decrypted string or None if decryption fails
    """
    if not encrypted_data:
        return None

    try:
        key = current_app.config['DB_ENCRYPTION_KEY']
        if not key:
            current_app.logger.warning("DB_ENCRYPTION_KEY not configured, returning data as-is")
            return encrypted_data

        f = Fernet(key.encode())
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        current_app.logger.error(f"Decryption error: {str(e)}")
        return None


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        Base64-encoded encryption key
    """
    return Fernet.generate_key().decode()
