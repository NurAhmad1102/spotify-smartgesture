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
        # Take a copy for blending
        overlay = img.copy()
        cv2.rectangle(overlay, top_left, bottom_right, bg_color, cv2.FILLED)
        
        # Blend the solid card with the original image
        cv2.addWeighted(overlay, alpha, img, 1.0 - alpha, 0, img)
        
        # Draw the card border
        cv2.rectangle(img, top_left, bottom_right, border_color, border_thickness)

    def draw(
        self, 
        frame: np.ndarray, 
        fps: float, 
        spotify_running: bool, 
        stable_label: Optional[str], 
        raw_gesture: Optional[str], 
        status_msg: str, 
        cooldown_progress: float
    ) -> np.ndarray:
        """
        Draws the full HUD display on the frame.
        
        Args:
            frame: The input image frame (BGR).
            fps: Current frame rate.
            spotify_running: Whether Spotify is running.
            stable_label: The stabilized hand classification label ("Left", "Right", or None).
            raw_gesture: Current raw gesture string, or None.
            status_msg: Current status string from the stabilizer.
            cooldown_progress: Float between 0.0 and 1.0.
            
        Returns:
            np.ndarray: The frame with the HUD drawn on it.
        """
        # Card 1: System Metrics (Top-Left)
        # Coordinates: (15, 15) to (250, 115)
        self.draw_glass_card(frame, (15, 15), (250, 115))
        
        # Title Header
        cv2.putText(
            frame, "SYSTEM METRICS", (25, 33), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_MUTED, 1, cv2.LINE_AA
        )
        # Separator line
        cv2.line(frame, (25, 40), (240, 40), config.COLOR_BORDER, 1)
        
        # FPS Label
        cv2.putText(
            frame, f"FPS: {fps:.1f}", (25, 60), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, config.COLOR_TEXT_PRIMARY, 1, cv2.LINE_AA
        )
        
        # Spotify Status Label
        spotify_text = "Spotify: CONNECTED" if spotify_running else "Spotify: NOT RUNNING"
        spotify_color = config.COLOR_ACCENT if spotify_running else config.COLOR_WARNING
        cv2.putText(
            frame, spotify_text, (25, 85), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, spotify_color, 1, cv2.LINE_AA
        )
        # Tiny indicator dot next to Spotify Status
        dot_color = config.COLOR_ACCENT if spotify_running else config.COLOR_WARNING
        cv2.circle(frame, (230, 80), 4, dot_color, cv2.FILLED)

        # Card 2: Gesture Controller (Bottom-Left)
        # Coordinates: (15, 310) to (310, 465)
        self.draw_glass_card(frame, (15, 310), (310, 465))
        
        # Title Header
        cv2.putText(
            frame, "GESTURE CONTROLLER", (25, 328), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, config.COLOR_TEXT_MUTED, 1, cv2.LINE_AA
        )
        # Separator line
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
        
        # Stabilizer Status
        status_text = f"Status: {status_msg}"
        status_color = config.COLOR_TEXT_PRIMARY
        
        if "Triggered" in status_msg or "Stepping" in status_msg:
            status_color = config.COLOR_ACCENT
        elif "Cooldown" in status_msg:
            status_color = config.COLOR_COOLDOWN
        elif "No Hand" in status_msg or "Ready" in status_msg:
            status_color = config.COLOR_TEXT_MUTED
            
        cv2.putText(
            frame, status_text, (25, 405), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 1, cv2.LINE_AA
        )
        
        # Cooldown Progress Bar (at the bottom of Card 2)
        # Coordinates: (25, 440) to (300, 450)
        bar_x1, bar_y1 = 25, 435
        bar_x2, bar_y2 = 300, 445
        
        # Draw background bar (border outline)
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), config.COLOR_BORDER, 1)
        
        if cooldown_progress > 0.0:
            # Draw remaining cooldown bar (shrinks from right to left)
            fill_width = int((bar_x2 - bar_x1) * cooldown_progress)
            cv2.rectangle(
                frame, 
                (bar_x1, bar_y1), 
                (bar_x1 + fill_width, bar_y2), 
                config.COLOR_COOLDOWN, 
                cv2.FILLED
            )
            # Label
            cv2.putText(
                frame, "COOLDOWN ACTIVE", (25, 427), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, config.COLOR_COOLDOWN, 1, cv2.LINE_AA
            )
        else:
            # Ready indicator
            cv2.putText(
                frame, "SYSTEM READY", (25, 427), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, config.COLOR_ACCENT, 1, cv2.LINE_AA
            )
            
        return frame
