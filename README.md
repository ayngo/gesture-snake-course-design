# 手势控制贪吃蛇

基于 **MediaPipe Hands** 的 Python 课程设计项目：玩家用手在摄像头前上下左右移动控制贪吃蛇，支持键盘回退、暂停/重开、难度与计分。

## 项目结构

```text
gesture-snake-course-design/
├── main.py                 # 主循环、状态机、模块集成（队长）
├── gesture_controller.py   # MediaPipe 手势识别与方向映射（成员 A）
├── snake_game.py           # 贪吃蛇核心逻辑（成员 B）
├── ui.py                   # Pygame 界面与渲染（成员 C）
├── assets/                 # 图片、音效等资源
├── tests/                  # 测试用例与自测脚本
├── docs/                   # 实验报告、提交文档模板、AI 使用说明
├── requirements.txt        # 依赖列表
└── README.md
```

> 具体分工与阶段规划见 `贪吃蛇课程设计_四人小组规划.md`。

## 环境安装

建议使用 Python 3.10 / 3.11（MediaPipe 对 3.12 支持不稳定）。

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

`requirements.txt` 至少包含：

```text
mediapipe
opencv-python
pygame
numpy
```

## 运行

```bash
python main.py
```

## 操作方式

| 操作 | 手势 | 键盘 |
|---|---|---|
| 开始 / 暂停 | 拇指与食指捏合 | 空格 |
| 上 | 手掌向上移动 | ↑ / W |
| 下 | 手掌向下移动 | ↓ / S |
| 左 | 手掌向左移动 | ← / A |
| 右 | 手掌向右移动 | → / D |
| 重开 | 捏合（结束后） | R |

手势识别结果会显示在摄像头小窗中，包含关键点与“已检测到手 / 未检测到手”状态提示。为减少误判，代码中使用了指数平滑、位移死区、指令冷却，并禁止 180° 掉头。

## Git 协作约定

- 主分支：`main`（只放可运行版本）
- 功能分支：`feature/hand`（成员 A）、`feature/game`（成员 B）、`feature/ui`（成员 C）
- 提交格式：`feat(hand): 添加掌心平滑`、`fix(game): 修复食物生成在蛇身上`
- 每个功能分支通过合并请求合入 `main`，至少队长 + 一位成员确认

## AI 辅助说明

本项目允许使用 AI 工具辅助编码，但遵循：

1. 人先定接口与伪代码，AI 再补实现；
2. 所有 AI 生成代码必须由负责人逐行审查并能口头解释；
3. 只参考 MediaPipe / Pygame / OpenCV 官方文档与 API，不照搬完整项目；
4. 实验报告中写明 AI 辅助边界与自研集成、调试工作。

## 提交材料

- 实验报告：项目功能、实现思路、技术栈、环境、交互、测试、部署文档
- 提交文档：使用 `Submission document - Project name` 模板，标题为 `项目名称_组名`
- 演示视频：不超过 5 分钟
