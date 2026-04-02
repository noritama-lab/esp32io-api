# ESP32IO Python API

日本語 / English

---

## 日本語

ESP32IO は、ESP32-S3 を USB シリアル経由で Python から扱うための軽量クライアントです。
ESP32 側で JSON コマンドを受け取るファームウェアと組み合わせることで、デジタル入出力、ADC、PWM をシンプルな Python API で操作できます。

### 特徴

- USB シリアル経由で ESP32-S3 と通信
- JSON プロトコルを `ESP32IO` クラスが隠蔽
- `ping`、DIO、ADC、PWM、全体状態取得をサポート
- タイムアウト、プロトコル不整合、ESP32 側エラーを例外として統一処理
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

```python
from esp32io import ESP32IO

esp = ESP32IO("COM4", debug=False, recv_timeout=2.0)

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))

esp.set_do(0, 1)
esp.set_pwm(0, 128)

state = esp.get_io_state()
print(state)

esp.close()
```

サンプル実行:

```bash
py -m examples.esp32io_sample
```

### API 一覧

- `ESP32IO(port, baud=115200, timeout=2.0, debug=False, recv_timeout=None)`
    シリアルポートを開いて ESP32 に接続します。
- `ping() -> bool`
    疎通確認を行い、`pong` 応答を検証します。
- `read_di(pin_id) -> int`
    デジタル入力を 0 または 1 で返します。
- `set_do(pin_id, value) -> dict`
    デジタル出力を設定します。
- `read_adc(pin_id) -> int`
    ADC 値を返します。
- `set_pwm(pin_id, duty) -> dict`
    PWM デューティを設定します。
- `get_io_state() -> dict`
    DIO、ADC、PWM の状態をまとめて返します。
- `command(cmd, **kwargs) -> dict`
    任意の JSON コマンドを送る低レベル API です。
- `close() -> None`
    シリアルポートを閉じます。

### 例外

- `ESP32IOError`
    ESP32 が `status=error` を返した場合
- `ESP32IOTimeoutError`
    応答待ちがタイムアウトした場合
- `ESP32IOProtocolError`
    JSON 不正や期待しない応答を受けた場合

### 想定コマンド

このクライアントは、少なくとも以下のコマンドを実装したファームウェアを前提にしています。

- `ping`
- `read_di`
- `set_do`
- `read_adc`
- `set_pwm`
- `get_io_state`

### プロジェクト構成

```text
.
├── esp32io/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   └── protocol.py
├── examples/
│   └── esp32io_sample.py
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

ESP32IO is a lightweight Python client for controlling an ESP32-S3 over USB serial.
When paired with firmware that accepts JSON commands, it provides a small and practical API for digital I/O, ADC, and PWM control.

### Features

- USB serial communication with ESP32-S3
- JSON protocol hidden behind the `ESP32IO` client
- Support for `ping`, DIO, ADC, PWM, and full I/O state reads
- Unified exception handling for device errors, timeouts, and protocol issues
- Includes a low-level `command()` API for custom commands

### Requirements

- Python 3.8+
- `pyserial>=3.5`
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

```python
from esp32io import ESP32IO

esp = ESP32IO("COM4", debug=False, recv_timeout=2.0)

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))

esp.set_do(0, 1)
esp.set_pwm(0, 128)

state = esp.get_io_state()
print(state)

esp.close()
```

Run the sample:

```bash
py -m examples.esp32io_sample
```

### API Summary

- `ESP32IO(port, baud=115200, timeout=2.0, debug=False, recv_timeout=None)`
    Opens the serial port and prepares the client.
- `ping() -> bool`
    Verifies connectivity by checking for a `pong` response.
- `read_di(pin_id) -> int`
    Reads a digital input and returns `0` or `1`.
- `set_do(pin_id, value) -> dict`
    Sets a digital output.
- `read_adc(pin_id) -> int`
    Reads an ADC value.
- `set_pwm(pin_id, duty) -> dict`
    Sets a PWM duty cycle.
- `get_io_state() -> dict`
    Returns DIO, ADC, and PWM state in one response.
- `command(cmd, **kwargs) -> dict`
    Low-level API for sending custom JSON commands.
- `close() -> None`
    Closes the serial port.

### Exceptions

- `ESP32IOError`
    Raised when the device returns `status=error`
- `ESP32IOTimeoutError`
    Raised when waiting for a response times out
- `ESP32IOProtocolError`
    Raised for invalid JSON or unexpected responses

### Expected Firmware Commands

The client expects firmware that implements at least these commands:

- `ping`
- `read_di`
- `set_do`
- `read_adc`
- `set_pwm`
- `get_io_state`

### Project Structure

```text
.
├── esp32io/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   └── protocol.py
├── examples/
│   └── esp32io_sample.py
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
