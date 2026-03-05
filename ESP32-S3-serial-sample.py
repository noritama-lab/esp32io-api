import serial, json

# "COM5" の部分は、Arduino IDE で書き込みに使ったポート番号に合わせてください
ser = serial.Serial("COM5", 115200, timeout=1)

# ESP32-S3 に ping コマンドを送信
ser.write(b'{"cmd":"ping"}\n')

# 1 行の JSON レスポンスを受信
line = ser.readline().decode().strip()

# JSON を Python の辞書に変換して表示
print(json.loads(line))