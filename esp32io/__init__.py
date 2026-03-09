from .exceptions import (
    ESP32IOError,
    ESP32ConnectionError,
    ESP32DeviceError,
)
from .models import (
    ResponseBase,
    DioReadResponse,
    AdcReadResponse,
    StatusResponse,
)
from .async_client import ESP32IOAsync
from .advanced_io import AdvancedIO


class ESP32IO(AdvancedIO, ESP32IOAsync):
    """Final public API class."""
    pass


__all__ = [
    "ESP32IO",
    "ESP32IOError",
    "ESP32ConnectionError",
    "ESP32DeviceError",
    "ResponseBase",
    "DioReadResponse",
    "AdcReadResponse",
    "StatusResponse",
]