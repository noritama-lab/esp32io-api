import time
from esp32io import ESP32S3IONet

def main():
    # ESP32のIPアドレスを設定してください
    # シリアル接続の場合は ESP32S3IOSerial("COMx") を使用します
    IP_ADDRESS = "192.168.1.10"
    
    print(f"Connecting to {IP_ADDRESS}...")
    try:
        with ESP32S3IONet(IP_ADDRESS, debug=False) as io:
            # 1. I2Cバスのスキャン
            print("\n--- I2C Scan ---")
            addresses = io.i2c_scan()
            print(f"Found devices at: {[hex(addr) for addr in addresses]}")

            # 2. センサーデータの一括取得 (BME280, MPU6050, VL53L0X)
            print("\n--- Sensor Data ---")
            sensors = io.get_sensors()
            print(f"Raw sensors data: {sensors}")

            # 3. OLEDディスプレイへの表示
            # x, y 座標指定と clear フラグを組み合わせてレイアウトします
            print("\n--- Updating OLED Display ---")
            io.set_oled("I2C MONITOR", x=20, y=0, size=1, clear=True)
            
            if "bme280" in sensors:
                s = sensors["bme280"]
                io.set_oled(f"Temp: {s['temp']:.1f} C", x=0, y=16, clear=False)
                io.set_oled(f"Hum:  {s['hum']:.1f} %", x=0, y=26, clear=False)

            if "vl53l0x" in sensors:
                dist = sensors["vl53l0x"].get("distance", 0)
                io.set_oled(f"Dist: {dist} mm", x=0, y=40, clear=False)

            # 4. 生のI2C読み書き例 (MPU6050のWHO_AM_Iレジスタ 0x75 を確認)
            if 0x68 in addresses:
                # 0x75レジスタを指定して書き込み
                io.i2c_write(0x68, [0x75])
                # 1バイト読み取り
                who_am_i = io.i2c_read(0x68, 1)
                if who_am_i:
                    print(f"MPU6050 WHO_AM_I: {hex(who_am_i[0])}")

            print("\nOLED display updated with sensor values.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()