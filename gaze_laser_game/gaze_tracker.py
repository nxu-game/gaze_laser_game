#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼睛激光游戏 - 眼睛注视方向跟踪模块
"""

import cv2
import numpy as np
import mediapipe as mp
import time


class GazeTracker:
    """眼睛注视方向跟踪器"""

    def __init__(self):
        """初始化眼睛注视方向跟踪器"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands  # 添加手部检测
        
        # 眼睛关键点索引
        # 左眼
        self.LEFT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        # 右眼
        self.RIGHT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        # 虹膜
        self.LEFT_IRIS_INDICES = [474, 475, 476, 477]
        self.RIGHT_IRIS_INDICES = [469, 470, 471, 472]
        
        # 校准参数
        self.calibrated = False
        self.calibration_center = None
        
        # 食指触摸鼻子检测参数
        self.finger_nose_threshold = 50  # 食指与鼻子的距离阈值（像素）
        self.is_finger_near_nose = False
        
        # 显示设置
        self.show_face_mesh = True  # 显示人脸网格
        self.show_hand_landmarks = True  # 显示手部关键点
        
        # 保存最后一次检测结果
        self.last_result = {
            "gaze_point": None,
            "left_eye_position": None,
            "right_eye_position": None,
            "face_detected": False,
            "is_finger_near_nose": False,  # 新增：食指是否靠近鼻子
            "finger_position": None  # 新增：食指位置
        }
        
    def setup(self):
        """设置眼睛注视方向跟踪器"""
        # 降低检测精度以提高性能
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  # 保留虹膜检测
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False  # 确保使用视频模式
        )
        
        # 初始化手部检测 - 降低精度以提高性能
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,  # 只检测一只手
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False,  # 确保使用视频模式
            model_complexity=0  # 使用最轻量级的模型
        )
        
    def detect_gaze(self, frame):
        """
        检测眼睛注视方向
        
        参数:
            frame: 输入的视频帧，如果为None则返回上一次的结果
            
        返回:
            result_dict: 包含以下信息的字典：
                - gaze_point: 注视点坐标 (x, y)
                - left_eye_position: 左眼位置 (x, y)
                - right_eye_position: 右眼位置 (x, y)
                - face_detected: 是否检测到面部
                - is_finger_near_nose: 食指是否靠近鼻子
                - finger_position: 食指位置
        """
        # 如果帧为None，返回上一次的结果
        if frame is None:
            return self.last_result
            
        result_dict = {
            "gaze_point": None,
            "left_eye_position": None,
            "right_eye_position": None,
            "face_detected": False,
            "is_finger_near_nose": False,
            "finger_position": None
        }
        
        if self.face_mesh is None:
            return result_dict
            
        # 性能优化：降低处理分辨率
        frame_height, frame_width = frame.shape[:2]
        if frame_width > 640:  # 如果分辨率过高，进行缩放
            scale_factor = 640 / frame_width
            frame_small = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
            scale_up = 1.0 / scale_factor
        else:
            frame_small = frame
            scale_up = 1.0
            
        # 转换为RGB（MediaPipe需要RGB输入）
        rgb_frame = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
        height, width = frame_small.shape[:2]
        
        # 处理帧
        results = self.face_mesh.process(rgb_frame)
        
        # 处理手部检测
        hand_results = self.hands.process(rgb_frame)
        
        # 初始化手指位置变量
        finger_position = None
        
        # 绘制人脸网格 - 仅在需要时绘制以提高性能
        if self.show_face_mesh and results.multi_face_landmarks:
            # 简化网格绘制，只绘制轮廓和虹膜
            for face_landmarks in results.multi_face_landmarks:
                # 绘制眼睛轮廓
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
                
                # 绘制虹膜
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                )
        
        # 绘制手部关键点
        if self.show_hand_landmarks and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        if not results.multi_face_landmarks:
            return result_dict
            
        result_dict["face_detected"] = True
        face_landmarks = results.multi_face_landmarks[0]
        
        # 获取左右眼和虹膜的关键点
        left_eye_landmarks = [face_landmarks.landmark[i] for i in self.LEFT_EYE_INDICES]
        right_eye_landmarks = [face_landmarks.landmark[i] for i in self.RIGHT_EYE_INDICES]
        left_iris_landmarks = [face_landmarks.landmark[i] for i in self.LEFT_IRIS_INDICES]
        right_iris_landmarks = [face_landmarks.landmark[i] for i in self.RIGHT_IRIS_INDICES]
        
        # 计算眼睛中心
        left_eye_center = self._calculate_center(left_eye_landmarks, width, height)
        right_eye_center = self._calculate_center(right_eye_landmarks, width, height)
        
        # 计算虹膜中心
        left_iris_center = self._calculate_center(left_iris_landmarks, width, height)
        right_iris_center = self._calculate_center(right_iris_landmarks, width, height)
        
        # 如果使用了缩放，将坐标转换回原始尺寸
        if scale_up != 1.0:
            left_eye_center = (int(left_eye_center[0] * scale_up), int(left_eye_center[1] * scale_up))
            right_eye_center = (int(right_eye_center[0] * scale_up), int(right_eye_center[1] * scale_up))
            left_iris_center = (int(left_iris_center[0] * scale_up), int(left_iris_center[1] * scale_up))
            right_iris_center = (int(right_iris_center[0] * scale_up), int(right_iris_center[1] * scale_up))
        
        # 计算注视方向向量
        left_gaze_vector = self._calculate_gaze_vector(left_eye_center, left_iris_center)
        right_gaze_vector = self._calculate_gaze_vector(right_eye_center, right_iris_center)
        
        # 合并左右眼的注视向量
        gaze_vector = self._combine_gaze_vectors(left_gaze_vector, right_gaze_vector)
        
        # 将注视向量映射到屏幕坐标
        gaze_point = self._map_gaze_to_screen(gaze_vector, frame_width, frame_height)
        
        # 检测食指是否靠近鼻子
        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            
            # 获取食指指尖位置（食指指尖是索引8）
            index_finger_tip = hand_landmarks.landmark[8]
            finger_position = (int(index_finger_tip.x * width), int(index_finger_tip.y * height))
            
            # 如果使用了缩放，将坐标转换回原始尺寸
            if scale_up != 1.0:
                finger_position = (int(finger_position[0] * scale_up), int(finger_position[1] * scale_up))
                
            result_dict["finger_position"] = finger_position
            
            # 计算食指与鼻子的距离
            nose_tip = face_landmarks.landmark[4]
            nose_position = (int(nose_tip.x * width * scale_up), int(nose_tip.y * height * scale_up))
            distance = np.sqrt((finger_position[0] - nose_position[0])**2 + 
                              (finger_position[1] - nose_position[1])**2)
            
            # 判断食指是否靠近鼻子
            result_dict["is_finger_near_nose"] = distance < self.finger_nose_threshold
            
        # 在调试模式下绘制眼睛和注视方向
        self._draw_debug_info(frame, left_eye_center, right_eye_center, 
                             left_iris_center, right_iris_center, gaze_point, finger_position)
        
        # 更新结果字典
        result_dict["gaze_point"] = gaze_point
        result_dict["left_eye_position"] = left_eye_center
        result_dict["right_eye_position"] = right_eye_center
        
        # 保存结果以便下次使用
        self.last_result = result_dict
        
        return result_dict
        
    def _calculate_center(self, landmarks, width, height):
        """计算关键点的中心位置"""
        x_sum = sum(landmark.x for landmark in landmarks)
        y_sum = sum(landmark.y for landmark in landmarks)
        center_x = int(x_sum / len(landmarks) * width)
        center_y = int(y_sum / len(landmarks) * height)
        return (center_x, center_y)
        
    def _calculate_gaze_vector(self, eye_center, iris_center):
        """计算注视向量"""
        return (iris_center[0] - eye_center[0], iris_center[1] - eye_center[1])
        
    def _combine_gaze_vectors(self, left_vector, right_vector):
        """合并左右眼的注视向量"""
        return ((left_vector[0] + right_vector[0]) / 2, 
                (left_vector[1] + right_vector[1]) / 2)
                
    def _map_gaze_to_screen(self, gaze_vector, width, height):
        """将注视向量映射到屏幕坐标"""
        # 这里使用简单的线性映射，实际应用中可能需要更复杂的映射方法
        # 例如校准过程和非线性映射
        
        # 缩放因子，可以通过校准调整
        scale_x = 10.0
        scale_y = 10.0
        
        # 屏幕中心
        center_x = width / 2
        center_y = height / 2
        
        # 计算屏幕上的注视点
        screen_x = center_x + gaze_vector[0] * scale_x
        screen_y = center_y + gaze_vector[1] * scale_y
        
        # 确保坐标在屏幕范围内
        screen_x = max(0, min(width, screen_x))
        screen_y = max(0, min(height, screen_y))
        
        return (int(screen_x), int(screen_y))
    
    def _draw_debug_info(self, frame, left_eye_center, right_eye_center, 
                        left_iris_center, right_iris_center, gaze_point, finger_position=None):
        """绘制调试信息"""
        # 绘制眼睛中心
        cv2.circle(frame, left_eye_center, 3, (0, 255, 0), -1)
        cv2.circle(frame, right_eye_center, 3, (0, 255, 0), -1)
        
        # 绘制虹膜中心
        cv2.circle(frame, left_iris_center, 3, (255, 0, 0), -1)
        cv2.circle(frame, right_iris_center, 3, (255, 0, 0), -1)
        
        # 绘制注视点
        if gaze_point is not None:
            cv2.circle(frame, gaze_point, 10, (0, 0, 255), -1)
            
        # 绘制食指位置和状态
        if finger_position:
            # 使用is_finger_near_nose
            is_near_nose = self.last_result.get("is_finger_near_nose", False)
            color = (0, 255, 0) if is_near_nose else (255, 0, 255)
            cv2.circle(frame, finger_position, 8, color, -1)
            
            # 如果食指靠近鼻子，显示发射文本 - 使用英文替代中文
            if is_near_nose:
                cv2.putText(frame, "FIRE!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
    def calibrate(self, frame, target_points):
        """
        校准眼睛追踪器
        
        参数:
            frame: 输入的视频帧
            target_points: 校准目标点列表
        """
        # 这里可以实现校准逻辑
        # 例如，让用户注视屏幕上的几个点，然后调整映射参数
        pass
        
    def cleanup(self):
        """清理资源"""
        if self.face_mesh is not None:
            self.face_mesh.close()
        if self.hands is not None:
            self.hands.close() 