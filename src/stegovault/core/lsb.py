"""
StegoVault Core: LSB Steganography Engine
A completely generic Least Significant Bit (1-bit LSB) engine.
Embeds and extracts arbitrary binary streams (bytes) across the RGB 
channels of PNG images.
"""

import struct
from pathlib import Path
from typing import Generator
from PIL import Image

# Import decoupled exceptions
from stegovault.utils.exceptions import SteganographyError, CapacityError, FormatError


class LSBSteganography:
    """
    Core engine for embedding and extracting raw bytes using 1-bit LSB.
    Strictly accepts PNG images and relies on a 4-byte length prefix 
    for extremely fast and precise payload extraction.
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
                "StegoVault strictly requires .png extensions."
            )

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
    def encode_bytes(
        cls, input_image_path: Path | str, payload: bytes, output_image_path: Path | str
    ) -> None:
        """
        Encodes a raw byte stream into the Least Significant Bits of a PNG image.
        Automatically prepends a 4-byte length header.

        Args:
            input_image_path (Path | str): Path to the carrier PNG image.
            payload (bytes): The arbitrary binary data to hide.
            output_image_path (Path | str): Path where the resulting PNG will be saved.

        Raises:
            ValueError: If the payload is empty.
            FormatError: If input path is not a valid PNG.
            CapacityError: If the payload is too large for the image.
        """
        if not payload:
            raise ValueError("Payload cannot be empty.")

        in_path = Path(input_image_path)
        out_path = Path(output_image_path)

        cls._validate_png(in_path)

        # Prepend a 4-byte unsigned int (>I) representing the exact payload length
        length_header = struct.pack(">I", len(payload))
        full_payload_bytes = length_header + payload
        full_payload_bits_count = len(full_payload_bytes) * 8

        with Image.open(in_path) as img:
            encoded_img = img.convert("RGB")
            width, height = encoded_img.size
            max_bits = width * height * 3

            if full_payload_bits_count > max_bits:
                raise CapacityError(
                    f"Payload too large. Requires {full_payload_bits_count} bits, "
                    f"but the image can only hold {max_bits} bits."
                )

            pixels = encoded_img.load()
            bit_generator = cls._bytes_to_bits(full_payload_bytes)

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
    def decode_bytes(cls, input_image_path: Path | str) -> bytes:
        """
        Extracts a hidden byte stream from the Least Significant Bits of a PNG image.

        Args:
            input_image_path (Path | str): Path to the PNG image containing hidden data.

        Returns:
            bytes: The extracted binary payload.

        Raises:
            FormatError: If the input path is not a valid PNG.
            SteganographyError: If the image contains no valid hidden data.
        """
        in_path = Path(input_image_path)
        cls._validate_png(in_path)

        extracted_bytes = bytearray()
        current_byte = 0
        bit_index = 0

        reading_length_header = True
        payload_length = 0
        bytes_read = 0

        with Image.open(in_path) as img:
            encoded_img = img.convert("RGB")
            width, height = encoded_img.size
            max_payload_bytes = (width * height * 3) // 8 - 4
            
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

                            # Phase 1: Read the 4-byte length prefix
                            if reading_length_header:
                                if len(extracted_bytes) == 4:
                                    payload_length = struct.unpack(">I", extracted_bytes)[0]
                                    
                                    # Sanity check the length against image capacity
                                    if payload_length == 0 or payload_length > max_payload_bytes:
                                        raise SteganographyError(
                                            "Invalid length header. This image does not "
                                            "appear to contain StegoVault data."
                                        )
                                    
                                    reading_length_header = False
                                    extracted_bytes.clear()

                            # Phase 2: Read the actual payload
                            else:
                                bytes_read += 1
                                if bytes_read == payload_length:
                                    return bytes(extracted_bytes)

        raise SteganographyError("Reached the end of the image before the payload was fully extracted.")


# =====================================================================
# Example Usage Block
# =====================================================================
if __name__ == "__main__":
    import tempfile
    import os

    print("--- StegoVault Generic LSB Engine Test ---")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_in, \
         tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_out:
        
        carrier_path = Path(f_in.name)
        stego_path = Path(f_out.name)

    try:
        # Generate carrier image
        img = Image.new("RGB", (200, 200), color=(50, 100, 200))
        img.save(carrier_path, format="PNG")

        # Test with raw, arbitrary bytes (e.g., simulating a compressed/encrypted payload)
        test_payload = b"\x00\xFFGeneric Byte Stream!\x88\x12\x34"
        print(f"[1] Raw payload to hide : {test_payload}")

        LSBSteganography.encode_bytes(
            input_image_path=carrier_path,
            payload=test_payload,
            output_image_path=stego_path
        )
        print("[2] Raw bytes encoded successfully.")

        recovered_bytes = LSBSteganography.decode_bytes(input_image_path=stego_path)
        print(f"[3] Recovered raw bytes : {recovered_bytes}")

        assert test_payload == recovered_bytes
        print("\n✅ SUCCESS: Generic byte engine is working perfectly!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
    finally:
        if carrier_path.exists():
            os.remove(carrier_path)
        if stego_path.exists():
            os.remove(stego_path)