import asyncio

class AdvancedIO:
    async def stream_adc(self, pin_id: int, interval: float = 0.01):
        while True:
            value = await self.read_adc(pin_id)
            yield value
            await asyncio.sleep(interval)

    async def stream_pwm(self, pin_id: int, start: int, end: int, step: int = 1, interval: float = 0.01):
        """
        PWM duty を start → end まで一定間隔で変化させるストリーム。
        """
        if step == 0:
            raise ValueError("step must not be 0")

        duty = start
        direction = 1 if end >= start else -1
        step = abs(step) * direction

        while (direction == 1 and duty <= end) or (direction == -1 and duty >= end):
            await self.set_pwm(pin_id, duty)
            yield duty
            duty += step
            await asyncio.sleep(interval)

    async def stream_pwm_wave(self, pin_id: int, wave: list[int], interval: float = 0.01):
        """
        任意波形（duty の配列）を PWM に流すストリーム。
        例: [0, 10, 20, 30, ...] のような duty 値のリスト
        """
        for duty in wave:
            duty = max(0, min(255, int(duty)))  # 安全のためクリップ
            await self.set_pwm(pin_id, duty)
            yield duty
            await asyncio.sleep(interval)