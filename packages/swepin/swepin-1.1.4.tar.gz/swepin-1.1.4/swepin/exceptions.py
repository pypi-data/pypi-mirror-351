class SwePinFormatError(Exception):
    """PIN format validation failed."""
    pass

class SwePinLuhnError(Exception):
    """PIN Luhn checksum validation failed."""
    pass
