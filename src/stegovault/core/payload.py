"""
StegoVault Core: Payload Management Engine
Handles the serialization and deserialization of payloads into a custom,
highly efficient binary format suitable for steganographic embedding.
"""

import enum
import struct
import zlib
import mimetypes
from dataclasses import dataclass
from pathlib import Path


class PayloadError(Exception):
    """Base exception for all payload serialization/deserialization errors."""
    pass


class PayloadFormatError(PayloadError):
    """Raised when the payload binary structure is malformed or invalid."""
    pass


class ChecksumError(PayloadError):
    """Raised when the payload's CRC32 checksum verification fails."""
    pass


class PayloadType(enum.IntEnum):
    """Defines the type of data stored within the payload."""
    TEXT = 0
    FILE = 1


@dataclass(frozen=True)
class PayloadMetadata:
    """
    Immutable data transfer object representing the parsed header 
    information of a StegoVault payload.
    """
    version: int
    payload_type: PayloadType
    encrypted: bool
    compressed: bool
    filename: str
    mime_type: str
    payload_size: int
    checksum: int


class PayloadManager:
    """
    Core utility for packing text and file data into StegoVault's custom binary format,
    and unpacking binary data back into actionable metadata and raw bytes.
    """

    MAGIC: bytes = b"SVLT"
    CURRENT_VERSION: int = 1

    @classmethod
    def calculate_checksum(cls, data: bytes) -> int:
        """
        Calculates a guaranteed unsigned 32-bit CRC checksum for the provided data.
        
        Args:
            data (bytes): The raw bytes to hash.
            
        Returns:
            int: The unsigned 32-bit CRC checksum.
        """
        return zlib.crc32(data) & 0xFFFFFFFF

    @classmethod
    def verify_checksum(cls, data: bytes, checksum: int) -> bool:
        """
        Verifies the CRC32 checksum of the provided binary chunk.

        Args:
            data (bytes): The original binary data prior to checksum appending.
            checksum (int): The expected CRC32 integer.

        Returns:
            bool: True if the calculated checksum matches the expected checksum.
        """
        return cls.calculate_checksum(data) == checksum

    @classmethod
    def create_text_payload(cls, text: str) -> bytes:
        """
        Creates a serialized payload for a UTF-8 text string.

        Args:
            text (str): The text message to embed.

        Returns:
            bytes: The complete, packed binary payload.

        Raises:
            ValueError: If the input text is empty.
        """
        if not text:
            raise ValueError("Text payload cannot be empty.")

        text_bytes = text.encode('utf-8')

        return cls._build_payload(
            p_type=PayloadType.TEXT,
            filename="",
            mime_type="text/plain",
            data=text_bytes,
            encrypted=False,
            compressed=False
        )

    @classmethod
    def create_file_payload(cls, file_path: Path | str) -> bytes:
        """
        Creates a serialized payload for a file, automatically detecting
        its MIME type and packaging its raw bytes.

        Args:
            file_path (Path | str): Path to the file to embed.

        Returns:
            bytes: The complete, packed binary payload.

        Raises:
            FileNotFoundError: If the target file does not exist.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        mime_type, _ = mimetypes.guess_type(path.name)
        if not mime_type:
            mime_type = "application/octet-stream"

        file_bytes = path.read_bytes()

        return cls._build_payload(
            p_type=PayloadType.FILE,
            filename=path.name,
            mime_type=mime_type,
            data=file_bytes,
            encrypted=False,
            compressed=False
        )

    @classmethod
    def _build_payload(
        cls, 
        p_type: PayloadType, 
        filename: str, 
        mime_type: str, 
        data: bytes,
        encrypted: bool,
        compressed: bool
    ) -> bytes:
        """Internal helper to construct the binary payload structure."""
        
        fn_bytes = filename.encode('utf-8')
        mime_bytes = mime_type.encode('utf-8')

        if len(fn_bytes) > 65535:
            raise ValueError("Filename is too long (exceeds 65KB).")
        if len(mime_bytes) > 65535:
            raise ValueError("MIME type is too long (exceeds 65KB).")

        flags = 0
        if encrypted:
            flags |= 1  # bit0
        if compressed:
            flags |= 2  # bit1

        buffer = bytearray()
        
        # 1. Magic Header (4 bytes), Version (1 byte), Type (1 byte), Flags (1 byte)
        buffer.extend(struct.pack(">4s B B B", cls.MAGIC, cls.CURRENT_VERSION, p_type.value, flags))
        
        # 2. Filename Length (2 bytes) + Filename String
        buffer.extend(struct.pack(">H", len(fn_bytes)))
        buffer.extend(fn_bytes)
        
        # 3. MIME Length (2 bytes) + MIME Type String
        buffer.extend(struct.pack(">H", len(mime_bytes)))
        buffer.extend(mime_bytes)
        
        # 4. Payload Length (8 bytes) + Raw Payload Data
        buffer.extend(struct.pack(">Q", len(data)))
        buffer.extend(data)
        
        # 5. Checksum (4 bytes) computed over everything built so far
        crc = cls.calculate_checksum(buffer)
        buffer.extend(struct.pack(">I", crc))
        
        return bytes(buffer)

    @classmethod
    def parse_payload(cls, data: bytes) -> tuple[PayloadMetadata, bytes]:
        """
        Parses a serialized StegoVault binary payload.

        Args:
            data (bytes): The binary data extracted from the image.

        Returns:
            tuple[PayloadMetadata, bytes]: A tuple containing the parsed metadata dataclass 
                                           and the raw payload bytes.

        Raises:
            PayloadFormatError: If the binary structure is malformed or not a StegoVault payload.
            ChecksumError: If the CRC32 validation fails.
        """
        offset = 0

        def read(size: int) -> bytes:
            """Helper to sequentially read bytes and advance the offset pointer."""
            nonlocal offset
            if offset + size > len(data):
                raise PayloadFormatError("Unexpected end of data. Payload is truncated.")
            chunk = data[offset : offset + size]
            offset += size
            return chunk

        try:
            # 1. Extract and validate Fixed Prefix (7 bytes)
            prefix = read(7)
            magic, version, p_type_val, flags = struct.unpack(">4s B B B", prefix)

            if magic != cls.MAGIC:
                raise PayloadFormatError("Invalid Magic Header. Not a StegoVault payload.")
            if version != cls.CURRENT_VERSION:
                raise PayloadFormatError(f"Unsupported payload version: {version}")

            try:
                p_type = PayloadType(p_type_val)
            except ValueError:
                raise PayloadFormatError(f"Unknown payload type ID: {p_type_val}")

            encrypted = bool(flags & 1)
            compressed = bool(flags & 2)

            # 2. Extract Filename
            fn_len = struct.unpack(">H", read(2))[0]
            filename = read(fn_len).decode('utf-8')

            # 3. Extract MIME Type
            mime_len = struct.unpack(">H", read(2))[0]
            mime_type = read(mime_len).decode('utf-8')

            # 4. Extract Payload Data
            payload_len = struct.unpack(">Q", read(8))[0]
            payload_data = read(payload_len)

            # 5. Extract Checksum
            checksum = struct.unpack(">I", read(4))[0]

        except struct.error as e:
            raise PayloadFormatError(f"Failed to unpack binary structure: {e}")
        except UnicodeDecodeError as e:
            raise PayloadFormatError(f"Failed to decode string fields (Invalid UTF-8): {e}")

        # 6. Verify Checksum
        buffer_to_check = data[: offset - 4]
        if not cls.verify_checksum(buffer_to_check, checksum):
            raise ChecksumError("Payload CRC32 verification failed. Data may be corrupted.")

        metadata = PayloadMetadata(
            version=version,
            payload_type=p_type,
            encrypted=encrypted,
            compressed=compressed,
            filename=filename,
            mime_type=mime_type,
            payload_size=payload_len,
            checksum=checksum
        )

        return metadata, payload_data


# =====================================================================
# Example Usage Block
# =====================================================================
if __name__ == "__main__":
    import tempfile
    import os

    print("--- StegoVault Payload Manager Test ---")

    print("\n[1] Testing Text Payload Serialization")
    secret_text = "This is a covert message! 🚀"
    
    text_binary = PayloadManager.create_text_payload(secret_text)
    print(f"    Serialized text into {len(text_binary)} bytes.")
    
    text_meta, text_data = PayloadManager.parse_payload(text_binary)
    print(f"    Metadata : {text_meta}")
    print(f"    Decoded  : '{text_data.decode('utf-8')}'")
    assert text_data.decode('utf-8') == secret_text

    print("\n[2] Testing File Payload Serialization")
    
    test_content = b"Fake PDF file header %PDF-1.4 ... binary data ... EOF"
    with tempfile.NamedTemporaryFile(suffix=" secret_資料.pdf", delete=False) as f:
        f.write(test_content)
        temp_file_path = Path(f.name)

    try:
        file_binary = PayloadManager.create_file_payload(temp_file_path)
        print(f"    Serialized file into {len(file_binary)} bytes.")
        
        file_meta, file_data = PayloadManager.parse_payload(file_binary)
        print(f"    Metadata : {file_meta}")
        print(f"    MIME Type: {file_meta.mime_type}")
        print(f"    Matched? : {file_data == test_content}")
        assert file_data == test_content

        print("\n[3] Testing Checksum Validation (Corruption)")
        corrupted_binary = bytearray(file_binary)
        # Flip bits in the data stream (adjusting offset for new 7-byte header)
        corrupted_binary[20] ^= 0xFF  
        
        try:
            PayloadManager.parse_payload(bytes(corrupted_binary))
            print("    ❌ FAILED: Did not catch corruption!")
        except ChecksumError as e:
            print(f"    ✅ SUCCESS: Caught corruption - {e}")

    finally:
        if temp_file_path.exists():
            os.remove(temp_file_path)