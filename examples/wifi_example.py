# Wi-Fi (HTTP) 接続
from esp32io import ESP32S3IONet
# 192.168.1.10はESP32のIPアドレスに置き換えてください。
esp = ESP32S3IONet("172.20.10.14", debug=False)

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))
print("pwm config =", esp.get_pwm_config())

esp.set_do(0, 1)
esp.set_pwm(0, 128)

state = esp.get_io_state()
print(state)

esp.close()  # 通信の終了