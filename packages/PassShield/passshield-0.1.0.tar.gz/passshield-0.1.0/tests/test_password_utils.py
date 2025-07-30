import os
import tempfile
import pytest
from cryptography.fernet import Fernet
import base64


# Password utility functions
def generate_key():
    """Generate a new encryption key"""
    return Fernet.generate_key()


def save_key(key, key_file="secret.key"):
    """Save encryption key to file"""
    with open(key_file, "wb") as f:
        f.write(key)


def load_key(key_file="secret.key"):
    """Load encryption key from file"""
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Key file {key_file} not found")
    with open(key_file, "rb") as f:
        return f.read()


def encrypt_password(password, key=None):
    """Encrypt a password"""
    if key is None:
        key = load_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_password(encrypted_password, key=None):
    """Decrypt a password"""
    if key is None:
        key = load_key()
    fernet = Fernet(key)
    encrypted = base64.urlsafe_b64decode(encrypted_password.encode())
    return fernet.decrypt(encrypted).decode()


# Test cases
class TestPasswordUtils:
    def setup_method(self):
        self.test_key = generate_key()
        self.test_password = "my_secure_password_123!"
        self.temp_key_file = tempfile.NamedTemporaryFile(delete=False).name

    def teardown_method(self):
        if os.path.exists(self.temp_key_file):
            os.unlink(self.temp_key_file)

    def test_generate_key(self):
        key = generate_key()
        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_save_and_load_key(self):
        save_key(self.test_key, self.temp_key_file)
        loaded_key = load_key(self.temp_key_file)
        assert loaded_key == self.test_key

    def test_load_key_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_key("non_existent_file.key")

    def test_encrypt_decrypt(self):
        encrypted = encrypt_password(self.test_password, self.test_key)
        assert isinstance(encrypted, str)
        assert encrypted != self.test_password

        decrypted = decrypt_password(encrypted, self.test_key)
        assert decrypted == self.test_password

    def test_encrypt_decrypt_without_key_param(self):
        # Save the test key to the default location
        save_key(self.test_key, "secret.key")

        try:
            # Test with implicit key loading
            encrypted = encrypt_password(self.test_password)
            decrypted = decrypt_password(encrypted)
            assert decrypted == self.test_password
        finally:
            # Clean up the default key file
            if os.path.exists("secret.key"):
                os.unlink("secret.key")