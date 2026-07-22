# gesture_detector.py
"""
Gesture recognition and stabilization module.
"""

import time
import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class HandLabelStabilizer:
    def __init__(self, window_size: int = 15):
        """
        Initializes the HandLabelStabilizer to smooth Left/Right hand classification swaps.
        
        Args:
            window_size: Number of frames to use in majority voting.
        """
        self.window_size = window_size
        self.history = []

    def process(self, current_label: Optional[str]) -> Optional[str]:
        """
        Processes a raw frame hand label and returns the smoothed/stabilized label.
        """
        if current_label is None:
            self.history.clear()
            return None
            
        self.history.append(current_label)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        # Perform majority voting
        left_count = self.history.count("Left")
        right_count = self.history.count("Right")
        
        return "Left" if left_count >= right_count else "Right"


class GestureDetector:
    @staticmethod
    def detect_gesture(finger_results: Dict[str, Any], hand_label: str = "Right") -> Optional[str]:
        """
        Maps finger count to actions, differentiated by handedness (2-handed mode).
        
        Right Hand (Physical, detected as 'Right' on mirrored feed) -> Playback Controls:
        - 0 fingers (Fist) -> Volume Down
        - 1 finger -> Play/Pause
        - 2 fingers -> Next Track
        - 3 fingers -> Previous Track
        - 5 fingers -> Volume Up
        
        Left Hand (Physical, detected as 'Left' on mirrored feed) -> Advanced Settings:
        - 1 finger -> Like Song
        - 2 fingers -> Shuffle
        - 3 fingers -> Enable Repeat
        
        Args:
            finger_results: Dictionary containing 'count' and 'fingers' list.
            hand_label: The stabilized hand classification label ("Left" or "Right").
            
        Returns:
            Optional[str]: Name of the gesture action, or None if unmapped.
        """
        count = finger_results["count"]
        
        if hand_label == "Right":
            # --- Physical Right Hand (Playback Controls) ---
            if count == 0:
                return "Volume Down"
            elif count == 1:
                return "Play/Pause"
            elif count == 2:
                return "Next Track"
            elif count == 4:
                return "Previous Track"
            elif count == 5:
                return "Volume Up"
        else:
            # --- Physical Left Hand (Advanced Spotify Hotkeys) ---
            if count == 1:
                return "Like Song"
            elif count == 2:
                return "Shuffle"
            elif count == 4:
                return "Enable Repeat"
                
        return None





class GestureStabilizer:
    def __init__(self, stabilization_ms: int = 700, cooldown_ms: int = 1000, volume_repeat_ms: int = 300):
        """
        Initializes the GestureStabilizer.
        
        Args:
            stabilization_ms: Minimum duration in ms the gesture must be stable.
            cooldown_ms: Cooldown duration in ms after triggering a regular action.
            volume_repeat_ms: Interval in ms to repeat volume changes while held.
        """
        self.stabilization_time = stabilization_ms / 1000.0
        self.cooldown_time = cooldown_ms / 1000.0
        self.volume_repeat_interval = volume_repeat_ms / 1000.0
        
        self.current_gesture: Optional[str] = None
        self.gesture_start_time: float = 0.0
        
        self.last_executed_gesture: Optional[str] = None
        self.cooldown_end_time: float = 0.0
        self.last_volume_trigger_time: float = 0.0

    def process(self, gesture: Optional[str]) -> Tuple[Optional[str], str]:
        """
        Processes a raw detected gesture and handles stabilization, cooldown, and repeat/stepping logic.
        
        Args:
            gesture: The raw gesture string detected in the current frame.
            
        Returns:
            Tuple[Optional[str], str]:
                - The gesture action name to execute (if triggered, else None).
                - A status string describing the stabilizer state.
        """
        current_time = time.time()
            
        # 1. No Gesture/Hand Case
        if gesture is None:
            self.current_gesture = None
            self.gesture_start_time = current_time
            self.last_executed_gesture = None
            self.last_volume_trigger_time = 0.0
            return None, "Ready (No Gesture)"
            
        # 2. Gesture Transition
        if gesture != self.current_gesture:
            logger.info(f"Gesture changed: {self.current_gesture} -> {gesture}. Starting stabilization.")
            self.current_gesture = gesture
            self.gesture_start_time = current_time
            self.last_volume_trigger_time = 0.0
            return None, f"Stabilizing {gesture}..."
            
        # 3. Gesture Constant - Check Hold Duration
        held_duration = current_time - self.gesture_start_time
        
        if held_duration >= self.stabilization_time:
            is_volume = gesture in ["Volume Up", "Volume Down"]
            
            if is_volume:
                # First trigger of volume action
                if self.last_volume_trigger_time == 0.0:
                    logger.info(f"Volume gesture stabilized! Triggering: {gesture}")
                    self.last_volume_trigger_time = current_time
                    self.last_executed_gesture = gesture
                    self.cooldown_end_time = current_time + self.volume_repeat_interval
                    return gesture, f"Triggered {gesture}!"
                
                # Stepping repeats
                elif current_time >= self.cooldown_end_time:
                    self.cooldown_end_time = current_time + self.volume_repeat_interval
                    return gesture, f"Stepping {gesture}..."
                
                # Within repeat interval wait window
                else:
                    remaining_repeat = self.cooldown_end_time - current_time
                    return None, f"Stepping {gesture} ({remaining_repeat:.1f}s wait)"
            else:
                # Regular gestures check normal cooldown
                if current_time < self.cooldown_end_time:
                    remaining = self.cooldown_end_time - current_time
                    return None, f"Cooldown ({remaining:.1f}s)"
                    
                # Prevent repeated execution of the same gesture without resetting hand
                if gesture == self.last_executed_gesture:
                    return None, f"Active {gesture} (Hold)"
                    
                # Trigger Action
                logger.info(f"Gesture stabilized! Triggering: {gesture}")
                self.last_executed_gesture = gesture
                self.cooldown_end_time = current_time + self.cooldown_time
                return gesture, f"Triggered {gesture}!"
            
        return None, f"Stabilizing {gesture} ({held_duration:.2f}s)"

    @property
    def cooldown_progress(self) -> float:
        """
        Returns the progress of the current cooldown as a float between 0.0 and 1.0.
        0.0 means no cooldown or cooldown completed.
        1.0 means cooldown just started.
        """
        current_time = time.time()
        if current_time >= self.cooldown_end_time:
            return 0.0
            
        is_volume = self.current_gesture in ["Volume Up", "Volume Down"]
        total_duration = self.volume_repeat_interval if is_volume else self.cooldown_time
        
        if total_duration <= 0.0:
            return 0.0
            
        remaining = self.cooldown_end_time - current_time
        return max(0.0, min(1.0, remaining / total_duration))

