from esp32io import ESP32IO
import time

def measure(label, func, *args, **kwargs):
    """コマンドの応答時間を計測して表示する"""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000
    print(f"{label}: {elapsed_ms:.2f} ms")
    return result


def main():
    print("=== ESP32IO 初回テスト（応答速度つき） ===")

    esp = ESP32IO("COM5", debug=False)

    # ------------------------------------------------------------
    # 1. DIO 出力
    # ------------------------------------------------------------
    print("\n[1] DIO 出力テスト")
    measure("write_dio(0,1)", esp.write_dio, 0, 1)
    time.sleep(0.3)
    measure("write_dio(0,0)", esp.write_dio, 0, 0)

    # ------------------------------------------------------------
    # 2. DIO 入力
    # ------------------------------------------------------------
    print("\n[2] DIO 入力テスト")
    dio0 = measure("read_dio(0)", esp.read_dio, 0)
    print("dio0 =", dio0)

    # ------------------------------------------------------------
    # 3. ADC 読み取り
    # ------------------------------------------------------------
    print("\n[3] ADC 読み取りテスト")
    adc0 = measure("read_adc(0)", esp.read_adc, 0)
    print("adc0 =", adc0)

    # ------------------------------------------------------------
    # 4. PWM 出力
    # ------------------------------------------------------------
    print("\n[4] PWM 出力テスト")
    measure("set_pwm(0,128)", esp.set_pwm, 0, 128)
    time.sleep(0.5)
    measure("set_pwm(0,0)", esp.set_pwm, 0, 0)

    # ------------------------------------------------------------
    # 5. 全 I/O 状態取得（変数として扱う例）
    # ------------------------------------------------------------
    print("\n[5] 全 I/O 状態取得")
    state = measure("get_io_state()", esp.get_io_state)

    # state は dict として扱える
    dio_in  = state["dio_in"]
    dio_out = state["dio_out"]
    adc     = state["adc"]
    pwm     = state["pwm"]

    print("dio_in  =", dio_in)
    print("dio_out =", dio_out)
    print("adc     =", adc)
    print("pwm     =", pwm)

    # 個別アクセス例
    print("dio_in[0] =", dio_in[0])
    print("adc[1]    =", adc[1])
    print("pwm[0]    =", pwm[0])

    esp.close()
    print("\n=== 完了：ESP32IO の基本動作と応答速度が確認できました ===")


if __name__ == "__main__":
    main()