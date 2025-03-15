#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼睛激光游戏 - 模块入口点
"""

from .app import GazeLaserGameApp

def main():
    """主函数"""
    app = GazeLaserGameApp()
    app.setup()
    app.run()

if __name__ == "__main__":
    main() 