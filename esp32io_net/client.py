import json
import time
import requests
import serial
from typing import Optional, Dict, Any, List
from .exceptions import ESP32S3IODeviceError, ESP32S3IONetworkError, ESP32S3IOSerialError, ESP32S3IOProtocolError
from . import protocol

class ESP32S3IOBase:
    """ESP32-S3 IO デバイス操作の共通基底クラス"""
    debug = False
    
    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """トランスポート層（Network/Serial）で実装される抽象メソッド"""
        raise NotImplementedError

    def _process_response(self, data: Dict[str, Any], cmd: str) -> Dict[str, Any]:
        """デバイスからのレスポンスを検証し、エラーがあれば例外を投げる"""
        if data.get("status") == "error":
            code = data.get("code", "UNKNOWN")
            detail = data.get("detail", "")
            raise ESP32S3IODeviceError(f"Device error on '{cmd}': {code} ({detail})")
        return data

    def _log(self, *args: Any) -> None:
        if self.debug:
            print("[ESP32S3IO]", *args)

    def command(self, cmd: str, **kwargs: Any) -> Dict[str, Any]:
        """任意のコマンドを送信し、JSON 応答を返す低レベル API"""
        payload = {"cmd": cmd}
        payload.update(kwargs)
        return self._execute(payload)

    def ping(self) -> bool:
        """疎通確認"""
        res = self.command(protocol.CMD_PING)
        return res.get("message") == "pong"

    def get_status(self) -> Dict[str, Any]:
        """デバイスの稼働状況（起動時間、ヒープ、IP等）を取得"""
        return self.command(protocol.CMD_GET_STATUS)

    def get_io_state(self) -> Dict[str, Any]:
        """DI, DO, ADC, PWM の全状態を一括取得"""
        res = self.command(protocol.CMD_GET_IO_STATE)
        return {
            "dio_in":  list(res["dio_in"]),
            "dio_out": list(res["dio_out"]),
            "adc":     list(res["adc"]),
            "pwm":     list(res["pwm"]),
        }

    def read_di(self, pin_id: int) -> int:
        """デジタル入力の読み取り"""
        res = self.command(protocol.CMD_READ_DI, pin_id=pin_id)
        val = res.get("value")
        if not isinstance(val, int):
            raise ESP32S3IOProtocolError(f"Invalid read_di response: {res}")
        return val

    def set_do(self, pin_id: int, value: int) -> bool:
        """デジタル出力の設定 (0 or 1)"""
        res = self.command(protocol.CMD_SET_DO, pin_id=pin_id, value=value)
        return res.get("status") == "ok"

    def read_adc(self, pin_id: int) -> int:
        """アナログ入力の読み取り"""
        res = self.command(protocol.CMD_READ_ADC, pin_id=pin_id)
        val = res.get("value")
        if not isinstance(val, int):
            raise ESP32S3IOProtocolError(f"Invalid read_adc response: {res}")
        return val

    def set_pwm(self, pin_id: int, duty: int) -> int:
        """PWM出力の設定"""
        res = self.command(protocol.CMD_SET_PWM, pin_id=pin_id, duty=duty)
        return res["duty"]

    def get_pwm_config(self) -> Dict[str, int]:
        """現在のPWM周波数と分解能を取得"""
        res = self.command(protocol.CMD_GET_PWM_CONFIG)
        if not isinstance(res.get("freq"), int) or not isinstance(res.get("res"), int):
            raise ESP32S3IOProtocolError(f"Invalid get_pwm_config response: {res}")
        return {"freq": res["freq"], "res": res["res"]}

    def set_pwm_config(self, freq: int, res_bit: int) -> Dict[str, int]:
        """PWMの周波数と分解能を動的に変更"""
        res = self.command(protocol.CMD_SET_PWM_CONFIG, freq=freq, res=res_bit)
        if not isinstance(res.get("freq"), int) or not isinstance(res.get("res"), int):
            raise ESP32S3IOProtocolError(f"Invalid set_pwm_config response: {res}")
        return {"freq": res["freq"], "res": res["res"]}

    def set_rgb(self, r: int, g: int, b: int, brightness: Optional[int] = None) -> bool:
        """内蔵RGB LEDの制御"""
        payload = {"cmd": protocol.CMD_SET_RGB, "r": r, "g": g, "b": b}
        if brightness is not None:
            payload["brightness"] = brightness
        res = self._execute(payload) # 直接 execute
        return res.get("status") == "ok"

    def led_off(self) -> bool:
        """RGB LEDの消灯（ステータス表示モードへの復帰）"""
        res = self.command(protocol.CMD_LED_OFF)
        return res.get("status") == "ok"

    def get_led_state(self) -> Dict[str, Any]:
        """現在のLED設定値を取得"""
        return self.command(protocol.CMD_GET_LED_STATE)

    def help(self) -> List[str]:
        """デバイスがサポートするコマンド一覧を取得"""
        res = self.command(protocol.CMD_HELP)
        return res.get("commands", [])


