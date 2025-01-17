# Python 俄罗斯方块游戏

一个使用 Python 和 Pygame 库开发的经典俄罗斯方块游戏。

## 安装依赖

在运行游戏之前，请先安装必要的依赖：

```bash
pip install -r requirements.txt
```

## 运行游戏

```bash
python tetris.py
```

## 游戏控制

- ↑ (上箭头): 旋转方块
- ↓ (下箭头): 加速下落
- ← (左箭头): 向左移动
- → (右箭头): 向右移动
- 空格键: 直接落到底部
- ESC: 退出游戏

## 游戏规则

- 方块会持续从顶部落下
- 使用方向键控制方块的移动和旋转
- 当一行被完全填满时，该行会消失并获得分数
- 当方块堆到顶部时游戏结束
