#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼睛激光游戏 - 入口脚本
"""

from gaze_laser_game.app import GazeLaserGameApp

if __name__ == "__main__":
    app = GazeLaserGameApp()
    app.setup()
    app.run() 