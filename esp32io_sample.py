import asyncio
import time
from esp32io import ESP32IO, ESP32IOError


async def main():
    io = ESP32IO(port="COM5", baudrate=115200)

    try:
        await io.start()

        print("\n--- PWM Waveform Streaming (200 samples) ---")

        # 三角波
        wave = list(range(0, 256)) + list(range(255, -1, -1))

        # 計測開始
        t0 = time.perf_counter()

        sample_count = 0
        async for duty in io.stream_pwm_wave(pin_id=1, wave=wave, interval=0.1):
            sample_count += 1
            if sample_count >= 200:
                break

        # 計測終了
        t1 = time.perf_counter()

        elapsed = t1 - t0
        print(f"200 samples took: {elapsed:.4f} sec")
        print(f"Average per sample: {elapsed / 200 * 1000:.3f} ms")

    except ESP32IOError as e:
        print("ESP32IO error:", e)

    finally:
        await io.close()


if __name__ == "__main__":
    asyncio.run(main())