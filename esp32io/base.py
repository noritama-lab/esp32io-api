import json
from .exceptions import ESP32DeviceError


class ESP32IOBase:
    """Protocol utilities shared by sync/async clients."""

    def build_cmd(self, cmd: str, **kwargs):
        return {"cmd": cmd, **kwargs}

    def parse_response(self, json_obj: dict, model):
        res = model(**json_obj)
        if res.status == "error":
            raise ESP32DeviceError(f"{res.code}: {res.detail}")
        return res