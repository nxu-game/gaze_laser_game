# 眼睛激光游戏

一个基于眼睛追踪的激光射击游戏，使用MediaPipe进行眼睛位置检测和手势识别。

![眼睛激光游戏演示](https://github.com/nxu-game/interesting_assets/raw/main/images/gaze_laser_game1.png)

[English Documentation](README.md)

## 游戏特性

- 从眼睛位置发射的持续激光束
- 通过触摸鼻尖发射强力激光
- 从各个方向接近的目标
- 普通目标和炸弹目标
- 等级系统和生命值系统
- 炫酷的视觉效果和音效
- 性能优化的物理引擎

## 系统要求

1. Python 3.7+
2. 网络摄像头

## 依赖项

```
pip install -r requirements.txt
```

主要依赖项:
- OpenCV
- MediaPipe
- Pygame
- NumPy

## 如何运行

1. 安装所有依赖项:
   ```
   pip install -r requirements.txt
   ```

2. 运行游戏(两种方式):
   ```
   python run.py
   ```
   或
   ```
   python -m gaze_laser_game
   ```

## 声音和背景

游戏支持以下声音和背景图像:

1. 声音文件 (放在 `gaze_laser_game/assets/sounds` 目录):
   - `laser.wav` - 激光发射声音
   - `bomb0.mp3` - 普通目标爆炸声音
   - `bomb1.mp3` - 炸弹爆炸声音
   - `game_over.mp3` - 游戏结束声音
   - `background.mp3` - 背景音乐

2. 背景图像 (放在 `gaze_laser_game/assets` 目录):
   - `background.jpg` - 游戏背景图像

如果这些文件不存在，游戏仍然可以运行，只是没有声音和背景图像。

## 游戏控制

- **眼睛移动**: 用眼睛瞄准(细的持续激光束)
- **触摸鼻尖**: 发射强力激光
- **空格键**: 暂停/继续游戏，游戏结束后重新开始
- **ESC键**: 退出游戏
- **M键**: 静音/取消静音背景音乐
- **F键**: 在调试模式下手动发射激光

## 游戏规则

1. 用眼睛瞄准目标，触摸鼻尖发射强力激光
2. 击中普通目标(彩色)获得分数
3. 避免炸弹目标(红色)击中你的眼睛，否则会失去生命值
4. 当生命值降至零时游戏结束
5. 随着分数增加，难度会增加

## 技术特点

- 使用MediaPipe的Face Mesh模型进行面部特征检测
- 实时眼睛位置跟踪和手势识别
- 优化的碰撞检测算法
- 多线程处理提高性能
- 自适应难度系统

## 提示

- 确保良好的光照条件以获得最佳眼睛追踪效果
- 保持适当的距离，通常为30-60厘米
- 如果眼睛追踪不准确，尝试调整摄像头位置或光照条件

## 故障排除

- 如果游戏无法启动，确保你的摄像头已连接并正常工作
- 如果眼睛追踪不准确，尝试在更好的光照条件下玩游戏
- 如果游戏帧率低，尝试降低摄像头分辨率或关闭一些视觉效果

## 开发者信息

这个游戏使用MediaPipe和Pygame开发，利用MediaPipe的Face Mesh模型进行眼睛位置检测和手势识别。游戏包含优化的物理引擎，支持从各个方向接近的目标，以及炫酷的视觉效果。

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 微信：znzatop

![微信](https://github.com/nxu-game/interesting_assets/raw/main/images/wechat.jpg)

## 更多项目

更多有趣的项目请见：https://github.com/nxu-game/interesting_assets.git

## 许可证

本项目采用GNU通用公共许可证v3.0(GPLv3)。详情请参阅LICENSE文件。 
