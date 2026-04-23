import json
import time
import logging
import threading
import requests
import serial
from typing import Optional, Dict, Any, List, Literal
from abc import ABC, abstractmethod
from .exceptions import ESP32S3IODeviceError, ESP32S3IONetworkError, ESP32S3IOSerialError, ESP32S3IOProtocolError
from . import protocol

logger = logging.getLogger(__name__)

class ESP32S3IOBase(ABC):
    """ESP32-S3 IO デバイス操作の共通基底クラス"""
    
    def __init__(self, debug: bool = False):
        if debug:
            logging.basicConfig(level=logging.DEBUG)

    @abstractmethod
    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """トランスポート層（Network/Serial）で実装される抽象メソッド"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _process_response(self, data: Dict[str, Any], cmd: str) -> Dict[str, Any]:
        """デバイスからのレスポンスを検証し、エラーがあれば例外を投げる"""
        if data.get("status") == "error":
            code = data.get("code", "UNKNOWN")
            detail = data.get("detail", "")
            raise ESP32S3IODeviceError(f"Device error on '{cmd}': {code} ({detail})")
        return data

    def _log(self, *args: Any) -> None:
        logger.debug(" ".join(map(str, args)))

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
            "dio_out": list(res.get("dio_out", [])),
            "adc":     list(res.get("adc", [])),
            "pwm":     list(res.get("pwm", [])),
        }

    def read_di(self, pin_id: int) -> int:
        """デジタル入力の読み取り"""
        if not isinstance(pin_id, int):
            raise ValueError("pin_id must be an integer")
        res = self.command(protocol.CMD_READ_DI, pin_id=pin_id)
        val = res.get("value")
        if not isinstance(val, int):
            raise ESP32S3IOProtocolError(f"Invalid read_di response: {res}")
        return val

    def set_do(self, pin_id: int, value: int) -> bool:
        """デジタル出力の設定 (0 or 1)"""
        if value not in (0, 1):
            raise ValueError("value must be 0 or 1")
        res = self.command(protocol.CMD_SET_DO, pin_id=pin_id, value=value)
        return res.get("status") == "ok"

    def read_adc(self, pin_id: int) -> int:
        """アナログ入力の読み取り"""
        if not isinstance(pin_id, int):
            raise ValueError("pin_id must be an integer")
        res = self.command(protocol.CMD_READ_ADC, pin_id=pin_id)
        val = res.get("value")
        if not isinstance(val, int):
            raise ESP32S3IOProtocolError(f"Invalid read_adc response: {res}")
        return val

    def set_pwm(self, pin_id: int, duty: int) -> Dict[str, Any]:
        """PWM出力の設定"""
        if not (0 <= duty):
            raise ValueError("duty must be 0 or greater")
        res = self.command(protocol.CMD_SET_PWM, pin_id=pin_id, duty=duty)
        return res

    def get_pwm_config(self) -> Dict[str, int]:
        """現在のPWM周波数、分解能、および最大デューティを取得"""
        """現在のPWM周波数、分解能、および最大デューティを取得"""
        res = self.command(protocol.CMD_GET_PWM_CONFIG)
        if not isinstance(res.get("freq"), int) or not isinstance(res.get("res"), int) or not isinstance(res.get("max_duty"), int):
            raise ESP32S3IOProtocolError(f"Invalid get_pwm_config response: {res}")
        return {"freq": res["freq"], "res": res["res"], "max_duty": res["max_duty"]}

    def set_pwm_config(self, freq: int, res_bit: int) -> bool:
        """PWMの周波数と分解能を動的に変更"""
        res = self.command(protocol.CMD_SET_PWM_CONFIG, freq=freq, res=res_bit)
        return res.get("status") == "ok"

    def set_rgb(self, r: int, g: int, b: int, brightness: Optional[int] = None) -> bool:
        """内蔵RGB LEDの制御"""
        if any(not (0 <= c <= 255) for c in (r, g, b)):
            raise ValueError("RGB values must be between 0 and 255")
        kwargs = {"r": r, "g": g, "b": b}
        if brightness is not None:
            kwargs["brightness"] = brightness
        res = self.command(protocol.CMD_SET_RGB, **kwargs)
        return res.get("status") == "ok"

    def led_off(self) -> bool:
        """RGB LEDの消灯"""
        res = self.command(protocol.CMD_LED_OFF)
        return res.get("status") == "ok"

    def set_led_mode(self, mode: Literal["status", "manual"]) -> bool:
        """LEDの動作モードを設定 ('status' または 'manual')"""
        res = self.command(protocol.CMD_SET_LED_MODE, mode=mode)
        return res.get("status") == "ok"

    def get_led_state(self) -> Dict[str, Any]:
        """現在のLED設定値を取得"""
        return self.command(protocol.CMD_GET_LED_STATE)

    def help(self) -> List[str]:
        """デバイスがサポートするコマンド一覧を取得"""
        res = self.command(protocol.CMD_HELP)
        return res.get("commands", [])

    def close(self):
        """リソースを解放する (サブクラスでオーバーライド)"""
        pass


class ESP32S3IONet(ESP32S3IOBase):
    """HTTP API を使用してネットワーク経由で操作するクライアント"""
    def __init__(self, ip_address: str, timeout: float = 5.0, debug: bool = False):
        super().__init__(debug=debug)
        self.base_url = f"http://{ip_address}/api"
        # (接続タイムアウト, 読み取りタイムアウト) のタプルで指定
        # Wi-Fi不安定時は接続タイムアウトを短く設定するのがセオリー
        self.timeout = (2.0, timeout)
        self.session = requests.Session()

    def _reconnect_session(self):
        """エラー時にセッションをリセットしてコネクションをクリーンにする"""
        self._log("Resetting HTTP session due to network error.")
        self.session.close()
        self.session = requests.Session()

    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cmd_name = payload.get("cmd", "unknown")
        try:
            response = self.session.post(
                url=self.base_url,
                json=payload,
                timeout=self.timeout,
                allow_redirects=False
            )
            self._log(f"HTTP POST {self.base_url} {payload} -> {response.status_code}")
            
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

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            # ネットワークの問題が発生した場合はセッションをリセット
            self._reconnect_session()
            raise ESP32S3IONetworkError(f"Network connectivity issue: {e}")
        except requests.exceptions.RequestException as e:
            raise ESP32S3IONetworkError(f"HTTP Request failed: {e}")

    def close(self):
        self.session.close()


class ESP32S3IOSerial(ESP32S3IOBase):
    """USB シリアル (JSONプロトコル) を使用して操作するクライアント"""
    def __init__(self, port: str, baud: int = 115200, timeout: float = 2.0, debug: bool = False):
        super().__init__(debug=debug)
        try:
            # DTR/RTS 制御を無効にして、ポート開閉時のリセットを防ぐ
            self.ser = serial.Serial(port, baudrate=baud, timeout=timeout, dsrdtr=False, rtscts=False)
            self.ser.dtr = False
            self.ser.rts = False
            
            self._lock = threading.Lock()
            # ESP32-S3のUSB CDCが安定するまで待機
            time.sleep(0.5)
            self.ser.reset_input_buffer()
            
            # ウォームアップ: 最初の通信が化けることがあるためpingを投げておく
            try:
                with self._lock:
                    self.ser.write(b'{"cmd":"ping"}\n')
                    self.ser.readline()
            except Exception: pass
        except serial.SerialException as e:
            raise ESP32S3IOSerialError(f"Failed to open port {port}: {e}")

    def _execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        cmd_name = payload.get("cmd", "unknown")
        with self._lock:
            try:
                # コマンド送信前に受信バッファをクリアし、古いログ等の混入を防ぐ
                self.ser.reset_input_buffer()

                # JSON送信
                line = json.dumps(payload, separators=(",", ":")) + "\n"
                self._log(f"SEND: {line.strip()}")
                self.ser.write(line.encode("ascii"))
                
                # 応答待ち（シリアル上のログ出力を無視してJSONを探す）
                start_time = time.monotonic()
                effective_timeout = self.ser.timeout or 2.0
                while (time.monotonic() - start_time) < effective_timeout:
                    if self.ser.in_waiting == 0:
                        time.sleep(0.01)
                        continue
                    resp_line = self.ser.readline().decode("utf-8", errors="replace").strip()
                    if not resp_line:
                        continue
                    
                    # JSON らしき開始文字がない場合はログとみなしてスキップ
                    if not resp_line.startswith("{"):
                        self._log(f"SKIP (Log): {resp_line}")
                        continue

                    # JSONとしてパースを試みる
                    try:
                        data = json.loads(resp_line)
                        self._log(f"RECV (JSON): {resp_line}")
                        return self._process_response(data, cmd_name)
                    except json.JSONDecodeError:
                        # { で始まっていても不正な形式ならスキップして次を待つ
                        self._log(f"SKIP (Invalid JSON): {resp_line}")
                        continue
                
                raise ESP32S3IOSerialError(f"Timeout waiting for response to '{cmd_name}'")
            except serial.SerialException as e:
                raise ESP32S3IOSerialError(f"Serial communication error: {e}")

    def close(self):
        if hasattr(self, "ser") and self.ser.is_open:
            self.ser.dtr = False
            self.ser.rts = False
            self.ser.close()

    def __del__(self):
        self.close()