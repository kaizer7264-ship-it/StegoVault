"""
StegoVault Core: File Management Engine
Provides robust, generic file handling utilities for reading, writing,
validating, and extracting metadata from files. Designed to safely handle
large files and full Unicode file paths.
"""

import hashlib
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class FileInfo:
    """
    Immutable data transfer object containing comprehensive metadata
    about a specific file on the filesystem.
    """
    filename: str
    extension: str
    mime_type: str
    size_bytes: int
    sha256: str


class FileManager:
    """
    Stateless utility class for performing safe, memory-efficient file operations.
    """

    # 64 KB chunk size for memory-efficient file reading (e.g., during hashing)
    CHUNK_SIZE: ClassVar[int] = 65536

    @classmethod
    def validate_file(cls, file_path: Path | str) -> None:
        """
        Validates that a given path exists, is a regular file, and is accessible.

        Args:
            file_path (Path | str): The path to the file to validate.

        Raises:
            FileNotFoundError: If the file does not exist.
            IsADirectoryError: If the path points to a directory.
            PermissionError: If the file lacks read permissions.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: '{path}'")
        
        if not path.is_file():
            raise IsADirectoryError(f"Target is a directory, not a file: '{path}'")
            
        try:
            # Quick open/close to verify read permissions
            with open(path, "rb"):
                pass
        except PermissionError as e:
            raise PermissionError(f"Permission denied when accessing: '{path}'") from e

    @classmethod
    def calculate_sha256(cls, file_path: Path | str) -> str:
        """
        Calculates the SHA-256 hash of a file using memory-efficient chunking.
        This prevents massive memory spikes when processing multi-gigabyte files.

        Args:
            file_path (Path | str): Path to the target file.

        Returns:
            str: The lowercase hexadecimal SHA-256 hash string.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        cls.validate_file(path)

        sha256_hash = hashlib.sha256()

        with open(path, "rb") as f:
            # Read the file in chunks until the end is reached
            for byte_block in iter(lambda: f.read(cls.CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    @classmethod
    def get_file_info(cls, file_path: Path | str) -> FileInfo:
        """
        Gathers comprehensive metadata and cryptographic identity of a file.

        Args:
            file_path (Path | str): Path to the target file.

        Returns:
            FileInfo: A frozen dataclass containing the file's metadata.

        Raises:
            FileNotFoundError: If the target file does not exist.
        """
        path = Path(file_path)
        cls.validate_file(path)

        filename = path.name
        extension = path.suffix.lower()
        
        # Guess MIME type, fallback to generic binary stream if unknown
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        size_bytes = path.stat().st_size
        sha256_hash = cls.calculate_sha256(path)

        return FileInfo(
            filename=filename,
            extension=extension,
            mime_type=mime_type,
            size_bytes=size_bytes,
            sha256=sha256_hash
        )

    @classmethod
    def read_file(cls, file_path: Path | str) -> bytes:
        """
        Reads the entire contents of a file into a byte string.
        Note: Use carefully with massive files, as it loads entirely into RAM.

        Args:
            file_path (Path | str): Path to the target file.

        Returns:
            bytes: The complete raw binary data of the file.

        Raises:
            FileNotFoundError: If the target file does not exist.
            IsADirectoryError: If the target is a directory.
        """
        path = Path(file_path)
        cls.validate_file(path)
        
        return path.read_bytes()

    @classmethod
    def write_file(cls, output_path: Path | str, data: bytes, overwrite: bool = False) -> None:
        """
        Writes a byte sequence to a file, automatically creating any missing
        parent directories in the path.

        Args:
            output_path (Path | str): The destination file path.
            data (bytes): The raw binary data to write.
            overwrite (bool): If False, raises an error if the file already exists.

        Raises:
            FileExistsError: If the file exists and overwrite is False.
            PermissionError: If writing to the directory is forbidden.
            OSError: For general I/O failures.
        """
        path = Path(output_path)
        
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"Destination file already exists: '{path}'. "
                "Enable overwriting in settings to replace it."
            )
            
        # Ensure the parent directory structure exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_bytes(data)


# =====================================================================
# Example Usage Block
# =====================================================================
if __name__ == "__main__":
    import tempfile
    import os

    print("--- StegoVault File Manager Test ---")

    test_filename = "tést_secrèt_資料.txt"
    test_content = b"StegoVault secure file management test content."
    new_content = b"This is the overwritten data!"
    
    temp_dir = Path(tempfile.mkdtemp())
    temp_file = temp_dir / test_filename

    try:
        # 1. Test Writing (Initial)
        print(f"\n[1] Writing file to: {temp_file}")
        FileManager.write_file(temp_file, test_content)
        print("    ✅ Initial write successful.")

        # 2. Test Overwrite Protection (Should Fail)
        print("\n[2] Testing Overwrite Protection...")
        try:
            FileManager.write_file(temp_file, new_content, overwrite=False)
            print("    ❌ FAILED: It overwrote the file when it shouldn't have!")
        except FileExistsError:
            print("    ✅ SUCCESS: Blocked accidental overwrite.")

        # 3. Test Forced Overwrite (Should Succeed)
        print("\n[3] Testing Forced Overwrite...")
        FileManager.write_file(temp_file, new_content, overwrite=True)
        
        read_content = FileManager.read_file(temp_file)
        assert read_content == new_content
        print("    ✅ SUCCESS: Safely overwrote the file when instructed.")

        # 4. Test Metadata & Hashing
        print("\n[4] Extracting File Info...")
        info = FileManager.get_file_info(temp_file)
        
        print(f"    Filename  : {info.filename}")
        print(f"    Extension : {info.extension}")
        print(f"    Size      : {info.size_bytes} bytes")
        print(f"    SHA-256   : {info.sha256}")
        print("    ✅ File metadata verified.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
    finally:
        if temp_file.exists():
            os.remove(temp_file)
        if temp_dir.exists():
            os.rmdir(temp_dir)