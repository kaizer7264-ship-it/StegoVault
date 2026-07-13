"""
StegoVault Crypto: AES-256-GCM Engine
Provides military-grade authenticated encryption and decryption.
Utilizes PBKDF2-HMAC-SHA256 for secure key derivation from user passwords.
"""

import os
from dataclasses import dataclass
from typing import ClassVar

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Import custom exceptions
from stegovault.utils.exceptions import CryptoError, AuthenticationError


@dataclass(frozen=True)
class EncryptionResult:
    """
    Immutable data transfer object containing all necessary cryptographic 
    components required to safely store and eventually decrypt the payload.
    """
    salt: bytes
    nonce: bytes
    ciphertext: bytes


class AESEncryption:
    """
    Stateless utility class for performing AES-256-GCM authenticated encryption.
    Automatically handles secure random generation for salts and nonces,
    and applies PBKDF2 key stretching to defend against brute-force attacks.
    """

    # Cryptographic Constants
    PBKDF2_ITERATIONS: ClassVar[int] = 200_000
    KEY_SIZE: ClassVar[int] = 32    # 256 bits for AES-256
    SALT_SIZE: ClassVar[int] = 16   # 128 bits
    NONCE_SIZE: ClassVar[int] = 12  # 96 bits (Standard for GCM)

    @classmethod
    def _derive_key(cls, password: str, salt: bytes) -> bytes:
        """
        Derives a 256-bit cryptographic key from a user-provided password
        using PBKDF2-HMAC-SHA256.

        Args:
            password (str): The plaintext password.
            salt (bytes): The 16-byte random salt.

        Returns:
            bytes: The derived 32-byte (256-bit) AES key.

        Raises:
            CryptoError: If key derivation fails.
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=cls.KEY_SIZE,
                salt=salt,
                iterations=cls.PBKDF2_ITERATIONS,
            )
            return kdf.derive(password.encode('utf-8'))
        except Exception as e:
            raise CryptoError(f"Failed to derive cryptographic key: {e}") from e

    @classmethod
    def encrypt(
        cls, 
        data: bytes, 
        password: str, 
        aad: bytes | None = None
    ) -> EncryptionResult:
        """
        Encrypts arbitrary byte data using AES-256-GCM.
        Generates a secure random salt and nonce for each operation.

        Args:
            data (bytes): The raw plaintext binary data to encrypt.
            password (str): The password used to secure the data.
            aad (bytes | None): Optional Associated Authenticated Data (e.g., headers) 
                                to bind to the ciphertext to prevent tampering.

        Returns:
            EncryptionResult: A dataclass containing the salt, nonce, and ciphertext.

        Raises:
            ValueError: If the input data or password is empty.
            CryptoError: If the encryption process encounters an internal error.
        """
        if not data:
            raise ValueError("Data payload cannot be empty.")
        if not password:
            raise ValueError("Encryption password cannot be empty.")

        salt = os.urandom(cls.SALT_SIZE)
        nonce = os.urandom(cls.NONCE_SIZE)

        key = cls._derive_key(password, salt)

        try:
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, data, associated_data=aad)
            
            return EncryptionResult(
                salt=salt,
                nonce=nonce,
                ciphertext=ciphertext
            )
        except Exception as e:
            raise CryptoError(f"Encryption operation failed: {e}") from e

    @classmethod
    def decrypt(
        cls, 
        result: EncryptionResult, 
        password: str, 
        aad: bytes | None = None
    ) -> bytes:
        """
        Decrypts an EncryptionResult back into the original plaintext bytes.
        Verifies the GCM authentication tag to ensure data and AAD integrity.

        Args:
            result (EncryptionResult): The previously encrypted data and parameters.
            password (str): The password required to unlock the data.
            aad (bytes | None): The exact Associated Authenticated Data used during encryption.

        Returns:
            bytes: The original decrypted plaintext data.

        Raises:
            ValueError: If the password is empty.
            AuthenticationError: If the password is incorrect or data/AAD was tampered with.
            CryptoError: For any other cryptographic failures.
        """
        if not password:
            raise ValueError("Decryption password cannot be empty.")

        key = cls._derive_key(password, result.salt)

        try:
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(
                result.nonce, 
                result.ciphertext, 
                associated_data=aad
            )
            return plaintext
            
        except InvalidTag as e:
            raise AuthenticationError(
                "Decryption failed: Incorrect password or corrupted data/AAD payload."
            ) from e
        except Exception as e:
            raise CryptoError(f"Decryption operation failed: {e}") from e


# =====================================================================
# Example Usage Block
# =====================================================================
if __name__ == "__main__":
    print("--- StegoVault AES-256-GCM Engine Test ---")

    secret_data = b"Highly confidential payload data."
    user_password = "SuperSecretPassword123!"
    metadata_aad = b"VERSION=1;TYPE=TEXT"

    try:
        # 1. Encryption with AAD
        print("\n[1] Encrypting Data with Associated Data...")
        encrypted_result = AESEncryption.encrypt(secret_data, user_password, aad=metadata_aad)
        print("    ✅ Encryption successful.")

        # 2. Decryption (Success)
        print("\n[2] Decrypting Data (Correct Password & AAD)...")
        decrypted_data = AESEncryption.decrypt(encrypted_result, user_password, aad=metadata_aad)
        assert decrypted_data == secret_data
        print(f"    Recovered: {decrypted_data.decode('utf-8')}")

        # 3. Decryption Failure (Tampered AAD)
        print("\n[3] Testing Authentication Integrity (Tampered AAD)...")
        tampered_aad = b"VERSION=2;TYPE=TEXT"  # Attacker changed the version header
        try:
            AESEncryption.decrypt(encrypted_result, user_password, aad=tampered_aad)
            print("    ❌ FAILED: Accepted tampered AAD?!")
        except AuthenticationError:
            print("    ✅ SUCCESS: Blocked tampered AAD (Invalid GCM Tag).")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")