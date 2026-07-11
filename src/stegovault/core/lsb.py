"""
StegoVault Core: LSB Steganography Engine
Implements Least Significant Bit (1-bit LSB) steganography for hiding
UTF-8 encoded text payloads within the RGB channels of PNG images.
"""

from pathlib import Path
from typing import Generator
from PIL import Image

# Import decoupled exceptions
from stegovault.utils.exceptions import SteganographyError, CapacityError, FormatError


class LSBSteganography:
    """
    Core engine for embedding and extracting hidden UTF-8 text using 1-bit LSB.
    Strictly accepts PNG images and verifies headers to prevent data corruption.
    """

    # Note: V1 uses a hardcoded delimiter. V2 will replace this with a structured
    # binary header (Length, Encrypted Flag, Compressed Flag, Checksum, etc.).
    DELIMITER: bytes = b"!!STEGO_END_EOF!!"

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
                "StegoVault strictly requires .png extensions."
            )

        # Verify the actual file signature/header to prevent extension spoofing
        try:
            with Image.open(image_path) as img:
                if img.format != "PNG":
                    raise FormatError(
                        f"Spoofed file detected. Internal format is {img.format}, not PNG."
                    )
        except IOError as e:
            raise FormatError(f"Unable to read image data: {e}") from e

    @staticmethod
    def _bytes_to_bits(data: bytes) -> Generator[int, None, None]:
        """
        Converts a sequence of bytes into a generator of individual bits.

        Args:
            data (bytes): The byte sequence to convert.

        Yields:
            int: The next bit (0 or 1) in the sequence (MSB first).
        """
        for byte in data:
            for i in range(8):
                yield (byte >> (7 - i)) & 1

    @classmethod
    def encode_text(
        cls, input_image_path: Path | str, text: str, output_image_path: Path | str
    ) -> None:
        """
        Encodes UTF-8 text into the Least Significant Bits of a PNG image.

        Args:
            input_image_path (Path | str): Path to the carrier PNG image.
            text (str): The secret message to hide.
            output_image_path (Path | str): Path where the resulting PNG will be saved.

        Raises:
            ValueError: If the input text is empty.
            FormatError: If input path is not a valid PNG.
            CapacityError: If the text is too large for the image.
        """
        if not text:
            raise ValueError("Payload text cannot be empty.")

        in_path = Path(input_image_path)
        out_path = Path(output_image_path)

        cls._validate_png(in_path)

        payload_bytes = text.encode('utf-8') + cls.DELIMITER
        payload_bits_count = len(payload_bytes) * 8

        with Image.open(in_path) as img:
            encoded_img = img.convert("RGB")
            width, height = encoded_img.size
            max_bits = width * height * 3

            if payload_bits_count > max_bits:
                raise CapacityError(
                    f"Payload too large. Requires {payload_bits_count} bits, "
                    f"but the image can only hold {max_bits} bits."
                )

            # Using load() provides memory-efficient, in-place pixel access
            pixels = encoded_img.load()
            bit_generator = cls._bytes_to_bits(payload_bytes)

            # Define a helper to handle the iteration cleanly and break out early
            # without leaving a partially written pixel behind.
            def _embed_bits() -> None:
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]

                        try:
                            r = (r & ~1) | next(bit_generator)
                        except StopIteration:
                            pixels[x, y] = (r, g, b)
                            return

                        try:
                            g = (g & ~1) | next(bit_generator)
                        except StopIteration:
                            pixels[x, y] = (r, g, b)
                            return

                        try:
                            b = (b & ~1) | next(bit_generator)
                        except StopIteration:
                            pixels[x, y] = (r, g, b)
                            return

                        pixels[x, y] = (r, g, b)

            _embed_bits()
            encoded_img.save(out_path, format="PNG")

    @classmethod
    def decode_text(cls, input_image_path: Path | str) -> str:
        """
        Extracts hidden UTF-8 text from the Least Significant Bits of a PNG image.

        Args:
            input_image_path (Path | str): Path to the PNG image containing hidden data.

        Returns:
            str: The decoded secret message.

        Raises:
            FormatError: If the input path is not a valid PNG.
            SteganographyError: If no hidden message delimiter is found or decoding fails.
        """
        in_path = Path(input_image_path)
        cls._validate_png(in_path)

        extracted_bytes = bytearray()
        current_byte = 0
        bit_index = 0

        with Image.open(in_path) as img:
            encoded_img = img.convert("RGB")
            width, height = encoded_img.size
            
            # Using load() to prevent loading millions of tuples into memory
            pixels = encoded_img.load()

            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    
                    for color_channel in (r, g, b):
                        current_byte = (current_byte << 1) | (color_channel & 1)
                        bit_index += 1

                        if bit_index == 8:
                            extracted_bytes.append(current_byte)
                            current_byte = 0
                            bit_index = 0

                            # Check for the end of the message
                            if extracted_bytes.endswith(cls.DELIMITER):
                                payload = extracted_bytes[:-len(cls.DELIMITER)]
                                try:
                                    return payload.decode('utf-8')
                                except UnicodeDecodeError as e:
                                    raise SteganographyError(
                                        "Data extracted successfully, but failed to decode as UTF-8."
                                    ) from e

        raise SteganographyError(
            "Delimiter not found. This image may not contain hidden data, "
            "or the data was corrupted."
        )


# =====================================================================
# Example Usage Block (Can be safely removed or used for testing)
# =====================================================================
if __name__ == "__main__":
    import tempfile
    import os

    print("--- StegoVault LSB Core Engine Test ---")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_in, \
         tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_out:
        
        carrier_path = Path(f_in.name)
        stego_path = Path(f_out.name)

    try:
        # Generate carrier image
        img = Image.new("RGB", (200, 200), color=(50, 100, 200))
        img.save(carrier_path, format="PNG")

        secret_message = "Memory-efficient embedding successful! 🚀"
        print(f"Secret message to hide: '{secret_message}'")

        LSBSteganography.encode_text(
            input_image_path=carrier_path,
            text=secret_message,
            output_image_path=stego_path
        )
        print("-> Encoding successful.")

        recovered_message = LSBSteganography.decode_text(input_image_path=stego_path)
        print(f"-> Recovered message: '{recovered_message}'")

        assert secret_message == recovered_message
        print("\n✅ SUCCESS: Tests passed!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
    finally:
        if carrier_path.exists():
            os.remove(carrier_path)
        if stego_path.exists():
            os.remove(stego_path)