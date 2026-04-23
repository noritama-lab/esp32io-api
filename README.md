# ESP32IO Python API

日本語 / English

---

## 日本語

ESP32IO は、ESP32-S3 を USB シリアルまたは Wi-Fi (HTTP) 経由で Python から扱うための軽量クライアントです。
ESP32 側で JSON コマンドを受け取るファームウェアと組み合わせることで、DIO、ADC、PWM、および内蔵 RGB LED をシンプルな Python API で操作できます。

### 特徴

- USB シリアルおよび Wi-Fi (HTTP) 経由での通信を単一パッケージでサポート
- JSON プロトコルを `ESP32IOSerial` および `ESP32IONet` クラスが隠蔽
- DIO、ADC、PWM、内蔵 RGB LED、システム状態の取得をサポート
- PWM 周波数と分解能の取得・更新をサポート
- 接続エラー、タイムアウト、プロトコル不整合、ESP32 側エラーなど 5 つの例外を定義
- 低レベル API `command()` も用意

### 動作環境

- Python 3.8 以上
- `pyserial>=3.5`
- 対応する ESP32-S3 ファームウェア

### インストール

開発中のローカル環境で使う場合:

```bash
pip install -e .
```

依存関係だけ入れる場合:

```bash
pip install -r requirements.txt
```

### クイックスタート

**USB シリアル接続:**

```python
from esp32io import ESP32IOSerial

esp = ESP32IOSerial("COM4", debug=False)
```

**Wi-Fi (HTTP) 接続:**

```python
from esp32io import ESP32IONet

esp = ESP32IONet("192.168.1.10", debug=False)
```

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))
print("pwm config =", esp.get_pwm_config())

esp.set_do(0, 1)
esp.set_pwm(0, 128)

state = esp.get_io_state()
print(state)

esp.close()  # 通信の終了
```

サンプル実行:

```bash
py -m examples.serial_example
```

### API 一覧

- `ESP32IOSerial(port, baud=115200, timeout=2.0, debug=False, recv_timeout=None)`
    USB シリアル経由で ESP32 に接続します。
- `ESP32IONet(address, timeout=2.0, debug=False)`
    Wi-Fi (HTTP) 経由で ESP32 に接続します。`address` は IP アドレスまたはホスト名です。
- `ping() -> bool`
    疎通確認を行い、`pong` 応答を検証します。
- `read_di(pin_id) -> int`
    デジタル入力を 0 または 1 で返します。
- `set_do(pin_id, value) -> dict`
    デジタル出力を設定します。
- `read_adc(pin_id) -> int`
    ADC 値を返します。
- `set_pwm(pin_id, duty) -> dict`
    PWM デューティを設定し、適用された値を返します。
- `get_pwm_config() -> dict`
    PWM の周波数 (`freq`)、分解能 (`res`)、および現在の解像度での最大値 (`max_duty`) を返します。
- `set_pwm_config(freq, res) -> bool`
    PWM の周波数と分解能を設定します。
- `set_led_mode(mode) -> bool`
    LED の動作モード (`status` または `manual`) を設定します。
- `set_rgb(r, g, b, brightness) -> bool`
    内蔵 RGB LED の色と明るさを設定します。
- `led_off() -> bool`
    LED を消灯します。
- `get_io_state() -> dict`
    DIO、ADC、PWM の状態をまとめて返します。
- `get_status() -> dict`
    デバイスの稼働時間、ヒープメモリ、ネットワーク状態などを取得します。
- `command(cmd, **kwargs) -> dict`
    任意の JSON コマンドを送る低レベル API です。
- `help() -> list`
    デバイスがサポートしているコマンド一覧を返します。
- `close() -> None`
    通信セッションを終了します（シリアルの場合はポートを解放します）。

### 例外

- `ESP32IOError` (Base)
    すべての例外の基底クラス
- `ESP32IOConnectionError`
    シリアルポートや HTTP 接続の失敗
- `ESP32IOTimeoutError`
    応答待ちがタイムアウトした場合
- `ESP32IOProtocolError`
    JSON 不正や期待しない応答を受けた場合
- `ESP32IOCommandError`
    ESP32 が `status=error` を返した場合（コマンド実行失敗）

### 想定コマンド

このクライアントは、少なくとも以下のコマンドを実装したファームウェアを前提にしています。

- `ping`
- `read_di`
- `set_do`
- `read_adc`
- `set_pwm`
- `get_pwm_config`
- `set_pwm_config`
- `set_led_mode`
- `set_rgb`
- `get_io_state`
- `get_status`
- `help`

### プロジェクト構成

```text
.
├── esp32io/
│   ├── __init__.py
│   ├── client.py        # ESP32IOSerial & ESP32IONet
│   ├── exceptions.py    # Unified exceptions
│   └── protocol.py      # JSON Protocol logic
├── examples/
│   ├── serial_example.py
│   └── wifi_example.py
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

### ファームウェアについて

