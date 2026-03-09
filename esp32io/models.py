from pydantic import BaseModel
from typing import Optional


class ResponseBase(BaseModel):
    status: str
    code: Optional[str] = None
    detail: Optional[str] = None


class DioReadResponse(ResponseBase):
    value: int


class AdcReadResponse(ResponseBase):
    value: int


class StatusResponse(ResponseBase):
    uptime_ms: int
    free_heap: int

class IOStateResponse(ResponseBase):
    dio_in: list[int]
    dio_out: list[int]
    adc: list[int]
    pwm: list[int]