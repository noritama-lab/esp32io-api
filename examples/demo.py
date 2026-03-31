from esp32io import ESP32IO
import time

io = ESP32IO("COM3")

io.set_do(0, True)
time.sleep(2)
io.set_do(0, False)