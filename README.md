# ESP32IO Python API  
日本語 / English

---

## 🇯🇵 ESP32IO Python API

ESP32IO は、ESP32‑S3 を USB で接続するだけで I/O デバイスとして扱える Python API です。  
ESP32‑S3 側のファームウェアと組み合わせることで、JSON コマンドを意識せずに Python から I/O を安全かつ直感的に操作できます。

### 特徴

- USB シリアル経由で I/O を制御  
- JSON ベースの通信プロトコルを API 内部で抽象化  
- ADC / PWM / DIO（入力・出力）を Python から簡単に操作  
- エラー処理・タイムアウト処理を統一  
- 全 I/O 状態を取得できる get_io_state()  
- 初回動作確認用のサンプルコード付き  

### リポジトリ構成

```
esp32io-api/
├── esp32io/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   └── protocol.py
├── samples.py
├── LICENSE
└── README.md
```

### 主なメソッド

- read_dio(pin_id) — デジタル入力  
- write_dio(pin_id, value) — デジタル出力  
- read_adc(pin_id) — ADC 読み取り  
- set_pwm(pin_id, duty) — PWM 出力  
- get_io_state() — 全 I/O 状態の取得  

### 使用例：ADC の値で LED の明るさを制御

```python
from esp32io import ESP32IO
import time
import serial

def main():
    try:
        esp = ESP32IO("COM3", debug=False)
        print("ESP32 に接続しました。")

        while True:
            adc_value = esp.read_adc(0)
            duty = int(adc_value / 4095 * 255)
            esp.set_pwm(0, duty)

            print(f"ADC={adc_value}, PWM duty={duty}")
            time.sleep(0.05)

    except serial.SerialException as e:
        print("ERROR: ESP32 に接続できませんでした。")
        print("理由:", e)

    finally:
        try:
            esp.set_pwm(0, 0)
        except:
            pass
        print("終了しました。PWM を停止しました。")

if __name__ == "__main__":
    main()
```

### ESP32‑S3 ファームウェア

この API は、以下のファームウェアと連携して動作します：  
https://github.com/noritama-lab/esp32io-firmware

### ライセンス

MIT License  
Copyright (c) 2026 Noritama-Lab

---

## 🇺🇸 ESP32IO Python API

ESP32IO is a Python API that turns an ESP32‑S3 into a USB‑connected I/O device.  
With the corresponding firmware, you can control I/O safely and intuitively without handling JSON commands directly.

### Features

- I/O control over USB serial  
- JSON protocol fully abstracted inside the API  
- Easy access to ADC / PWM / DIO (input/output)  
- Unified error handling and timeout management  
- get_io_state() for full I/O monitoring  
- Includes sample code for quick testing  

### Repository Structure

```
esp32io-api/
├── esp32io/
│   ├── __init__.py
│   ├── client.py
│   ├── exceptions.py
│   └── protocol.py
├── samples.py
├── LICENSE
└── README.md
```

### Main Methods

- read_dio(pin_id) — Digital input  
- write_dio(pin_id, value) — Digital output  
- read_adc(pin_id) — Read ADC  
- set_pwm(pin_id, duty) — PWM output  
- get_io_state() — Get all I/O states  

### Example: Control LED brightness using ADC input

```python
from esp32io import ESP32IO
import time
import serial

def main():
    try:
        esp = ESP32IO("COM3", debug=False)
        print("Connected to ESP32.")

        while True:
            adc_value = esp.read_adc(0)
            duty = int(adc_value / 4095 * 255)
            esp.set_pwm(0, duty)

            print(f"ADC={adc_value}, PWM duty={duty}")
            time.sleep(0.05)

    except serial.SerialException as e:
        print("ERROR: Could not connect to ESP32.")
        print("Reason:", e)

    finally:
        try:
            esp.set_pwm(0, 0)
        except:
            pass
        print("Finished. PWM stopped.")

if __name__ == "__main__":
    main()
```

### ESP32‑S3 Firmware

This API works with the following firmware:  
https://github.com/noritama-lab/esp32io-firmware

### License

MIT License  
Copyright (c) 2026 Noritama-Lab