class ESP32S3IONet(ESP32S3IOBase):
    """HTTP API を使用してネットワーク経由で操作するクライアント"""
    def __init__(self, ip_address: str, timeout: int = 5, debug: bool = False):
        self.base_url = f"http://{ip_address}/api"
        self.timeout = timeout
        self.debug = debug

    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cmd_name = payload.get("cmd", "unknown")
        try:
            response = requests.post(
                url=self.base_url,
                json=payload,
                timeout=self.timeout,
                allow_redirects=False
            )
            self._log(f"HTTP {payload} -> {response.status_code}")
            
            # HTTPステータスに関わらず、まずJSONとしてパースを試みる
            # デバイスは400エラー時も詳細なJSONを返すため
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError):
                # JSONでない場合はHTTPエラーを発生させる
                response.raise_for_status()
                raise ESP32S3IONetworkError(f"Unexpected non-JSON response: {response.text}")

            self._log(f"RECV: {data}")
            return self._process_response(data, cmd_name)

        except requests.exceptions.RequestException as e:
            raise ESP32S3IONetworkError(f"HTTP Request failed: {e}")


class ESP32S3IOSerial(ESP32S3IOBase):
    """USB シリアル (JSONプロトコル) を使用して操作するクライアント"""
    def __init__(self, port: str, baud: int = 115200, timeout: float = 2.0, debug: bool = False):
        try:
            self.ser = serial.Serial(port, baudrate=baud, timeout=timeout)
            self.debug = debug
            # ESP32-S3のUSB CDCが安定するまで待機
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            
            # ウォームアップ: 最初の通信が化けることがあるためpingを投げておく
            try:
                self.ser.write(b'{"cmd":"ping"}\n')
                self.ser.readline()
            except Exception: pass
        except serial.SerialException as e:
            raise ESP32S3IOSerialError(f"Failed to open port {port}: {e}")

    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cmd_name = payload.get("cmd", "unknown")
        try:
            # JSON送信
            line = json.dumps(payload, separators=(",", ":")) + "\n"
            self._log(f"SEND: {line.strip()}")
            self.ser.write(line.encode("utf-8"))
            
            # 応答待ち（シリアル上のログ出力を無視してJSONを探す）
            start_time = time.monotonic()
            timeout = self.ser.timeout
            while timeout is None or (time.monotonic() - start_time) < timeout:
                resp_line = self.ser.readline().decode("utf-8", errors="replace").strip()
                if not resp_line:
                    continue
                if resp_line.startswith("{"):
                    self._log(f"RECV: {resp_line}")
                    return self._process_response(json.loads(resp_line), cmd_name)
            
            raise ESP32S3IOSerialError(f"Timeout waiting for response to '{cmd_name}'")
        except (serial.SerialException, json.JSONDecodeError) as e:
            raise ESP32S3IOProtocolError(f"Serial communication or JSON error: {e}")

    def close(self):
        if hasattr(self, "ser") and self.ser.is_open:
            self.ser.close()

    def __del__(self):
        self.close()