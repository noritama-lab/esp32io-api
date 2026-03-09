class ESP32IOError(Exception):
    """Base exception for ESP32 I/O errors."""
    pass


class ESP32ConnectionError(ESP32IOError):
    """Raised when serial connection fails."""
    pass


class ESP32DeviceError(ESP32IOError):
    """Raised when device returns status='error'."""
    pass