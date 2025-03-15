#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼睛激光游戏 - 工具函数模块
"""

import time
import numpy as np
import cv2


class FPS:
    """帧率计算器"""
    
    def __init__(self):
        """初始化帧率计算器"""
        self.prev_time = time.time()
        self.frame_times = []
        self.max_samples = 30
        
    def update(self):
        """更新帧率计算"""
        current_time = time.time()
        delta_time = current_time - self.prev_time
        self.prev_time = current_time
        
        self.frame_times.append(delta_time)
        
        # 保持样本数量
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
            
    def get_fps(self):
        """获取当前帧率"""
        if not self.frame_times:
            return 0
            
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0


def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    """
    保持纵横比调整图像大小
    
    参数:
        image: 输入图像
        width: 目标宽度
        height: 目标高度
        inter: 插值方法
        
    返回:
        调整大小后的图像
    """
    dim = None
    (h, w) = image.shape[:2]
    
    if width is None and height is None:
        return image
        
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
        
    return cv2.resize(image, dim, interpolation=inter)


def draw_text(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, 
              font_thickness=2, text_color=(255, 255, 255), text_color_bg=(0, 0, 0)):
    """
    在图像上绘制带背景的文本
    
    参数:
        img: 输入图像
        text: 要绘制的文本
        pos: 文本位置 (x, y)
        font: 字体
        font_scale: 字体大小
        font_thickness: 字体粗细
        text_color: 文本颜色
        text_color_bg: 背景颜色
        
    返回:
        带有文本的图像
    """
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    
    # 绘制背景矩形
    cv2.rectangle(img, (x, y - text_h - 10), (x + text_w, y), text_color_bg, -1)
    
    # 绘制文本
    cv2.putText(img, text, (x, y - 5), font, font_scale, text_color, font_thickness)
    
    return img


def distance(point1, point2):
    """
    计算两点之间的欧几里得距离
    
    参数:
        point1: 第一个点 (x, y)
        point2: 第二个点 (x, y)
        
    返回:
        两点之间的距离
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def normalize_vector(vector):
    """
    归一化向量
    
    参数:
        vector: 输入向量 (x, y)
        
    返回:
        归一化后的向量
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm 