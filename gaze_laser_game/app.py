#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Eye Laser Game - Main Application Module
"""

import cv2
import time
import numpy as np
import pygame
import os
import sys

from .gaze_tracker import GazeTracker
from .game_objects import GameObjectManager, Target, Laser, Explosion
from .renderer import GameRenderer
from .physics import PhysicsEngine
from .utils import FPS


class GazeLaserGameApp:
    """Eye Laser Game Application"""

    def __init__(self):
        """Initialize the application"""
        self.gaze_tracker = GazeTracker()
        self.game_object_manager = GameObjectManager()
        self.renderer = GameRenderer()
        self.physics_engine = PhysicsEngine()
        self.fps = FPS()
        self.cap = None
        
        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.level = 1
        self.lives = 3
        
        # 触发控制
        self.last_fire_time = 0
        self.fire_cooldown = 0.3  # 发射冷却时间（秒）
        
        # Debug mode
        self.debug = True
        
        # Music control
        self.background_music_playing = False
        
        # 屏幕尺寸
        self.screen_width = 1280
        self.screen_height = 720
        
    def setup(self):
        """Set up the application"""
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise ValueError("Cannot open camera")
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.screen_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.screen_height)
        
        # Initialize Pygame
        pygame.init()
        
        # Initialize game renderer
        self.renderer.setup(self.screen_width, self.screen_height)
        
        # Initialize eye tracker
        self.gaze_tracker.setup()
        
        # Initialize physics engine
        self.physics_engine.setup()
        
        # Initialize game object manager
        self.game_object_manager.setup()
        
        # Load sounds
        self.load_sounds()
        
        # Play background music
        self.play_background_music()
        
        # Print debug info
        if self.debug:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            print(f"Assets directory: {assets_dir}")
            
    def load_sounds(self):
        """Load game sounds"""
        # Create sounds directory
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        sounds_dir = os.path.join(assets_dir, "sounds")
        os.makedirs(sounds_dir, exist_ok=True)
        
        # Initialize sounds dictionary
        self.sounds = {}
        
        # Set sound volume
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
        
        try:
            # 加载激光声音
            laser_sound_path = os.path.join(sounds_dir, "laser.wav")
            
            # 加载爆炸声音（普通目标）
            normal_explosion_path = os.path.join(sounds_dir, "bomb0.mp3")
            
            # 加载爆炸声音（炸弹）
            bomb_explosion_path = os.path.join(sounds_dir, "bomb1.mp3")
            
            # 加载游戏结束声音
            game_over_sound_path = os.path.join(sounds_dir, "game_over.mp3")
            
            # 加载背景音乐
            background_music_path = os.path.join(sounds_dir, "background.mp3")
            
            # 检查并加载声音文件
            if os.path.exists(laser_sound_path):
                self.sounds["laser"] = pygame.mixer.Sound(laser_sound_path)
                self.sounds["laser"].set_volume(0.3)
            
            if os.path.exists(normal_explosion_path):
                self.sounds["normal_explosion"] = pygame.mixer.Sound(normal_explosion_path)
                self.sounds["normal_explosion"].set_volume(0.5)
                
            if os.path.exists(bomb_explosion_path):
                self.sounds["bomb_explosion"] = pygame.mixer.Sound(bomb_explosion_path)
                self.sounds["bomb_explosion"].set_volume(0.5)
                
            if os.path.exists(game_over_sound_path):
                self.sounds["game_over"] = pygame.mixer.Sound(game_over_sound_path)
                self.sounds["game_over"].set_volume(0.7)
                
            # 设置背景音乐
            if os.path.exists(background_music_path):
                self.background_music = background_music_path
            else:
                self.background_music = None
                
        except Exception as e:
            print(f"Error loading sounds: {e}")
            
    def play_background_music(self):
        """Play background music"""
        if hasattr(self, 'background_music') and self.background_music and not self.background_music_playing:
            try:
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.set_volume(0.3)  # Set volume
                pygame.mixer.music.play(-1)  # -1 means loop forever
                self.background_music_playing = True
            except Exception as e:
                print(f"Error playing background music: {e}")
                
    def stop_background_music(self):
        """Stop background music"""
        if self.background_music_playing:
            pygame.mixer.music.stop()
            self.background_music_playing = False
            
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def run(self):
        """Run the main application loop"""
        running = True
        clock = pygame.time.Clock()  # 添加时钟对象用于控制帧率
        target_fps = 60  # 目标帧率
        
        while running:
            # 限制帧率
            clock.tick(target_fps)
            
            self.fps.update()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.game_over:
                            # Restart game
                            self.reset_game()
                        else:
                            self.paused = not self.paused
                            # Pause/resume background music
                            if self.paused:
                                pygame.mixer.music.pause()
                            else:
                                pygame.mixer.music.unpause()
                    elif event.key == pygame.K_f and self.debug:
                        # Fire lasers in debug mode
                        self.fire_lasers()
                    elif event.key == pygame.K_m:
                        # Mute/unmute with M key
                        if pygame.mixer.music.get_volume() > 0:
                            pygame.mixer.music.set_volume(0)
                        else:
                            pygame.mixer.music.set_volume(0.3)
            
            if self.paused:
                self.renderer.render_pause_screen()
                pygame.display.flip()
                continue
                
            if self.game_over:
                self.renderer.render_game_over(self.score)
                pygame.display.flip()
                continue
            
            # Get camera frame
            ret, frame = self.cap.read()
            if not ret:
                print("Cannot get camera frame")
                break
                
            # Process frame
            self.process_frame(frame)
            
            # Update display
            pygame.display.flip()
            
        self.cleanup()
        
    def reset_game(self):
        """Reset game state"""
        self.score = 0
        self.game_over = False
        self.paused = False
        self.level = 1
        self.lives = 3
        self.game_object_manager.setup()
        
        # Restart background music
        self.play_background_music()
        
    def process_frame(self, frame):
        """Process camera frame"""
        # 获取原始图像尺寸
        frame_height, frame_width = frame.shape[:2]
        
        # 先获取原始帧中的眼睛位置（未翻转）
        original_gaze_result = self.gaze_tracker.detect_gaze(frame.copy())
        
        # 然后翻转图像用于显示
        # flipped_frame = cv2.flip(frame, 1)
        
        # 在翻转后的图像上进行面部特征检测（用于显示）
        # flipped_gaze_result = self.gaze_tracker.detect_gaze(flipped_frame)
        flipped_gaze_result = self.gaze_tracker.detect_gaze(frame)
        
        # flipped_frame = cv2.flip(frame, 1)
        
        # 更新眼睛位置和注视点 - 使用原始帧中的坐标，但进行水平翻转以匹配显示
        if original_gaze_result["face_detected"]:
            # 获取原始帧中的眼睛位置
            left_eye_pos = original_gaze_result["left_eye_position"]
            right_eye_pos = original_gaze_result["right_eye_position"]
            gaze_point = original_gaze_result["gaze_point"]
            
            # 水平翻转坐标以匹配显示的画面
            if left_eye_pos:
                left_eye_pos = (frame_width - left_eye_pos[0], left_eye_pos[1])
            if right_eye_pos:
                right_eye_pos = (frame_width - right_eye_pos[0], right_eye_pos[1])
            if gaze_point:
                gaze_point = (frame_width - gaze_point[0], gaze_point[1])
            
            # 更新游戏对象管理器中的眼睛位置
            self.game_object_manager.update_eye_positions(
                left_eye_pos,
                right_eye_pos,
                gaze_point
            )
        
        # 检测食指是否靠近鼻子，如果是则发射激光
        # 使用翻转后的检测结果，因为用户是看着翻转后的画面进行交互
        current_time = time.time()
        if (flipped_gaze_result["is_finger_near_nose"] and 
            current_time - self.last_fire_time > self.fire_cooldown):
            self.fire_lasers()
            self.last_fire_time = current_time
        
        # 更新游戏对象
        game_over = self.game_object_manager.update()
        
        # 如果炸弹击中眼睛，减少生命值
        if game_over:
            self.lives -= 1
            self.play_sound("bomb_explosion")  # 使用炸弹爆炸音效
            
            if self.lives <= 0:
                self.game_over = True
                self.play_sound("game_over")
                self.stop_background_music()
        
        # 检测碰撞 - 性能优化：只在有激光的情况下检测碰撞
        if self.game_object_manager.lasers:
            collisions = self.physics_engine.detect_collisions(
                self.game_object_manager.lasers,
                self.game_object_manager.targets
            )
            
            # 处理碰撞
            for laser, target in collisions:
                # 跳过眼睛持续发射的激光（用于显示）
                if hasattr(laser, 'is_eye_beam') and laser.is_eye_beam:
                    continue
                    
                # 移除目标
                self.game_object_manager.remove_target(target)
                
                # 根据目标类型播放不同的音效
                if target.target_type == "bomb":
                    # 如果是炸弹，播放炸弹爆炸音效
                    self.play_sound("bomb_explosion")
                else:
                    # 如果是普通目标，播放普通爆炸音效并增加分数
                    self.score += target.points
                    self.play_sound("normal_explosion")
                    
                    # 每1000分升一级
                    if self.score // 1000 > self.level - 1:
                        self.level = self.score // 1000 + 1
        
        # 渲染游戏 - 使用翻转后的帧
        self.renderer.render_game(
            frame,
            # flipped_frame,
            self.game_object_manager.targets,
            self.game_object_manager.lasers,
            self.game_object_manager.explosions,
            self.score,
            self.fps.get_fps(),
            self.level,
            self.lives
        )
        
    def fire_lasers(self):
        """从眼睛位置发射激光"""
        # 获取眼睛位置和注视方向
        # 使用游戏对象管理器中已经翻转过的坐标
        left_eye_pos = self.game_object_manager.left_eye_position
        right_eye_pos = self.game_object_manager.right_eye_position
        gaze_point = self.game_object_manager.gaze_point
        
        if not left_eye_pos or not right_eye_pos:
            return
            
        # 从左眼发射激光
        if left_eye_pos and gaze_point:
            self.game_object_manager.fire_laser(
                left_eye_pos,
                gaze_point
            )
            
        # 从右眼发射激光
        if right_eye_pos and gaze_point:
            self.game_object_manager.fire_laser(
                right_eye_pos,
                gaze_point
            )
            
        # 播放激光声音
        self.play_sound("laser")
        
    def cleanup(self):
        """清理资源"""
        if self.cap is not None:
            self.cap.release()
        
        self.stop_background_music()
        self.gaze_tracker.cleanup()
        pygame.quit()
        cv2.destroyAllWindows() 