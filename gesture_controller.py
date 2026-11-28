from collections import deque
from math import hypot
from time import monotonic


class GestureController:
    """逐帧的掌心和指尖观测--->一次性游戏指令。"""

    SWIPE_WINDOW = 0.32
    SWIPE_DISTANCE = 0.12
    REST_DISTANCE = 0.035
    SMOOTHING = 0.55

    PINCH_OPEN = 0.60
    PINCH_CLOSE = 0.32
    OPEN_SECONDS = 0.15
    HOLD_SECONDS = 0.35
    ACTION_BY_STATE = {
        "READY": "START", "PLAYING": "PAUSE",
        "PAUSED": "START", "GAME_OVER": "RESTART",
    }

    def __init__(self):
        self._trail = deque()
        self._swipe_locked = False
        self._last_seen = None
        self._reset_pinch()
        self._pending = None
        self._action = None

    def _reset_pinch(self):
        self._armed = False
        self._open_since = None
        self._closed_since = None
        self.pinch_hint = "Open thumb and index"

    @staticmethod
    def pinch_ratio(points, width, height):
        def distance(a, b):
            return hypot((points[a].x - points[b].x) * width,
                         (points[a].y - points[b].y) * height)

        #侧转时掌宽投影会缩短，加入腕至中指根长度作为参考。
        scale = max(distance(5, 17), distance(0, 9))
        return distance(4, 8) / scale if scale >= 1 else None

    def _update_pinch(self, ratio, state, now):
        if not self._armed:
            if ratio < self.PINCH_OPEN:
                self._open_since = None
                return
            if self._open_since is None:
                self._open_since = now
            if now - self._open_since >= self.OPEN_SECONDS:
                self._armed = True
                self.pinch_hint = "Ready to pinch"
            return

        if ratio <= self.PINCH_CLOSE and self._closed_since is None:
            self._closed_since = now
        elif ratio > self.PINCH_CLOSE + 0.08:
            self._closed_since = None
        if self._closed_since is None:
            self.pinch_hint = "Ready to pinch"
            return

        progress = (now - self._closed_since) / self.HOLD_SECONDS
        if progress < 1:
            self.pinch_hint = f"Hold pinch: {int(100 * progress)}%"
            return
        self._action = self.ACTION_BY_STATE.get(state)
        self._reset_pinch()

    def _update_swipe(self, palm, now):
        while self._trail and now - self._trail[0][0] > self.SWIPE_WINDOW:
            self._trail.popleft()
        x, y = palm
        if self._trail:
            _, old_x, old_y = self._trail[-1]
            x = old_x + self.SMOOTHING * (x - old_x)
            y = old_y + self.SMOOTHING * (y - old_y)
        self._trail.append((now, x, y))
        if self._swipe_locked:
            #手停稳后才接受下一次挥动；连续同向划动只发一次。
            if len(self._trail) >= 2 and all(
                max(abs(x - px), abs(y - py)) < self.REST_DISTANCE
                for _, px, py in self._trail
            ):
                self._swipe_locked = False
            return
        _, start_x, start_y = self._trail[0]
        dx, dy = x - start_x, y - start_y
        major, minor = max(abs(dx), abs(dy)), min(abs(dx), abs(dy))
        if major < self.SWIPE_DISTANCE or major < 1.4 * minor:
            return
        if abs(dx) > abs(dy):
            self._pending = "RIGHT" if dx > 0 else "LEFT"
        else:
            self._pending = "DOWN" if dy > 0 else "UP"
        self._swipe_locked = True

    def update(self, palm, pinch_ratio=None, game_state=None):
        """每帧更新一次。仅传palm时仍可独立测试方向。"""
        self._pending = self._action = None
        now = monotonic()
        if palm is None or (self._last_seen is not None and now - self._last_seen > self.SWIPE_WINDOW):
            self._reset_pinch()
            self._trail.clear()
            self._swipe_locked = False
        self._last_seen = now if palm is not None else None
        if palm is None:
            return
        if pinch_ratio is None:
            self._reset_pinch()
        else:
            self._update_pinch(pinch_ratio, game_state, now)

        direction_only = game_state is None and pinch_ratio is None
        open_hand = self._armed and pinch_ratio is not None and pinch_ratio >= self.PINCH_OPEN
        if direction_only or (game_state == "PLAYING" and open_hand):
            self._update_swipe(palm, now)
        else:
            self._trail.clear()
            self._swipe_locked = False

    def get_direction(self):
        direction = self._pending
        self._pending = None
        return direction

    def get_action(self):
        action = self._action
        self._action = None
        return action
