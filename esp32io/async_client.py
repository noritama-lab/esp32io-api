import json
import asyncio
import serial_asyncio

from .exceptions import ESP32IOError, ESP32ConnectionError
from .models import (
    ResponseBase,
    DioReadResponse,
    AdcReadResponse,
    StatusResponse,
    IOStateResponse,
)
from .base import ESP32IOBase

class ESP32IOAsync(ESP32IOBase):
    RECONNECT_WAIT = 0.5

    def __init__(self, port: str, baudrate: int = 115200,
                 timeout: float = 1.0, autoreconnect: bool = True):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.autoreconnect = autoreconnect

        self.reader = None
        self.writer = None

        self.cmd_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()

        self.lock = asyncio.Lock()
        self._stop = False

        self.worker_task = None
        self.reconnect_task = None

    # ------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------
    async def connect(self):
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate
            )
        except Exception as e:
            raise ESP32ConnectionError(f"Failed to open serial port {self.port}: {e}")

    async def reconnect_loop(self):
        while not self._stop:
            if (self.reader is None or self.writer is None) and self.autoreconnect:
                try:
                    await self.connect()
                except Exception:
                    pass
            await asyncio.sleep(self.RECONNECT_WAIT)

    # ------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------
    async def worker_loop(self):
        while not self._stop:
            try:
                cmd, model = await asyncio.wait_for(self.cmd_queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            try:
                if self.writer is None or self.reader is None:
                    raise ESP32ConnectionError("Serial not connected")

                # Send
                line = json.dumps(cmd) + "\n"
                self.writer.write(line.encode("utf-8"))
                await self.writer.drain()

                # Receive
                resp_line = await self.reader.readline()
                if not resp_line:
                    raise ESP32IOError("No response from device")

                try:
                    json_obj = json.loads(resp_line.decode("utf-8").strip())
                except json.JSONDecodeError as e:
                    raise ESP32IOError(f"Invalid JSON from device: raw={resp_line!r}") from e

                res = self.parse_response(json_obj, model)
                await self.result_queue.put(res)

            except Exception as e:
                await self.result_queue.put(e)

    # ------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------
    async def start(self):
        """Connect and start worker/reconnect tasks."""
        await self.connect()
        self._stop = False
        self.worker_task = asyncio.create_task(self.worker_loop())
        self.reconnect_task = asyncio.create_task(self.reconnect_loop())

    async def close(self):
        """Stop tasks and close serial."""
        self._stop = True

        if self.worker_task:
            self.worker_task.cancel()
        if self.reconnect_task:
            self.reconnect_task.cancel()

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    async def request(self, cmd: dict, model):
        async with self.lock:
            await self.cmd_queue.put((cmd, model))
            try:
                res = await asyncio.wait_for(self.result_queue.get(), timeout=self.timeout)
            except asyncio.TimeoutError:
                raise ESP32IOError(f"Timeout waiting response for cmd={cmd.get('cmd')}")

        if isinstance(res, Exception):
            raise res
        return res

    # -------------------------
    # Commands
    # -------------------------
    async def read_dio(self, pin_id: int) -> int:
        cmd = self.build_cmd("read_dio", pin_id=pin_id)
        return (await self.request(cmd, DioReadResponse)).value

    async def write_dio(self, pin_id: int, value: int):
        if value not in (0, 1):
            raise ValueError("value must be 0 or 1")
        cmd = self.build_cmd("write_dio", pin_id=pin_id, value=value)
        await self.request(cmd, ResponseBase)

    async def read_adc(self, pin_id: int) -> int:
        cmd = self.build_cmd("read_adc", pin_id=pin_id)
        return (await self.request(cmd, AdcReadResponse)).value

    async def set_pwm(self, pin_id: int, duty: int):
        if not 0 <= duty <= 255:
            raise ValueError("duty must be 0-255")
        cmd = self.build_cmd("set_pwm", pin_id=pin_id, duty=duty)
        await self.request(cmd, ResponseBase)

    async def get_status(self) -> StatusResponse:
        cmd = self.build_cmd("get_status")
        return await self.request(cmd, StatusResponse)
    
    async def get_io_state(self) -> IOStateResponse:
        cmd = self.build_cmd("get_io_state")
        return await self.request(cmd, IOStateResponse)

    async def ping(self) -> ResponseBase:
        cmd = self.build_cmd("ping")
        return await self.request(cmd, ResponseBase)