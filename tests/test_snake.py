# -*- coding: utf-8 -*-
"""贪吃蛇核心逻辑自测脚本（成员 B）。

覆盖用例：
1. 走一步后蛇头坐标正确，蛇身整体平移。
2. 吃到食物后长度 +1、分数 +10，新食物不在蛇身上。
3. 撞墙后状态变为 'over'。
4. 撞到自己后状态变为 'over'。
5. 初始食物不在蛇身上。
6. 与当前方向相反的 180° 方向被忽略。

运行方式：在项目根目录执行  python tests/test_snake.py
"""

import os
import sys

# 让脚本在 tests/ 目录下也能找到根目录里的 snake_game 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from snake_game import SnakeGame


def check(name, condition):
    """一条用例的验收：通过打印 OK，不通过直接报错。"""
    if condition:
        print(f"OK: {name}")
    else:
        raise AssertionError(f"FAIL: {name}")


# 1. 走一步：初始蛇头 (10, 10)，朝右走一步到 (11, 10)，长度仍为 3
g = SnakeGame()
g.update('RIGHT')
state = g.get_state()
check("走一步蛇头右移、长度不变", state['snake'][0] == (11, 10) and len(state['snake']) == 3)

# 2. 吃食物：把食物放到蛇头正前方，走一步后长度 +1、分数 +10
g = SnakeGame()
g.food = (11, 10)
g.update('RIGHT')
state = g.get_state()
check("吃食物长度 +1", len(state['snake']) == 4)
check("吃食物分数 +10", state['score'] == 10)
check("新食物不在蛇身上", state['food'] not in state['snake'])

# 3. 撞墙：一直朝右走，第 10 步越出右边界
g = SnakeGame()
for _ in range(10):
    g.update('RIGHT')
check("撞右墙结束", g.get_state()['status'] == 'over')

# 4. 撞自己：手工摆出身体格，蛇头向下钻进身体
g = SnakeGame()
g.snake = [(2, 2), (2, 3), (1, 3), (1, 2)]
g.direction = 'DOWN'
g.food = (15, 15)
g.update()
check("撞到自己结束", g.get_state()['status'] == 'over')

# 5. 初始食物不在蛇身上
g = SnakeGame()
check("初始食物不在蛇身上", g.get_state()['food'] not in g.get_state()['snake'])

# 6. 掉头防护：初始朝右，传入 LEFT 应被忽略，继续向右走
g = SnakeGame()
g.update('LEFT')
check("180° 反向被忽略", g.direction == 'RIGHT' and g.get_state()['snake'][0] == (11, 10))

print("\n全部用例通过。")
