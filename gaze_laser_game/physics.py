#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼睛激光游戏 - 物理引擎模块
"""

import numpy as np
from typing import List, Tuple, Any


class PhysicsEngine:
    """物理引擎"""
    
    def __init__(self):
        """初始化物理引擎"""
        self.last_collision_check_time = 0
        self.collision_check_interval = 0.016  # 约60fps
        
    def setup(self):
        """设置物理引擎"""
        self.last_collision_check_time = 0
        
    def detect_collisions(self, lasers, targets):
        """
        检测激光和目标之间的碰撞
        
        参数:
            lasers: 激光对象列表
            targets: 目标对象列表
            
        返回:
            collisions: 碰撞对列表 [(laser, target), ...]
        """
        collisions = []
        
        # 性能优化：跳过眼睛持续发射的激光
        active_lasers = [laser for laser in lasers if not (hasattr(laser, 'is_eye_beam') and laser.is_eye_beam)]
        
        # 如果没有激活的激光或目标，直接返回
        if not active_lasers or not targets:
            return collisions
        
        # 性能优化：对目标进行预筛选
        # 只检查屏幕内的目标
        screen_width, screen_height = 1280, 720  # 假设屏幕尺寸
        visible_targets = []
        
        for target in targets:
            # 检查目标是否在屏幕内或接近屏幕
            if (target.position[0] + target.size >= 0 and 
                target.position[0] - target.size <= screen_width and
                target.position[1] + target.size >= 0 and
                target.position[1] - target.size <= screen_height):
                visible_targets.append(target)
        
        # 对每个激光检测碰撞
        for laser in active_lasers:
            # 获取激光的起点和终点
            p1 = np.array(laser.position)
            p2 = np.array(laser.end_position)
            
            # 计算激光方向向量
            line_direction = p2 - p1
            line_length = np.linalg.norm(line_direction)
            
            if line_length == 0:
                continue
                
            # 归一化方向向量
            line_direction = line_direction / line_length
            
            for target in visible_targets:
                if self._fast_laser_target_collision(laser, target, p1, line_direction, line_length):
                    collisions.append((laser, target))
                    
        return collisions
        
    def _fast_laser_target_collision(self, laser, target, p1, line_direction, line_length):
        """
        快速检查激光和目标之间是否发生碰撞（优化版本）
        
        参数:
            laser: 激光对象
            target: 目标对象
            p1: 激光起点
            line_direction: 归一化的激光方向向量
            line_length: 激光长度
            
        返回:
            bool: 是否碰撞
        """
        # 获取目标的位置和半径
        circle_center = np.array(target.position)
        circle_radius = target.size
        
        # 计算圆心到直线的向量
        circle_to_line_start = circle_center - p1
        
        # 计算圆心到直线的投影长度
        projection_length = np.dot(circle_to_line_start, line_direction)
        
        # 快速检查：如果投影长度为负且大于圆半径，则不可能碰撞
        if projection_length < -circle_radius:
            return False
            
        # 快速检查：如果投影长度大于线段长度加圆半径，则不可能碰撞
        if projection_length > line_length + circle_radius:
            return False
        
        # 如果投影点在线段外部，检查端点到圆心的距离
        if projection_length < 0:
            # 检查起点到圆心的距离
            return np.linalg.norm(p1 - circle_center) <= circle_radius
        elif projection_length > line_length:
            # 检查终点到圆心的距离
            return np.linalg.norm(laser.end_position - circle_center) <= circle_radius
        else:
            # 计算投影点到圆心的距离
            closest_point = p1 + line_direction * projection_length
            distance = np.linalg.norm(closest_point - circle_center)
            
            # 如果距离小于等于圆的半径，则发生碰撞
            return distance <= circle_radius
        
    def _check_laser_target_collision(self, laser, target):
        """
        检查激光和目标之间是否发生碰撞（原始版本，保留作为参考）
        
        参数:
            laser: 激光对象
            target: 目标对象
            
        返回:
            bool: 是否碰撞
        """
        # 获取激光的起点和终点
        p1 = np.array(laser.position)
        p2 = np.array(laser.end_position)
        
        # 获取目标的位置和半径
        circle_center = np.array(target.position)
        circle_radius = target.size
        
        # 计算激光方向向量
        line_direction = p2 - p1
        line_length = np.linalg.norm(line_direction)
        
        if line_length == 0:
            # 如果激光长度为0，直接检查起点是否在圆内
            return np.linalg.norm(p1 - circle_center) <= circle_radius
            
        # 归一化方向向量
        line_direction = line_direction / line_length
        
        # 计算圆心到直线的向量
        circle_to_line_start = circle_center - p1
        
        # 计算圆心到直线的投影长度
        projection_length = np.dot(circle_to_line_start, line_direction)
        
        # 如果投影点在线段外部，检查端点到圆心的距离
        if projection_length < 0:
            closest_point = p1
        elif projection_length > line_length:
            closest_point = p2
        else:
            # 计算投影点
            closest_point = p1 + line_direction * projection_length
            
        # 计算最近点到圆心的距离
        distance = np.linalg.norm(closest_point - circle_center)
        
        # 如果距离小于等于圆的半径，则发生碰撞
        return distance <= circle_radius
        
    def check_point_in_circle(self, point, circle_center, circle_radius):
        """
        检查点是否在圆内
        
        参数:
            point: 点坐标 (x, y)
            circle_center: 圆心坐标 (x, y)
            circle_radius: 圆半径
            
        返回:
            bool: 点是否在圆内
        """
        distance = np.sqrt((point[0] - circle_center[0])**2 + (point[1] - circle_center[1])**2)
        return distance <= circle_radius 