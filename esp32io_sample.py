from esp32io import ESP32IO
import time
import serial

def main():
    print("=== ESP32IO 初回テスト ===")

    try:
        esp = ESP32IO("COM3", debug=False)
    except serial.SerialException as e:
        print("ERROR: ESP32 に接続できませんでした。")
        print("理由:", e)
        print("COM ポートが正しいか確認してください。")
        return

    # ------------------------------------------------------------
    # 1. DIO 出力
    # ------------------------------------------------------------
    print("\n[1] DIO 出力テスト")
    esp.write_dio(0, 1)
    time.sleep(0.3)
    esp.write_dio(0, 0)

    # ------------------------------------------------------------
    # 2. DIO 入力
    # ------------------------------------------------------------
    print("\n[2] DIO 入力テスト")
    dio0 = esp.read_dio(0)
    print("dio0 =", dio0)

    # ------------------------------------------------------------
    # 3. ADC 読み取り
    # ------------------------------------------------------------
    print("\n[3] ADC 読み取りテスト")
    adc0 = esp.read_adc(0)
    print("adc0 =", adc0)

    # ------------------------------------------------------------
    # 4. PWM 出力
    # ------------------------------------------------------------
    print("\n[4] PWM 出力テスト")
    esp.set_pwm(0, 128)
    time.sleep(0.5)
    esp.set_pwm(0, 0)

    # ------------------------------------------------------------
    # 5. 全 I/O 状態取得
    # ------------------------------------------------------------
    print("\n[5] 全 I/O 状態取得")
    state = esp.get_io_state()

    dio_in  = state["dio_in"]
    dio_out = state["dio_out"]
    adc     = state["adc"]
    pwm     = state["pwm"]

    print("dio_in  =", dio_in)
    print("dio_out =", dio_out)
    print("adc     =", adc)
    print("pwm     =", pwm)

    print("dio_in[0] =", dio_in[0])
    print("adc[1]    =", adc[1])
    print("pwm[0]    =", pwm[0])

    esp.close()
    print("\n=== 完了：ESP32IO の基本動作が確認できました ===")


if __name__ == "__main__":
    main()
