# hand_detector.py
"""
MediaPipe Hands integration module for detecting hand landmarks.
"""

import cv2
import mediapipe as mp
import logging
from typing import Tuple, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class HandDetector:
    def __init__(self, 
                 max_num_hands: int = 1,
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.7):
        """
        Initializes the MediaPipe Hands detector.
        
        Args:
            max_num_hands: Maximum number of hands to detect.
            min_detection_confidence: Minimum confidence score for detection to be considered successful.
            min_tracking_confidence: Minimum confidence score for tracking.
        """
        logger.info("Initializing MediaPipe Hands detector...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def find_hands(self, frame: cv2.Mat, draw: bool = True) -> Tuple[cv2.Mat, List[Dict[str, Any]]]:
        """
        Detects hands in a BGR frame and returns the processed frame and landmarks.
        
        Args:
            frame: The input image from the webcam (BGR).
            draw: Whether to draw landmarks on the returned frame.
            
        Returns:
            Tuple[cv2.Mat, List[Dict[str, Any]]]: The modified frame and a list of detected hands.
                Each hand dict contains:
                - 'landmarks_pixel': List of (cx, cy) in image pixel coordinates.
                - 'landmarks_normalized': List of (x, y, z) normalized coordinates.
                - 'label': Handedness label ("Left" or "Right").
                - 'score': Handedness confidence score.
        """
        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.hands.process(rgb_frame)
        
        detected_hands = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            h, w, _ = frame.shape
            
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                landmarks_pixel = []
                landmarks_normalized = []
                
                # Extract landmark coordinates
                for lm in hand_landmarks.landmark:
                    # Normalized [0.0, 1.0]
                    landmarks_normalized.append((lm.x, lm.y, lm.z))
                    # Convert to pixel space
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks_pixel.append((cx, cy))
                
                # Get handedness classification
                # MediaPipe gives label relative to the physical hand.
                label = handedness.classification[0].label
                score = handedness.classification[0].score
                
                detected_hands.append({
                    "landmarks_pixel": landmarks_pixel,
                    "landmarks_normalized": landmarks_normalized,
                    "label": label,
                    "score": score
                })
                
                if draw:
                    # Draw default landmarks and connection lines
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
        return frame, detected_hands

    def close(self) -> None:
        """
        Releases MediaPipe Hands resources.
        """
        logger.info("Closing MediaPipe Hands detector.")
        self.hands.close()
