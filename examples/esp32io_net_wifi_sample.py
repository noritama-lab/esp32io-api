from esp32io_net import ESP32S3IONet
import requests # For catching network-specific exceptions

def main():
    print("=== ESP32IO Wi-Fi サンプル ===")

    # ESP32のIPアドレスに合わせてください
    # 例: esp = ESP32S3IONet("172.20.10.14", debug=True)
    IP_ADDRESS = "172.20.10.14" # ここを実際のIPアドレスに置き換えてください

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