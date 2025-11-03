"""
Generate a Fernet encryption key for DB_ENCRYPTION_KEY.
Run this to generate a secure key for your .env file.
"""
from cryptography.fernet import Fernet


def generate_key():
    """Generate a new Fernet encryption key."""
    key = Fernet.generate_key()
    return key.decode()


if __name__ == '__main__':
    key = generate_key()
    print("Generated encryption key:")
    print(key)
    print("\nAdd this to your .env file:")
    print(f"DB_ENCRYPTION_KEY={key}")
