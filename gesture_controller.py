from time import monotonic


class GestureController:
    """归一化掌心坐标--->一次性的转向指令"""

    SMOOTHING = 0.45
    DEAD_ZONE = 0.06
    COOLDOWN_SECONDS = 0.25

    def __init__(self):
        self._smoothed = None
        self._anchor = None
        self._ready_at = 0.0
        self._pending = None

    def update(self, palm):
        """每帧调用一次。palm是(x, y)；丢失手部时传None"""
        self._pending = None
        if palm is None:
            self._smoothed = None
            self._anchor = None
            return

        if self._smoothed is None:
            self._smoothed = self._anchor = palm
            return

        old_x, old_y = self._smoothed
        x = old_x + self.SMOOTHING * (palm[0] - old_x)
        y = old_y + self.SMOOTHING * (palm[1] - old_y)
        self._smoothed = (x, y)

        now = monotonic()
        if now < self._ready_at:
            self._anchor = (x, y)
            return

        dx = x - self._anchor[0]
        dy = y - self._anchor[1]
        if max(abs(dx), abs(dy)) < self.DEAD_ZONE:
            return

        if abs(dx) >= abs(dy):
            self._pending = "RIGHT" if dx > 0 else "LEFT"
        else:
            self._pending = "DOWN" if dy > 0 else "UP"

        self._anchor = (x, y)
        self._ready_at = now + self.COOLDOWN_SECONDS

    def get_direction(self):
        """返回本帧的方向；没有新指令则返回None。"""
        direction = self._pending
        self._pending = None
        return direction
