# overlay.py
"""
HUD Overlay drawing module for creating a premium glassmorphic camera dashboard.
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional
import config

class HUDOverlay:
    @staticmethod
    def draw_glass_card(
        img: np.ndarray, 
        top_left: tuple, 
        bottom_right: tuple, 
        bg_color: tuple = config.COLOR_BACKGROUND, 
        border_color: tuple = config.COLOR_BORDER, 
        alpha: float = 0.75, 
        border_thickness: int = 1
    ) -> None:
        """
        Draws a semi-transparent glassmorphic card on the image.
        """
        overlay = img.copy()
        cv2.rectangle(overlay, top_left, bottom_right, bg_color, cv2.FILLED)
        cv2.addWeighted(overlay, alpha, img, 1.0 - alpha, 0, img)
        cv2.rectangle(img, top_left, bottom_right, border_color, border_thickness)

    def draw(
        self, 
        frame: np.ndarray, 
        fps: float, 
        spotify_running: bool, 
        stable_label: Optional[str], 
        raw_gesture: Optional[str], 
        status_msg: str, 
        cooldown_progress: float,
        engagement_progress: float = 0.0
    ) -> np.ndarray:
        """
        Draws the full HUD display and spatial boundary line on the frame.
        """
        h, w, _ = frame.shape
        
        # 0. Draw Spatial Boundary Line (Keyboard exclusion line at y = SPATIAL_ZONE_MAX_Y)
        boundary_y = int(h * config.SPATIAL_ZONE_MAX_Y)
        cv2.line(frame, (0, boundary_y), (w, boundary_y), config.COLOR_LINE, 1)
        cv2.putText(
            frame, "KEYBOARD EXCLUSION ZONE (BELOW)", (w - 240, boundary_y + 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, config.COLOR_TEXT_MUTED, 1, cv2.LINE_AA
        )

        # Card 1: System Metrics (Top-Left)
        self.draw_glass_card(frame, (15, 15), (250, 115))
        
        cv2.putText(
            frame, "SYSTEM METRICS", (25, 33), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_MUTED, 1, cv2.LINE_AA
        )
        cv2.line(frame, (25, 40), (240, 40), config.COLOR_BORDER, 1)
        
        cv2.putText(
            frame, f"FPS: {fps:.1f}", (25, 60), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, config.COLOR_TEXT_PRIMARY, 1, cv2.LINE_AA
        )
        
        spotify_text = "Spotify: CONNECTED" if spotify_running else "Spotify: NOT RUNNING"
        spotify_color = config.COLOR_ACCENT if spotify_running else config.COLOR_WARNING
        cv2.putText(
            frame, spotify_text, (25, 85), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, spotify_color, 1, cv2.LINE_AA
        )
        dot_color = config.COLOR_ACCENT if spotify_running else config.COLOR_WARNING
        cv2.circle(frame, (230, 80), 4, dot_color, cv2.FILLED)

        # Card 2: Gesture Controller (Bottom-Left)
        self.draw_glass_card(frame, (15, 310), (310, 465))
        
        cv2.putText(
            frame, "GESTURE CONTROLLER", (25, 328), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_MUTED, 1, cv2.LINE_AA
        )
        cv2.line(frame, (25, 335), (300, 335), config.COLOR_BORDER, 1)
        
        # Hand Presence Info
        if stable_label:
            physical_hand = "Right Hand (Playback)" if stable_label == "Right" else "Left Hand (Advanced)"
            hand_text = f"Hand: {physical_hand}"
            hand_color = config.COLOR_TEXT_PRIMARY
        else:
            hand_text = "Hand: None Detected"
            hand_color = config.COLOR_TEXT_MUTED
            
        cv2.putText(
            frame, hand_text, (25, 355), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, hand_color, 1, cv2.LINE_AA
        )
        
        # Raw Gesture detected
        gesture_text = f"Gesture: {raw_gesture if raw_gesture else 'None'}"
        cv2.putText(
            frame, gesture_text, (25, 380), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, config.COLOR_TEXT_PRIMARY, 1, cv2.LINE_AA
        )
        
        # Stabilizer Status & Colors
        status_text = f"Status: {status_msg}"
        status_color = config.COLOR_TEXT_PRIMARY
        
        if "Triggered" in status_msg or "Stepping" in status_msg:
            status_color = config.COLOR_ACCENT
        elif "Cooldown" in status_msg:
            status_color = config.COLOR_COOLDOWN
        elif "Raising Hand" in status_msg:
            status_color = (255, 200, 50)
        elif "Standby" in status_msg or "Ready" in status_msg:
            status_color = getattr(config, 'COLOR_STANDBY', (120, 120, 120))
            
        cv2.putText(
            frame, status_text, (25, 405), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.52, status_color, 1, cv2.LINE_AA
        )
        
        # Progress Bar Area (at bottom of Card 2)
        bar_x1, bar_y1 = 25, 435
        bar_x2, bar_y2 = 300, 445
        
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), config.COLOR_BORDER, 1)
        
        if cooldown_progress > 0.0:
            fill_width = int((bar_x2 - bar_x1) * cooldown_progress)
            cv2.rectangle(
                frame, (bar_x1, bar_y1), (bar_x1 + fill_width, bar_y2), 
                config.COLOR_COOLDOWN, cv2.FILLED
            )
            cv2.putText(
                frame, "COOLDOWN ACTIVE", (25, 427), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, config.COLOR_COOLDOWN, 1, cv2.LINE_AA
            )
        elif 0.0 < engagement_progress < 1.0:
            fill_width = int((bar_x2 - bar_x1) * engagement_progress)
            cv2.rectangle(
                frame, (bar_x1, bar_y1), (bar_x1 + fill_width, bar_y2), 
                (255, 200, 50), cv2.FILLED
            )
            cv2.putText(
                frame, "ENGAGING HAND (INSTANT 0.3s)", (25, 427), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 200, 50), 1, cv2.LINE_AA
            )
        else:
            cv2.putText(
                frame, "SYSTEM READY", (25, 427), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, config.COLOR_ACCENT, 1, cv2.LINE_AA
            )
            
        return frame
