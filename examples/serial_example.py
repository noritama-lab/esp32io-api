# USB シリアル接続
from esp32io import ESP32S3IOSerial
# COM4は環境によって異なります。適切なポートを指定してください。
esp = ESP32S3IOSerial("COM4", debug=False)

print("ping =", esp.ping())
print("di0 =", esp.read_di(0))
print("adc0 =", esp.read_adc(0))
print("pwm config =", esp.get_pwm_config())

esp.set_do(0, 1)
esp.set_pwm(0, 128)

state = esp.get_io_state()
print(state)

esp.close()  # 通信の終了