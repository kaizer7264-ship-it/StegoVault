"""
StegoVault Services: Steganography Orchestration Service
Coordinates the core LSB engine, payload serialization, file management, 
and AES encryption modules to provide a unified API for the frontend GUI.
"""

from pathlib import Path

from stegovault.core.lsb import LSBSteganography
from stegovault.core.payload import PayloadManager, PayloadType
from stegovault.core.file_manager import FileManager
from stegovault.crypto.aes import AESEncryption, EncryptionResult
from stegovault.utils.exceptions import AuthenticationError, SteganographyError, CryptoError


class StegoService:
    """
    High-level service class that orchestrates the data flow between 
    StegoVault's backend modules. Exposes clean, synchronous methods 
    for hiding and extracting data.
    """

    @classmethod
    def hide_text(
        cls,
        input_image: Path | str,
        text: str,
        output_image: Path | str,
        encrypt: bool = False,
        password: str = ""
    ) -> str:
        """
        Coordinates the hiding of a text payload inside a carrier image.

        Args:
            input_image (Path | str): The source PNG image.
            text (str): The secret message to hide.
            output_image (Path | str): The destination path for the modified image.
            encrypt (bool): Whether to apply AES-256 encryption.
            password (str): The encryption password (required if encrypt=True).

        Returns:
            str: A meaningful success message.

        Raises:
            ValueError: If encryption is requested but no password is provided.
        """
        # 1. Serialize the payload using PayloadManager
        raw_payload = PayloadManager.create_text_payload(text)

        # 2. Optionally encrypt the entire serialized payload
        if encrypt:
            if not password:
                raise ValueError("A password is required to encrypt the payload.")
            
            enc_result = AESEncryption.encrypt(raw_payload, password)
            # Prepend the salt and nonce to the ciphertext for storage
            final_bytes = enc_result.salt + enc_result.nonce + enc_result.ciphertext
        else:
            final_bytes = raw_payload

        # 3. Embed the raw bytes into the image using the generic LSB engine
        LSBSteganography.encode_bytes(input_image, final_bytes, output_image)

        return f"Successfully embedded secret text into '{Path(output_image).name}'."

    @classmethod
    def hide_file(
        cls,
        input_image: Path | str,
        file_path: Path | str,
        output_image: Path | str,
        encrypt: bool = False,
        password: str = ""
    ) -> str:
        """
        Coordinates the hiding of a file inside a carrier image.

        Args:
            input_image (Path | str): The source PNG image.
            file_path (Path | str): The path of the file to be hidden.
            output_image (Path | str): The destination path for the modified image.
            encrypt (bool): Whether to apply AES-256 encryption.
            password (str): The encryption password (required if encrypt=True).

        Returns:
            str: A meaningful success message.

        Raises:
            ValueError: If encryption is requested but no password is provided.
        """
        # 1. Validate the file existence and accessibility via FileManager
        FileManager.validate_file(file_path)

        # 2. Serialize the file payload
        raw_payload = PayloadManager.create_file_payload(file_path)

        # 3. Optionally encrypt
        if encrypt:
            if not password:
                raise ValueError("A password is required to encrypt the payload.")
            
            enc_result = AESEncryption.encrypt(raw_payload, password)
            final_bytes = enc_result.salt + enc_result.nonce + enc_result.ciphertext
        else:
            final_bytes = raw_payload

        # 4. Embed into the image
        LSBSteganography.encode_bytes(input_image, final_bytes, output_image)

        return f"Successfully embedded file '{Path(file_path).name}' into '{Path(output_image).name}'."

    @classmethod
    def extract(
        cls,
        image_path: Path | str,
        output_directory: Path | str | None = None,
        password: str = ""
    ) -> str:
        """
        Extracts hidden data from a carrier image. Automatically detects 
        encryption, decrypts if necessary, parses the payload, and routes 
        the output to a string or a physical file.

        Args:
            image_path (Path | str): The path to the stego PNG image.
            output_directory (Path | str | None): The directory to save extracted files.
                                                  Defaults to current working directory.
            password (str): The decryption password (if applicable).

        Returns:
            str: The extracted text (if text payload) or a success message (if file payload).

        Raises:
            AuthenticationError: If the payload is encrypted but no/wrong password is provided.
            SteganographyError: If extraction fails or data is corrupted.
        """
        # 1. Extract raw bytes from the LSB engine
        raw_bytes = LSBSteganography.decode_bytes(image_path)

        # 2. Detect Encryption (Plaintext payloads strictly start with the MAGIC header)
        if not raw_bytes.startswith(PayloadManager.MAGIC):
            if not password:
                raise AuthenticationError(
                    "This image contains an encrypted payload, but no password was provided."
                )

            # Reconstruct the EncryptionResult (Salt: 16b, Nonce: 12b, Cipher: Remainder)
            if len(raw_bytes) < 28:
                raise SteganographyError(
                    "Extracted data is too short to be a valid encrypted StegoVault payload."
                )

            salt = raw_bytes[:16]
            nonce = raw_bytes[16:28]
            ciphertext = raw_bytes[28:]
            
            enc_result = EncryptionResult(salt=salt, nonce=nonce, ciphertext=ciphertext)
            
            # 3. Decrypt the payload
            try:
                raw_bytes = AESEncryption.decrypt(enc_result, password)
            except CryptoError as e:
                # Wrap underlying crypto errors for the frontend to handle cleanly
                raise AuthenticationError(f"Failed to unlock data: {e}") from e

        # 4. Parse the unencrypted (or decrypted) StegoVault payload
        metadata, payload_data = PayloadManager.parse_payload(raw_bytes)

        # 5. Route the payload to its destination based on its type
        if metadata.payload_type == PayloadType.TEXT:
            return payload_data.decode('utf-8')
            
        elif metadata.payload_type == PayloadType.FILE:
            out_dir = Path(output_directory) if output_directory else Path.cwd()
            out_file = out_dir / metadata.filename
            
            # Write out using FileManager (overwrite=True to prevent silent frontend failures)
            FileManager.write_file(out_file, payload_data, overwrite=True)
            
            return f"File extracted successfully: {out_file.resolve()}"
            
        else:
            raise SteganographyError(f"Unknown payload type ID: {metadata.payload_type}")