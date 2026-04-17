from esp32io_net import ESP32S3IOSerial
import serial

def main():
    print("=== ESP32IO シリアルサンプル ===")

    try:
        # "COM4" の部分は、ESP32-S3 のシリアルポート番号に合わせてください
        esp = ESP32S3IOSerial("COM4", debug=False)
    except serial.SerialException as e:
        print("ERROR: ESP32 に接続できませんでした。")
        print("理由:", e)
        print("COM ポートが正しいか確認してください。")
        return

    # ------------------------------------------------------------
    # 1. ping
    # ------------------------------------------------------------
    print("\n[1] ping テスト")
    print("ping =", esp.ping())

    # ------------------------------------------------------------
    # 6. 全 I/O 状態取得
    # ------------------------------------------------------------
    print("\n[6] 全 I/O 状態取得")
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
    print("\n=== 完了：ESP32IO の基本動作が確認できました (シリアル) ===")


if __name__ == "__main__":
    main()