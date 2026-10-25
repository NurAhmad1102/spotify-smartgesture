# hand_detector.py
"""
MediaPipe Hands and Face Detection module with Long-Distance (1-2m) Smart Intent Evaluation.
"""

import cv2
import mediapipe as mp
import logging
import math
import time
from typing import Tuple, List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

class HandMotionTracker:
    def __init__(self, smoothing: float = 0.6):
        """
        Tracks hand motion velocity using exponential moving average (EMA).
        """
        self.smoothing = smoothing
        self.prev_x: Optional[float] = None
        self.prev_y: Optional[float] = None
        self.prev_time: float = time.time()
        self.smoothed_velocity: float = 0.0

    def update(self, curr_x: float, curr_y: float) -> float:
        curr_time = time.time()
        dt = curr_time - self.prev_time
        
        if self.prev_x is None or dt <= 0.0:
            self.prev_x = curr_x
            self.prev_y = curr_y
            self.prev_time = curr_time
            return 0.0

        distance = math.hypot(curr_x - self.prev_x, curr_y - self.prev_y)
        inst_velocity = distance / dt
        
        self.smoothed_velocity = (self.smoothing * self.smoothed_velocity) + ((1.0 - self.smoothing) * inst_velocity)
        
        self.prev_x = curr_x
        self.prev_y = curr_y
        self.prev_time = curr_time
        
        return self.smoothed_velocity

    def reset(self) -> None:
        self.prev_x = None
        self.prev_y = None
        self.smoothed_velocity = 0.0


class HandDetector:
    def __init__(self, 
                 max_num_hands: int = 1,
                 min_detection_confidence: float = 0.45,
                 min_tracking_confidence: float = 0.45):
        """
        Initializes MediaPipe Hands and Face Detector optimized for 1-2m range.
        """
        logger.info("Initializing MediaPipe Hands & Face Detector for 1-2m distance...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Initialize Face Detector for Chin/Face Contact Exclusion
        self.mp_face = mp.solutions.face_detection
        self.face_detector = self.mp_face.FaceDetection(min_detection_confidence=0.45)
        
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.motion_tracker = HandMotionTracker()

    def find_hands(self, frame: cv2.Mat, draw: bool = True) -> Tuple[cv2.Mat, List[Dict[str, Any]], List[Tuple[float, float, float, float]]]:
        """
        Detects hands and faces in the frame.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hands
        hand_results = self.hands.process(rgb_frame)
        
        # Process face
        face_results = self.face_detector.process(rgb_frame)
        face_boxes = []
        
        if face_results.detections:
            for detection in face_results.detections:
                bbox = detection.location_data.relative_bounding_box
                face_boxes.append((bbox.xmin, bbox.ymin, bbox.width, bbox.height))

        detected_hands = []
        
        if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
            h, w, _ = frame.shape
            
            for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
                landmarks_pixel = []
                landmarks_normalized = []
                
                for lm in hand_landmarks.landmark:
                    landmarks_normalized.append((lm.x, lm.y, lm.z))
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks_pixel.append((cx, cy))
                
                label = handedness.classification[0].label
                score = handedness.classification[0].score
                
                # Update velocity using wrist (landmark 0)
                wrist_norm = landmarks_normalized[0]
                velocity = self.motion_tracker.update(wrist_norm[0], wrist_norm[1])
                
                detected_hands.append({
                    "landmarks_pixel": landmarks_pixel,
                    "landmarks_normalized": landmarks_normalized,
                    "label": label,
                    "score": score,
                    "velocity": velocity
                })
                
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
        else:
            self.motion_tracker.reset()
                    
        return frame, detected_hands, face_boxes

    @staticmethod
    def evaluate_intent(hand_data: Dict[str, Any], face_boxes: List[Tuple[float, float, float, float]]) -> Tuple[bool, str]:
        """
        Evaluates physical intent rules with dynamic distance scaling:
        1. Spatial Boundary (wrist y < SPATIAL_ZONE_MAX_Y)
        2. Dynamic Chin/Face Proximity Exclusion (scaled relative to face size)
        3. Motion Velocity Filter (hand movement speed < MAX_MOTION_VELOCITY)
        4. Upright Palm Orientation Check
        """
        landmarks_norm = hand_data["landmarks_normalized"]
        wrist = landmarks_norm[0]        # (x, y, z)
        middle_mcp = landmarks_norm[9]   # (x, y, z)
        velocity = hand_data.get("velocity", 0.0)
        
        # Rule 1: Spatial Boundary Check (Keyboard Area Exclusion)
        if wrist[1] >= config.SPATIAL_ZONE_MAX_Y:
            return False, "Keyboard Zone"

        # Rule 2: Dynamic Chin/Face Contact Exclusion Check
        # Margin scales dynamically with face height so distance doesn't block open-air hands at 1-2m
        for (fx, fy, fw, fh) in face_boxes:
            margin = fh * getattr(config, 'FACE_CLEARANCE_RATIO', 0.45)
            exp_xmin = fx - margin
            exp_xmax = fx + fw + margin
            exp_ymin = fy - (margin * 0.3)
            exp_ymax = fy + fh + (margin * 1.2)  # Covers chin & neck area
            
            for lm_idx in [0, 4, 8, 12, 16, 20, 9]:
                lx, ly, _ = landmarks_norm[lm_idx]
                if exp_xmin <= lx <= exp_xmax and exp_ymin <= ly <= exp_ymax:
                    return False, "Chin/Face Rest"

        # Rule 3: Motion Velocity Check
        if velocity > config.MAX_MOTION_VELOCITY:
            return False, "Hand Moving"

        # Rule 4: Palm Upright Orientation Check
        # Middle finger MCP (landmark 9) must be clearly above wrist (landmark 0)
        if wrist[1] <= middle_mcp[1]:
            return False, "Palm Tilted"

        return True, "Intent Valid"

    def close(self) -> None:
        """
        Releases detector resources.
        """
        logger.info("Closing MediaPipe Hands & Face detector.")
        self.hands.close()
        self.face_detector.close()
