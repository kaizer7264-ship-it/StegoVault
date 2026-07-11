"""
StegoVault Utilities: Exceptions
Contains custom exceptions used throughout the StegoVault application
to provide meaningful error handling and context.
"""

class SteganographyError(Exception):
    """Base exception for all steganography and cryptography-related errors."""
    pass

class CapacityError(SteganographyError):
    """Raised when the payload exceeds the maximum capacity of the carrier medium."""
    pass

class FormatError(SteganographyError):
    """Raised when an unsupported or spoofed image format is provided."""
    pass