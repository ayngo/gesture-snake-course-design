# -*- coding: utf-8 -*-
"""
贪吃蛇核心逻辑模块（成员 B）

职责：
- 蛇的数据模型：蛇身坐标、当前方向、分数、游戏状态
- 移动、吃食物增长、撞墙判定、撞自己判定
- 食物生成（避开蛇身）、计分、难度切换

边界：
- 本模块只做纯逻辑，不依赖 pygame、不依赖摄像头、不做任何渲染。
- 其他模块通过下面列出的接口调用本模块；接口签名冻结后不私自改动，
  需要改动时先发群消息通知队长并更新接口文档。

对外接口（S0 冻结）：
- SnakeGame(width=20, height=20)：创建一局游戏。
- update(direction)：推进一帧。direction 为 'UP' / 'DOWN' / 'LEFT' / 'RIGHT' / None；
  None 表示沿当前方向继续走；与当前方向相反的 180° 掉头方向必须被忽略。
- get_state()：返回字典，字段：
    snake   : [(x, y), ...]，列表第 0 项是蛇头
    food    : (x, y)
    score   : int
    status  : 'ready' / 'running' / 'paused' / 'over'
- reset()：清局重开，蛇身、食物、分数、状态回到初始值。
- set_difficulty(level)：'easy' / 'normal' / 'hard'；只改变 tick 间隔，不改移动逻辑。

一次 update 的执行顺序（伪代码）：
1. 校验方向：若与当前方向相反，忽略该方向；若为 None，沿用当前方向。
2. 用当前方向算出新蛇头坐标。
3. 撞墙判定：新蛇头超出网格边界 -> status = 'over'，结束本帧。
4. 撞自己判定：新蛇头落在蛇身里 -> status = 'over'，结束本帧。
5. 吃食物判定：新蛇头与食物坐标重合 -> 长度 +1、分数 +10、重新生成食物。
6. 没吃到食物 -> 去掉蛇尾，蛇身长度不变。
"""
import random

DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0),
}

# 反方向对照，用于禁止 180° 掉头
OPPOSITE = {
    'UP': 'DOWN',
    'DOWN': 'UP',
    'LEFT': 'RIGHT',
    'RIGHT': 'LEFT',
}

DIFFICULTY = {
    'easy': 150,
    'normal': 100,
    'hard': 70,
}


class SnakeGame:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height

        center_x = width // 2
        center_y = height // 2
        self.snake = [
            (center_x, center_y),       
            (center_x - 1, center_y),   
            (center_x - 2, center_y),   
        ]

        self.direction = 'RIGHT'
        self.score = 0
        self.status = 'ready'
        self.difficulty = 'normal'
        self.tick_interval = DIFFICULTY['normal']
        self.food = self._place_food()

    def reset(self):
        """清局重开：蛇身、方向、分数、状态、难度、食物回到初始值。"""
        center_x = self.width // 2
        center_y = self.height // 2
        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = 'RIGHT'
        self.score = 0
        self.status = 'ready'
        self.difficulty = 'normal'
        self.tick_interval = DIFFICULTY['normal']
        self.food = self._place_food()

    def set_difficulty(self, level):
        """切换难度：只记录档位和间隔时间，蛇的移动逻辑不变。"""
        if level in DIFFICULTY:
            self.difficulty = level
            self.tick_interval = DIFFICULTY[level]

    def _place_food(self):
        """在不在蛇身上的空格子里随机放一个食物。"""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def update(self, direction=None):
        """推进一帧：方向校验、移动、撞墙、撞自己、吃食物增长与计分。"""
        # 方向校验：None 沿用当前方向；与当前方向相反的 180° 掉头直接忽略
        if direction is not None:
            if direction != OPPOSITE[self.direction]:
                self.direction = direction

        # 从方向表里取坐标增量，算出新蛇头
        dx, dy = DIRECTIONS[self.direction]
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        # 撞墙判定：横坐标或纵坐标越出网格边界，游戏结束，本帧不再移动
        if new_head[0] < 0 or new_head[0] >= self.width:
            self.status = 'over'
            return
        if new_head[1] < 0 or new_head[1] >= self.height:
            self.status = 'over'
            return

        # 先判断这一帧会不会吃到食物，决定尾巴那一格算不算身体
        will_eat = (new_head == self.food)
        if will_eat:
            body_to_check = self.snake          # 吃到食物尾巴保留，整节身体都算
        else:
            body_to_check = self.snake[:-1]      # 没吃到食物尾巴会移走，排除尾格

        # 撞自己判定：新蛇头落在身体上，游戏结束
        if new_head in body_to_check:
            self.status = 'over'
            return

        # 新蛇头插到列表最前面
        self.snake.insert(0, new_head)

        if will_eat:
            # 吃到食物：不删蛇尾（长度 +1），分数 +10，重新生成食物
            self.score += 10
            self.food = self._place_food()
        else:
            # 没吃到食物：删掉旧蛇尾，长度不变
            self.snake.pop()

    def get_state(self):
        """把当前游戏状态交给界面模块渲染，不改内部数据。"""
        return {
            'snake': list(self.snake),
            'food': self.food,
            'score': self.score,
            'status': self.status,
        }
