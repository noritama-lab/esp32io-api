from esp32io_net import ESP32S3IONet
import time
import requests # For catching network-specific exceptions

def main():
    print("=== ESP32IO Wi-Fi サンプル ===")

    # ESP32のIPアドレスに合わせてください
    # 例: esp = ESP32S3IONet("192.168.1.100", debug=True)
    IP_ADDRESS = "192.168.0.20" # ここを実際のIPアドレスに置き換えてください

    try:
        esp = ESP32S3IONet(IP_ADDRESS, debug=False)
    except requests.exceptions.RequestException as e:
        print("ERROR: ESP32 に接続できませんでした。")
        print("理由:", e)
        print("IPアドレスが正しいか、ESP32がネットワークに接続されているか確認してください。")
        return

    # ------------------------------------------------------------
    # 1. ping
    # ------------------------------------------------------------
    print("\n[1] ping テスト")
    print("ping =", esp.ping())

    # ------------------------------------------------------------
    # 2. DIO 出力
    # ------------------------------------------------------------
    print("\n[2] DIO 出力テスト")
    esp.set_do(0, 1)
    time.sleep(0.3)
    esp.set_do(0, 0)

    # ------------------------------------------------------------
    # 3. DIO 入力
    # ------------------------------------------------------------
    print("\n[3] DIO 入力テスト")
    dio0 = esp.read_di(0)
    print("dio0 =", dio0)

    # ------------------------------------------------------------
    # 4. ADC 読み取り
    # ------------------------------------------------------------
    print("\n[4] ADC 読み取りテスト")
    adc0 = esp.read_adc(0)
    print("adc0 =", adc0)

    # ------------------------------------------------------------
    # 5. PWM 出力
    # ------------------------------------------------------------
    print("\n[5] PWM 出力テスト")
    pwm_config = esp.get_pwm_config()
    print("pwm config =", pwm_config)
    esp.set_pwm(0, 128)
    time.sleep(0.5)
    esp.set_pwm(0, 0)

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

    print("\n=== 完了：ESP32IO の基本動作が確認できました (Wi-Fi) ===")


if __name__ == "__main__":
    main()