この Python パッケージ自体には ESP32 側ファームウェアは含まれていません。
別途、同じ JSON コマンド仕様に従う ESP32-S3 ファームウェアを用意してください。

ファームウェア:  
https://github.com/noritama-lab/esp32io-firmware

### ライセンス

MIT License

Copyright (c) 2026 Noritama-Lab

---

## English
-
ESP32IO is a lightweight Python client for controlling an ESP32-S3 over USB serial or Wi-Fi (HTTP).
When paired with firmware that accepts JSON commands, it provides a small and practical API for digital I/O, ADC, and PWM control.

### Features
- Support for both USB serial and Wi-Fi (HTTP) communication in a single package
- JSON protocol abstracted by `ESP32IOSerial` and `ESP32IONet` classes
- Support for `ping`, DIO, ADC, PWM, and full I/O state reads
- Support for built-in RGB LED control and system status retrieval
- Support for reading and updating PWM frequency and resolution
- Unified exception handling for device errors, timeouts, and protocol issues
- Includes a low-level `command()` API for custom JSON commands

### Requirements

- Python 3.8+
- `pyserial>=3.5`
- `requests>=2.25.0`
- Compatible ESP32-S3 firmware

### Installation

For local development:

```bash
pip install -e .
```

To install dependencies only:

```bash
pip install -r requirements.txt
```

### Quick Start

**Via USB Serial:**

```python
from esp32io import ESP32IOSerial

esp = ESP32IOSerial("COM4", debug=False)
```

**Via Wi-Fi (HTTP):**

```python
from esp32io import ESP32IONet

esp = ESP32IONet("192.168.1.10", debug=False)
```

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))
print("pwm config =", esp.get_pwm_config())

esp.set_do(0, 1)
esp.set_pwm(0, 128)

state = esp.get_io_state()
print(state)

esp.close()  # End communication
```

Run the sample:

```bash
py -m examples.esp32io_sample
```

### API Summary

- `ESP32IOSerial(port, baud=115200, timeout=2.0, debug=False, recv_timeout=None)`
    Connects to the ESP32 via USB serial.
- `ESP32IONet(address, timeout=2.0, debug=False)`
    Connects to the ESP32 via Wi-Fi (HTTP). `address` is the IP or hostname.
- `ping() -> bool`
    Verifies connectivity by checking for a `pong` response.
- `read_di(pin_id) -> int`
    Reads a digital input and returns `0` or `1`.
- `set_do(pin_id, value) -> dict`
    Sets a digital output.
- `read_adc(pin_id) -> int`
    Reads an ADC value.
- `set_pwm(pin_id, duty) -> dict`
    Sets a PWM duty cycle and returns the applied value.
- `get_pwm_config() -> dict`
    Returns PWM frequency (`freq`), resolution (`res`), and maximum duty value (`max_duty`).
- `set_pwm_config(freq, res) -> bool`
    Updates PWM frequency and resolution.
- `set_led_mode(mode) -> bool`
    Sets the LED operating mode (`status` or `manual`).
- `set_rgb(r, g, b, brightness) -> bool`
    Sets the color and brightness of the built-in RGB LED.
- `led_off() -> bool`
    Turns off the LED.
- `get_io_state() -> dict`
    Returns DIO, ADC, and PWM state in one response.
- `get_status() -> dict`
    Retrieves device uptime, heap memory, network status, etc.
- `command(cmd, **kwargs) -> dict`
    Low-level API for sending custom JSON commands.
- `help() -> list`
    Returns a list of commands supported by the device.
- `close() -> None`
    Closes the communication session.

### Exceptions

- `ESP32IOError` (Base)
    Base class for all exceptions
- `ESP32IOConnectionError`
    Raised for serial port or HTTP connection failures
- `ESP32IOTimeoutError`
    Raised when waiting for a response times out
- `ESP32IOProtocolError`
    Raised for invalid JSON or unexpected responses
- `ESP32IOCommandError`
    Raised when the device returns `status=error` (Command failure)

### Expected Firmware Commands

The client expects firmware that implements at least these commands:

- `ping`
- `read_di`
- `set_do`
- `read_adc`
- `set_pwm`
- `get_pwm_config`
- `set_pwm_config`
- `set_led_mode`
- `set_rgb`
- `get_io_state`
- `get_status`
- `help`

### Project Structure

```text
.
├── esp32io/
│   ├── __init__.py
│   ├── client.py        # ESP32IOSerial & ESP32IONet
│   ├── exceptions.py    # Unified exceptions
│   └── protocol.py      # JSON Protocol logic
├── examples/
│   ├── serial_example.py
│   └── wifi_example.py
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

### Firmware

This repository contains the Python package only.
Prepare separate ESP32-S3 firmware that follows the same JSON command protocol.

Firmware repository:  
https://github.com/noritama-lab/esp32io-firmware

### License

MIT License

Copyright (c) 2026 Noritama-Lab
