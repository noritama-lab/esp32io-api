import asyncio
import math
from esp32io import ESP32IO, ESP32IOError


async def main():
    io = ESP32IO(port="COM5", baudrate=115200)

    try:
        print("Connecting...")
        await io.start()
        print("Connected!")

        # -----------------------------
        # Basic commands
        # -----------------------------
        print("\n--- DIO ---")
        await io.write_dio(pin_id=2, value=1)
        dio_value = await io.read_dio(pin_id=2)
        print(f"DIO read: {dio_value}")

        print("\n--- ADC ---")
        adc_value = await io.read_adc(pin_id=1)
        print(f"ADC read: {adc_value}")

        print("\n--- PWM ---")
        await io.set_pwm(pin_id=1, duty=128)
        print("PWM set to 128")

        print("\n--- Status ---")
        status = await io.get_status()
        print(f"Uptime: {status.uptime_ms} ms, Free heap: {status.free_heap}")

        print("\n--- IO State ---")
        io_state = await io.get_io_state()
        print("DIO IN :", io_state.dio_in)
        print("DIO OUT:", io_state.dio_out)
        print("ADC    :", io_state.adc)
        print("PWM    :", io_state.pwm)

        print("\n--- Ping ---")
        pong = await io.ping()
        print(f"Ping response: {pong.status}")

        # -----------------------------
        # High-level API: ADC streaming
        # -----------------------------
        print("\n--- ADC Streaming (5 samples) ---")
        count = 0
        async for value in io.stream_adc(pin_id=1, interval=0.05):
            print("ADC:", value)
            count += 1
            if count >= 5:
                break

        # -----------------------------
        # High-level API: PWM waveform streaming
        # -----------------------------
        print("\n--- PWM Waveform Streaming (Triangle Wave) ---")

        # 三角波を生成
        wave = list(range(0, 256)) + list(range(255, -1, -1))

        # PWM に流す
        sample_count = 0
        async for duty in io.stream_pwm_wave(pin_id=1, wave=wave, interval=0.005):
            print("PWM duty:", duty)
            sample_count += 1
            if sample_count >= 50:  # デモなので 50 サンプルで終了
                break

    except ESP32IOError as e:
        print("ESP32IO error:", e)

    finally:
        print("Closing...")
        await io.close()
        print("Closed.")


if __name__ == "__main__":
    asyncio.run(main())