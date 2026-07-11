"""
StegoVault Core: Capacity Engine
Evaluates the steganographic capacity of carrier PNG images.
Calculates available space assuming a 1-bit LSB approach across RGB channels
(3 bits per pixel).
"""

from dataclasses import dataclass
from pathlib import Path
from PIL import Image

# Import the shared custom exception
from stegovault.utils.exceptions import FormatError


@dataclass(frozen=True)
class CapacityInfo:
    """
    Immutable data transfer object containing detailed capacity metrics
    for a carrier image.
    """
    width: int
    height: int
    pixels: int
    usable_bits: int
    usable_bytes: int
    usable_kb: float
    usable_mb: float

    @property
    def formatted(self) -> str:
        """
        Returns a human-readable string representation of the usable capacity.
        Dynamically scales between MB, KB, or Bytes.
        """
        if self.usable_mb >= 1.0:
            return f"{self.usable_mb:.2f} MB"
        if self.usable_kb >= 1.0:
            return f"{self.usable_kb:.2f} KB"
        return f"{self.usable_bytes:,} Bytes"


class ImageCapacity:
    """
    Utility class for evaluating the storage capacity of PNG images.
    Provides methods to calculate total capacity and verify if specific
    payloads will fit within a given carrier image.
    """

    @staticmethod
    def _validate_png(image_path: Path) -> None:
        """
        Validates that the provided file path is a true PNG image.
        Checks both the file extension and the actual file header via Pillow.

        Args:
            image_path (Path): The file path to validate.

        Raises:
            FileNotFoundError: If the file does not exist.
            FormatError: If the file extension or internal format is not PNG.
        """
        if not image_path.is_file():
            raise FileNotFoundError(f"File not found: {image_path}")

        if image_path.suffix.lower() != '.png':
            raise FormatError(
                f"Unsupported extension '{image_path.suffix}'. "
                "StegoVault strictly requires .png extensions for lossless encoding."
            )

        try:
            with Image.open(image_path) as img:
                if img.format != "PNG":
                    raise FormatError(
                        f"Spoofed file detected. Internal format is {img.format}, not PNG."
                    )
        except IOError as e:
            raise FormatError(f"Unable to read image data: {e}") from e

    @classmethod
    def calculate(cls, image_path: Path | str) -> CapacityInfo:
        """
        Calculates the maximum steganographic capacity of a PNG image.

        Args:
            image_path (Path | str): Path to the carrier PNG image.

        Returns:
            CapacityInfo: A dataclass containing absolute capacity metrics.

        Raises:
            FileNotFoundError: If the file does not exist.
            FormatError: If the input path is not a valid PNG.
        """
        path = Path(image_path)
        cls._validate_png(path)

        with Image.open(path) as img:
            width, height = img.size

        pixels = width * height
        
        # Current engine uses one least significant bit 
        # from each RGB channel (3 bits per pixel).
        usable_bits = pixels * 3
        
        usable_bytes = usable_bits // 8
        usable_kb = usable_bytes / 1024
        usable_mb = usable_kb / 1024

        return CapacityInfo(
            width=width,
            height=height,
            pixels=pixels,
            usable_bits=usable_bits,
            usable_bytes=usable_bytes,
            usable_kb=usable_kb,
            usable_mb=usable_mb
        )

    @classmethod
    def fits_payload(cls, image_path: Path | str, payload_size_bytes: int) -> bool:
        """
        Determines if a given payload can fit inside the carrier image.

        Args:
            image_path (Path | str): Path to the carrier PNG image.
            payload_size_bytes (int): Size of the payload (including delimiters/headers) in bytes.

        Returns:
            bool: True if the payload fits, False otherwise.

        Raises:
            ValueError: If payload_size_bytes is negative.
            FileNotFoundError: If the image file does not exist.
            FormatError: If the image is not a valid PNG.
        """
        if payload_size_bytes < 0:
            raise ValueError("Payload size cannot be negative.")

        capacity = cls.calculate(image_path)
        return payload_size_bytes <= capacity.usable_bytes

    @classmethod
    def remaining_capacity(cls, image_path: Path | str, payload_size_bytes: int) -> int:
        """
        Calculates the remaining byte capacity after embedding a payload.
        A negative return value indicates a deficit (the payload is too large).

        Args:
            image_path (Path | str): Path to the carrier PNG image.
            payload_size_bytes (int): Size of the payload in bytes.

        Returns:
            int: The remaining capacity in bytes.

        Raises:
            ValueError: If payload_size_bytes is negative.
            FileNotFoundError: If the image file does not exist.
            FormatError: If the image is not a valid PNG.
        """
        if payload_size_bytes < 0:
            raise ValueError("Payload size cannot be negative.")

        capacity = cls.calculate(image_path)
        return capacity.usable_bytes - payload_size_bytes


# =====================================================================
# Example Usage Block
# =====================================================================
if __name__ == "__main__":
    import tempfile
    import os

    print("--- StegoVault Capacity Engine Test ---")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_in:
        carrier_path = Path(f_in.name)

    try:
        # Generate a standard 1080p image
        print(f"[1] Generating a 1920x1080 carrier image at: {carrier_path}")
        img = Image.new("RGB", (1920, 1080), color=(0, 0, 0))
        img.save(carrier_path, format="PNG")

        print("\n[2] Calculating maximum capacity...")
        info = ImageCapacity.calculate(carrier_path)
        
        # Demonstrating the new formatted property
        print(f"    Dimensions      : {info.width}x{info.height}")
        print(f"    Total Pixels    : {info.pixels:,}")
        print(f"    Usable Bytes    : {info.usable_bytes:,}")
        print(f"    Formatted Output: {info.formatted}")

        test_payload = 500_000

        print("\n[3] Testing payload fits...")
        fits = ImageCapacity.fits_payload(carrier_path, test_payload)
        rem = ImageCapacity.remaining_capacity(carrier_path, test_payload)
        print(f"    Can hold {test_payload:,} bytes? {fits} (Remaining: {rem:,} bytes)")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
    finally:
        if carrier_path.exists():
            os.remove(carrier_path)