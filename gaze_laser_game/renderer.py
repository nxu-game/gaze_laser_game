#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Eye Laser Game - Renderer Module
"""

import pygame
import cv2
import numpy as np
import os
import time


class GameRenderer:
    """Game Renderer"""
    
    def __init__(self):
        """Initialize the renderer"""
        self.screen = None
        self.width = 0
        self.height = 0
        self.font = None
        self.large_font = None
        self.background = None
        
    def setup(self, width, height):
        """
        Set up the renderer
        
        Parameters:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height
        
        # Create Pygame screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Eye Laser Game")
        
        # Initialize fonts
        pygame.font.init()
        
        # 尝试加载支持中文的字体
        try:
            # 尝试使用系统字体
            system_fonts = pygame.font.get_fonts()
            if 'microsoftyahei' in system_fonts:
                self.font = pygame.font.SysFont('microsoftyahei', 24)
                self.large_font = pygame.font.SysFont('microsoftyahei', 48)
            elif 'simsun' in system_fonts:
                self.font = pygame.font.SysFont('simsun', 24)
                self.large_font = pygame.font.SysFont('simsun', 48)
            else:
                # 如果没有找到中文字体，使用默认字体
                self.font = pygame.font.SysFont('Arial', 24)
                self.large_font = pygame.font.SysFont('Arial', 48)
        except:
            # 出错时使用默认字体
            self.font = pygame.font.SysFont('Arial', 24)
            self.large_font = pygame.font.SysFont('Arial', 48)
        
        # Load background image (if exists)
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        background_path = os.path.join(assets_dir, "background.jpg")
        
        if os.path.exists(background_path):
            self.background = pygame.image.load(background_path)
            self.background = pygame.transform.scale(self.background, (width, height))
        
    def render_game(self, frame, targets, lasers, explosions, score, fps, level=1, lives=3):
        """
        Render the game
        
        Parameters:
            frame: Camera frame
            targets: List of target objects
            lasers: List of laser objects
            explosions: List of explosion effects
            score: Current score
            fps: Current FPS
            level: Current level
            lives: Remaining lives
        """
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw background (if exists)
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # Convert camera frame to Pygame surface and display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
        
        # Draw targets
        for target in targets:
            self._render_target(target)
            
        # Draw lasers
        for laser in lasers:
            self._render_laser(laser)
            
        # Draw explosions
        for explosion in explosions:
            self._render_explosion(explosion)
            
        # Draw score
        score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = self.font.render(f"Level: {level}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 40))
        
        # Draw lives
        lives_text = self.font.render(f"Lives: {lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 70))
        
        # Draw FPS
        fps_text = self.font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 100))
        
        # Draw game hint - 使用英文替代中文
        hint_text = self.font.render("Touch nose with index finger to fire!", True, (255, 255, 0))
        self.screen.blit(hint_text, (self.width - 350, 10))
        
    def render_pause_screen(self):
        """Render pause screen"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.large_font.render("GAME PAUSED", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_text, text_rect)
        
        # Draw continue hint
        continue_text = self.font.render("Press SPACE to continue", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(continue_text, continue_rect)
        
    def render_game_over(self, score):
        """
        Render game over screen
        
        Parameters:
            score: Final score
        """
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Draw score
        score_text = self.large_font.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart hint
        restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
        
    def _render_target(self, target):
        """
        Render a target
        
        Parameters:
            target: Target object
        """
        # 如果目标有图片，使用图片渲染
        if target.image:
            # 获取图片尺寸
            img_width, img_height = target.image.get_size()
            
            # 计算图片位置（居中）
            img_x = int(target.position[0] - img_width / 2)
            img_y = int(target.position[1] - img_height / 2)
            
            # 绘制图片
            self.screen.blit(target.image, (img_x, img_y))
            
            # 如果是炸弹，添加警告标识
            if target.target_type == "bomb":
                # 在图片上方绘制警告标识
                pygame.draw.polygon(
                    self.screen,
                    (255, 0, 0),  # 红色
                    [
                        (target.position[0], target.position[1] - img_height / 2 - 20),
                        (target.position[0] - 10, target.position[1] - img_height / 2 - 5),
                        (target.position[0] + 10, target.position[1] - img_height / 2 - 5)
                    ]
                )
                
                # 绘制感叹号
                warning_text = self.font.render("!", True, (255, 255, 255))
                warning_rect = warning_text.get_rect(center=(target.position[0], target.position[1] - img_height / 2 - 12))
                self.screen.blit(warning_text, warning_rect)
        else:
            # 没有图片时使用原来的圆形渲染
            # Draw target circle
            pygame.draw.circle(
                self.screen,
                target.color,
                (int(target.position[0]), int(target.position[1])),
                target.size
            )
            
            # Draw target border
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (int(target.position[0]), int(target.position[1])),
                target.size,
                2
            )
            
            # If it's a bomb, draw bomb indicator
            if target.target_type == "bomb":
                # Draw bomb fuse
                pygame.draw.line(
                    self.screen,
                    (255, 255, 0),
                    (int(target.position[0]), int(target.position[1] - target.size)),
                    (int(target.position[0]), int(target.position[1] - target.size * 1.3)),
                    3
                )
                
                # Draw bomb spark
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 0),
                    (int(target.position[0]), int(target.position[1] - target.size * 1.3)),
                    3
                )
        
    def _render_laser(self, laser):
        """
        Render a laser
        
        Parameters:
            laser: Laser object
        """
        # 判断是否是眼睛持续发射的激光
        is_eye_beam = hasattr(laser, 'is_eye_beam') and laser.is_eye_beam
        
        # 为眼睛持续发射的激光添加外发光效果
        if is_eye_beam:
            # 绘制外发光效果（更大的半透明线条）
            glow_color = (255, 255, 255, 100)  # 白色半透明
            glow_width = laser.size * 3
            pygame.draw.line(
                self.screen,
                glow_color,
                laser.position,
                laser.end_position,
                glow_width
            )
        
        # Draw laser line
        pygame.draw.line(
            self.screen,
            laser.color,
            laser.position,
            laser.end_position,
            laser.size
        )
        
        # Draw laser origin
        pygame.draw.circle(
            self.screen,
            laser.color,
            (int(laser.position[0]), int(laser.position[1])),
            5
        )
        
        # 为激活的激光（非持续激光）添加更强的视觉效果
        if not is_eye_beam:
            # 绘制内发光效果（较亮的中心线）
            inner_color = (255, 255, 255)  # 纯白色
            inner_width = max(1, laser.size // 3)
            pygame.draw.line(
                self.screen,
                inner_color,
                laser.position,
                laser.end_position,
                inner_width
            )
        else:
            # 为持续激光添加脉冲效果
            pulse_size = 2 + int(abs(np.sin(time.time() * 5)) * 3)  # 脉冲大小随时间变化
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),  # 白色
                (int(laser.position[0]), int(laser.position[1])),
                pulse_size
            )
        
    def _render_explosion(self, explosion):
        """
        Render an explosion effect
        
        Parameters:
            explosion: Explosion object
        """
        # Draw explosion circle
        pygame.draw.circle(
            self.screen,
            explosion.color,
            (int(explosion.position[0]), int(explosion.position[1])),
            explosion.size
        )
        
        # Draw explosion rays
        for i in range(8):
            angle = i * np.pi / 4
            end_x = explosion.position[0] + np.cos(angle) * explosion.size * 1.5
            end_y = explosion.position[1] + np.sin(angle) * explosion.size * 1.5
            
            pygame.draw.line(
                self.screen,
                explosion.color,
                explosion.position,
                (end_x, end_y),
                max(1, explosion.size // 10)
            ) 