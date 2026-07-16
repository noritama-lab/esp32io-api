# ESP32IO Python API

> **⚠️ 開発終了 / Archived — Migrated to MQTT**
>
> このリポジトリの開発は終了しました。後継の MQTT 版に移行してください。
> This repository is no longer maintained. Development has moved to the MQTT-based successor.
>
> 👉 https://github.com/noritama-lab/esp32io-mqtt-api

ESP32IO is a lightweight Python client for controlling ESP32-S3 devices over USB serial or Wi-Fi (HTTP).

日本語 / English

---

## 日本語

> **本リポジトリはアーカイブされ、開発を終了しました。**
> USB シリアル / Wi-Fi (HTTP) 通信の Python API は今後更新されません。
> 今後は MQTT 版クライアントをご利用ください。
>
> 移行先: https://github.com/noritama-lab/esp32io-mqtt-api

ESP32IO は、ESP32-S3 を **USB シリアル** または **Wi-Fi (HTTP)** 経由で制御するための軽量 Python クライアントです。  
ESP32 側で JSON コマンドを受け取るファームウェアと組み合わせることで、**DIO / ADC / PWM / 内蔵 RGB LED / I2C / OLED** を統一 API で扱えます。

---

## 特徴

- USB シリアル & Wi-Fi (HTTP) の両通信方式を単一パッケージでサポート  
- JSON プロトコルを `ESP32S3IOSerial` / `ESP32S3IONet` が抽象化  
- DIO、ADC、PWM、RGB LED、システム状態取得に対応  
- I2C スキャン、リード/ライト、BME280 などのセンサー一括取得、OLED 表示をサポート  
- PWM 周波数・分解能の取得/更新に対応  
- 通信エラー・タイムアウト・プロトコル不整合・デバイスエラーなど統一例外を定義  
- 任意 JSON を送れる低レベル API `command()` を提供  

---

## 動作環境

- Python 3.8 以上  
- `pyserial>=3.5`  
- `requests>=2.25.0`  
- 対応する ESP32-S3 ファームウェア  

---

## インストール

```bash
pip install esp32io
```

---

## クイックスタート

### USB シリアル接続

```python
from esp32io import ESP32S3IOSerial

esp = ESP32S3IOSerial("COM4", debug=False)

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))
print("pwm config =", esp.get_pwm_config())

esp.set_do(0, 1)
esp.set_pwm(0, 128)

print(esp.get_io_state())

esp.close()
```

### Wi-Fi (HTTP) 接続

```python
from esp32io import ESP32S3IONet

esp = ESP32S3IONet("192.168.1.10", debug=False)

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))
print("pwm config =", esp.get_pwm_config())

esp.set_do(0, 1)
esp.set_pwm(0, 128)

print(esp.get_io_state())

esp.close()
```

サンプル実行:

```bash
py -m examples.serial_example
```

---

## API 一覧（主要メソッド）

- `ESP32S3IOSerial(port, baud=115200, timeout=2.0, debug=False, recv_timeout=None)`  
- `ESP32S3IONet(address, timeout=2.0, debug=False)`  
- `ping()`  
- `read_di(pin_id)` / `set_do(pin_id, value)`  
- `read_adc(pin_id)`  
- `set_pwm(pin_id, duty)`  
- `get_pwm_config()` / `set_pwm_config(freq, res)`  
- `set_led_mode(mode)` / `set_rgb(r, g, b, brightness)` / `led_off()` / `get_led_state()`  
- `i2c_scan()` / `i2c_read(addr, length)` / `i2c_write(addr, data)`  
- `get_sensors()`  
- `set_oled(text, x, y, size, clear)`  
- `get_io_state()` / `get_status()`  
- `command(cmd, **kwargs)`  
- `help()`  
- `close()`  

---

## 例外

- `ESP32S3IOError`（基底クラス）  
- `ESP32S3IONetworkError` / `ESP32S3IOSerialError`  
- `ESP32S3IOProtocolError`  
- `ESP32S3IODeviceError`  

---

## 必要なファームウェアコマンド

- `ping`  
- `read_di` / `set_do`  
- `read_adc`  
- `set_pwm` / `get_pwm_config` / `set_pwm_config`  
- `led_off` / `get_led_state` / `set_led_mode` / `set_rgb`  
- `get_io_state`  
- `i2c_scan` / `i2c_read` / `i2c_write`  
- `get_sensors`  
- `set_oled`  
- `get_status`  
- `help`  

---

## プロジェクト構成

```text
.
├── esp32io/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   └── protocol.py
├── examples/
│   ├── serial_example.py
│   ├── i2c_example.py
│   └── wifi_example.py
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md
```

---

## ファームウェア

このパッケージには ESP32 側ファームウェアは含まれていません。  
以下の JSON プロトコル対応ファームウェアを使用してください。

https://github.com/noritama-lab/esp32io-firmware

---

## ライセンス

MIT License  
Copyright (c) 2026 Noritama-Lab

---

## English

> **This repository is archived and no longer maintained.**
> The USB serial / Wi-Fi (HTTP) Python API will not receive further updates.
> Please migrate to the MQTT-based client instead.
>
> Migration target: https://github.com/noritama-lab/esp32io-mqtt-api

ESP32IO is a lightweight Python client for controlling an ESP32-S3 over **USB serial** or **Wi-Fi (HTTP)**.  
When paired with firmware that accepts JSON commands, it provides a unified API for **DIO, ADC, PWM, RGB LED, I2C, sensors, and OLED control**.

### Features

- Unified support for USB serial and HTTP communication  
- JSON protocol abstracted by `ESP32S3IOSerial` and `ESP32S3IONet`  
- Supports DIO, ADC, PWM, RGB LED, and full I/O state reads  
- I2C scanning, raw read/write, sensor batch reads, and OLED control  
- PWM frequency/resolution read & update  
- Unified exceptions for communication, protocol, and device errors  
- Low-level `command()` API for custom JSON commands  

### Requirements

- Python 3.8+  
- `pyserial>=3.5`  
- `requests>=2.25.0`  
- Compatible ESP32-S3 firmware  

### Installation

```bash
pip install esp32io
```

### Quick Start

(USB / Wi-Fi examples remain the same as Japanese section)

### License

MIT License  
Copyright (c) 2026 Noritama-Lab
