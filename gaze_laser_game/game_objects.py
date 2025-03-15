#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼睛激光游戏 - 游戏对象模块
"""

import random
import pygame
import numpy as np
import time
import threading


class GameObject:
    """游戏对象基类"""
    
    def __init__(self, position, size, color):
        """
        初始化游戏对象
        
        参数:
            position: 位置坐标 (x, y)
            size: 大小
            color: 颜色 (R, G, B)
        """
        self.position = position
        self.size = size
        self.color = color
        self.active = True
        
    def update(self):
        """更新游戏对象状态"""
        pass
        
    def is_active(self):
        """检查对象是否活跃"""
        return self.active


class Target(GameObject):
    """目标对象"""
    
    def __init__(self, position, size, color, speed=(0, 0), points=10, target_type="normal"):
        """
        初始化目标对象
        
        参数:
            position: 位置坐标 (x, y)
            size: 大小
            color: 颜色 (R, G, B)
            speed: 移动速度 (dx, dy)
            points: 击中目标获得的分数
            target_type: 目标类型 ("normal" 或 "bomb")
        """
        super().__init__(position, size, color)
        self.speed = speed
        self.points = points
        self.creation_time = time.time()
        self.lifetime = random.uniform(5.0, 10.0)  # 目标存在的时间（秒）
        self.target_type = target_type  # 目标类型
        
    def update(self, eye_positions=None):
        """
        更新目标状态
        
        参数:
            eye_positions: 眼睛位置列表 [(left_eye_x, left_eye_y), (right_eye_x, right_eye_y)]
        """
        # 更新位置
        self.position = (
            self.position[0] + self.speed[0],
            self.position[1] + self.speed[1]
        )
        
        # 检查是否超出屏幕边界，如果是则移除
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        if (self.position[0] + self.size < 0 or 
            self.position[0] - self.size > screen_width or
            self.position[1] + self.size < 0 or
            self.position[1] - self.size > screen_height):
            self.active = False
            
        # 检查生命周期
        if time.time() - self.creation_time > self.lifetime:
            self.active = False
            
        # 如果提供了眼睛位置，检查是否与眼睛碰撞（仅对炸弹类型）
        if eye_positions and self.target_type == "bomb":
            for eye_pos in eye_positions:
                if eye_pos:  # 确保眼睛位置有效
                    distance = np.sqrt((self.position[0] - eye_pos[0])**2 + 
                                      (self.position[1] - eye_pos[1])**2)
                    if distance < self.size + 10:  # 10是眼睛的近似半径
                        return "game_over"  # 返回游戏结束信号
        
        return None  # 正常返回


class Laser(GameObject):
    """激光对象"""
    
    def __init__(self, start_position, direction, color=(255, 0, 0), width=3, is_eye_beam=False):
        """
        初始化激光对象
        
        参数:
            start_position: 起始位置 (x, y)
            direction: 方向向量 (dx, dy)
            color: 颜色 (R, G, B)
            width: 激光宽度
            is_eye_beam: 是否是眼睛持续发射的激光
        """
        super().__init__(start_position, width, color)
        self.direction = direction
        self.length = 2000  # 激光长度，增加以确保覆盖整个屏幕
        self.start_time = time.time()
        self.duration = 0.3  # 激光持续时间（秒）
        self.is_eye_beam = is_eye_beam  # 是否是眼睛持续发射的激光
        
        # 计算终点位置
        direction_norm = np.linalg.norm(direction)
        if direction_norm > 0:
            normalized_direction = (direction[0] / direction_norm, direction[1] / direction_norm)
            self.end_position = (
                start_position[0] + normalized_direction[0] * self.length,
                start_position[1] + normalized_direction[1] * self.length
            )
        else:
            self.end_position = start_position
            
    def update(self, start_position=None, direction=None):
        """
        更新激光状态
        
        参数:
            start_position: 新的起始位置
            direction: 新的方向向量
        """
        # 如果是眼睛持续发射的激光，则不检查持续时间
        if not self.is_eye_beam:
            # 检查激光是否过期
            if time.time() - self.start_time > self.duration:
                self.active = False
                return
            
        if start_position and direction:
            self.position = start_position
            self.direction = direction
            
            # 重新计算终点位置
            direction_norm = np.linalg.norm(direction)
            if direction_norm > 0:
                normalized_direction = (direction[0] / direction_norm, direction[1] / direction_norm)
                self.end_position = (
                    start_position[0] + normalized_direction[0] * self.length,
                    start_position[1] + normalized_direction[1] * self.length
                )
            else:
                self.end_position = start_position


class Explosion(GameObject):
    """爆炸效果对象"""
    
    def __init__(self, position, max_size=50, color=(255, 165, 0), duration=0.5):
        """
        初始化爆炸效果对象
        
        参数:
            position: 位置坐标 (x, y)
            max_size: 最大尺寸
            color: 颜色 (R, G, B)
            duration: 持续时间（秒）
        """
        super().__init__(position, 1, color)
        self.max_size = max_size
        self.duration = duration
        self.creation_time = time.time()
        self.current_size = 1
        self.growth_rate = max_size / (duration * 0.5)  # 前一半时间膨胀
        
    def update(self):
        """更新爆炸效果状态"""
        elapsed_time = time.time() - self.creation_time
        
        if elapsed_time > self.duration:
            self.active = False
            return
            
        # 前一半时间膨胀，后一半时间收缩
        if elapsed_time < self.duration * 0.5:
            self.current_size = min(self.max_size, self.current_size + self.growth_rate * 0.016)  # 假设16ms一帧
        else:
            self.current_size = max(0, self.current_size - self.growth_rate * 0.016)
            
        self.size = int(self.current_size)


class GameObjectManager:
    """游戏对象管理器"""
    
    def __init__(self):
        """初始化游戏对象管理器"""
        self.targets = []
        self.lasers = []
        self.explosions = []
        self.last_target_spawn_time = 0
        self.target_spawn_interval = 1.0  # 目标生成间隔（秒）
        self.bomb_probability = 0.2  # 炸弹生成概率
        self.eye_positions = [None, None]  # 左右眼位置
        self.left_eye_position = None  # 左眼位置
        self.right_eye_position = None  # 右眼位置
        self.eye_beams = [None, None]  # 左右眼持续发射的激光
        self.gaze_point = None  # 注视点
        self.is_firing = False  # 是否正在发射激光
        
    def setup(self):
        """设置游戏对象管理器"""
        self.targets = []
        self.lasers = []
        self.explosions = []
        self.last_target_spawn_time = time.time()
        self.eye_beams = [None, None]
        self.left_eye_position = None
        self.right_eye_position = None
        self.gaze_point = None
        self.is_firing = False
        
    def update(self):
        """更新所有游戏对象"""
        game_over = False
        
        # 更新目标
        for target in self.targets[:]:
            result = target.update(self.eye_positions)
            if result == "game_over":
                game_over = True
            if not target.is_active():
                self.targets.remove(target)
                
        # 更新激光
        for laser in self.lasers[:]:
            laser.update()
            if not laser.is_active():
                self.lasers.remove(laser)
                
        # 更新爆炸效果
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.is_active():
                self.explosions.remove(explosion)
                
        # 更新眼睛激光（仅在未发射激光时显示）
        if not self.is_firing:
            self.update_eye_beams()
                
        # 自动生成目标
        current_time = time.time()
        if current_time - self.last_target_spawn_time > self.target_spawn_interval:
            self.spawn_random_target()
            self.last_target_spawn_time = current_time
            
            # 随着时间推移，增加生成频率和炸弹概率
            self.target_spawn_interval = max(0.5, self.target_spawn_interval * 0.99)
            self.bomb_probability = min(0.4, self.bomb_probability * 1.01)
            
        return game_over
                
    def update_eye_positions(self, left_eye_pos, right_eye_pos, gaze_point=None):
        """
        更新眼睛位置
        
        参数:
            left_eye_pos: 左眼位置 (x, y)
            right_eye_pos: 右眼位置 (x, y)
            gaze_point: 注视点 (x, y)
        """
        self.eye_positions = [left_eye_pos, right_eye_pos]
        self.left_eye_position = left_eye_pos
        self.right_eye_position = right_eye_pos
        if gaze_point:
            self.gaze_point = gaze_point
            
    def update_eye_beams(self):
        """更新眼睛持续发射的激光"""
        if not self.gaze_point:
            return
            
        # 更新左眼激光
        if self.eye_positions[0]:
            if self.eye_beams[0] is None:
                # 创建新的左眼激光 - 使用明亮的紫色，增加宽度
                direction = (self.gaze_point[0] - self.eye_positions[0][0], 
                            self.gaze_point[1] - self.eye_positions[0][1])
                self.eye_beams[0] = Laser(self.eye_positions[0], direction, 
                                         color=(180, 0, 255), width=2, is_eye_beam=True)
                self.lasers.append(self.eye_beams[0])
            else:
                # 更新现有左眼激光
                direction = (self.gaze_point[0] - self.eye_positions[0][0], 
                            self.gaze_point[1] - self.eye_positions[0][1])
                self.eye_beams[0].update(self.eye_positions[0], direction)
                
        # 更新右眼激光
        if self.eye_positions[1]:
            if self.eye_beams[1] is None:
                # 创建新的右眼激光 - 使用明亮的紫色，增加宽度
                direction = (self.gaze_point[0] - self.eye_positions[1][0], 
                            self.gaze_point[1] - self.eye_positions[1][1])
                self.eye_beams[1] = Laser(self.eye_positions[1], direction, 
                                         color=(180, 0, 255), width=2, is_eye_beam=True)
                self.lasers.append(self.eye_beams[1])
            else:
                # 更新现有右眼激光
                direction = (self.gaze_point[0] - self.eye_positions[1][0], 
                            self.gaze_point[1] - self.eye_positions[1][1])
                self.eye_beams[1].update(self.eye_positions[1], direction)
            
    def fire_laser(self, eye_pos, gaze_direction):
        """
        从眼睛位置发射激光
        
        参数:
            eye_pos: 眼睛位置 (x, y)
            gaze_direction: 注视方向 (x, y)
        """
        if not eye_pos or not gaze_direction:
            return
            
        # 设置发射状态为True
        self.is_firing = True
        
        # 移除未激活的瞄准线
        self.remove_eye_beams()
            
        # 计算方向向量
        direction = (gaze_direction[0] - eye_pos[0], gaze_direction[1] - eye_pos[1])
        
        # 创建激光 - 使用鲜艳的红色，增加宽度
        laser = Laser(eye_pos, direction, color=(255, 0, 0), width=6)
        self.lasers.append(laser)
        
        # 0.3秒后重置发射状态
        def reset_firing_state():
            self.is_firing = False
            
        timer = threading.Timer(0.3, reset_firing_state)
        timer.daemon = True
        timer.start()
            
    def remove_eye_beams(self):
        """移除未激活的瞄准线"""
        # 移除左眼激光
        if self.eye_beams[0] in self.lasers:
            self.lasers.remove(self.eye_beams[0])
        self.eye_beams[0] = None
        
        # 移除右眼激光
        if self.eye_beams[1] in self.lasers:
            self.lasers.remove(self.eye_beams[1])
        self.eye_beams[1] = None
            
    def spawn_random_target(self):
        """生成随机目标"""
        # 获取屏幕尺寸
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        # 决定目标类型
        target_type = "bomb" if random.random() < self.bomb_probability else "normal"
        
        # 决定目标颜色
        if target_type == "normal":
            # 普通目标使用随机颜色
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        else:
            # 炸弹使用红色
            color = (255, 0, 0)
        
        # 随机大小
        size = random.randint(20, 50)
        
        # 随机生成位置（在屏幕边缘）
        side = random.choice(["top", "right", "bottom", "left"])
        
        if side == "top":
            x = random.randint(0, screen_width)
            y = -size
            
        elif side == "right":
            x = screen_width + size
            y = random.randint(0, screen_height)
            
        elif side == "bottom":
            x = random.randint(0, screen_width)
            y = screen_height + size
            
        else:  # left
            x = -size
            y = random.randint(0, screen_height)
            
        # 计算目标移动方向（朝向屏幕中心或眼睛位置）
        target_position = (x, y)
        
        # 如果有眼睛位置，则朝向眼睛中心
        if self.eye_positions[0] and self.eye_positions[1]:
            eye_center_x = (self.eye_positions[0][0] + self.eye_positions[1][0]) / 2
            eye_center_y = (self.eye_positions[0][1] + self.eye_positions[1][1]) / 2
            target_center = (eye_center_x, eye_center_y)
        else:
            # 否则朝向屏幕中心
            target_center = (screen_width / 2, screen_height / 2)
            
        # 计算方向向量
        direction_x = target_center[0] - target_position[0]
        direction_y = target_center[1] - target_position[1]
        
        # 归一化方向向量
        direction_length = np.sqrt(direction_x**2 + direction_y**2)
        if direction_length > 0:
            direction_x /= direction_length
            direction_y /= direction_length
            
        # 设置速度（根据目标类型调整）
        # 炸弹速度降低为原来的一半
        speed_factor = 1.0 if target_type == "bomb" else 1.0
        speed = (direction_x * random.uniform(1.0, 2.0) * speed_factor, 
                direction_y * random.uniform(1.0, 2.0) * speed_factor)
        
        # 设置分数（炸弹不给分）
        points = 0 if target_type == "bomb" else int(100 / size * 10)
        
        # 创建目标
        target = Target(target_position, size, color, speed, points, target_type)
        self.targets.append(target)
        
    def create_explosion(self, position, is_bomb=False):
        """
        创建爆炸效果
        
        参数:
            position: 爆炸位置 (x, y)
            is_bomb: 是否是炸弹爆炸
        """
        # 炸弹爆炸效果更大，颜色为红色
        if is_bomb:
            explosion = Explosion(position, max_size=100, color=(255, 0, 0), duration=1.0)
        else:
            explosion = Explosion(position)
            
        self.explosions.append(explosion)
        
    def remove_target(self, target):
        """
        移除目标
        
        参数:
            target: 要移除的目标对象
        """
        if target in self.targets:
            # 如果是炸弹，创建炸弹爆炸效果
            if target.target_type == "bomb":
                self.create_explosion(target.position, is_bomb=True)
            else:
                self.create_explosion(target.position)
                
            self.targets.remove(target) 