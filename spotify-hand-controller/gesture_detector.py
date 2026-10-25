# gesture_detector.py
"""
Gesture recognition, hand engagement gating, and stabilization module.
"""

import time
import logging
from typing import Optional, Dict, Any, Tuple
import config

logger = logging.getLogger(__name__)

class HandLabelStabilizer:
    def __init__(self, window_size: int = 15):
        """
        Initializes the HandLabelStabilizer to smooth Left/Right hand classification swaps.
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
        - 4 fingers -> Previous Track
        - 5 fingers -> Volume Up
        
        Left Hand (Physical, detected as 'Left' on mirrored feed) -> Advanced Settings:
        - 1 finger -> Like Song
        - 2 fingers -> Shuffle
        - 4 fingers -> Enable Repeat
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
        Initializes the GestureStabilizer with a 1-Second Raised Hand Engagement Gate.
        """
        self.stabilization_time = stabilization_ms / 1000.0
        self.cooldown_time = cooldown_ms / 1000.0
        self.volume_repeat_interval = volume_repeat_ms / 1000.0
        self.hand_raised_gate_time = getattr(config, 'HAND_RAISED_GATE_MS', 1000) / 1000.0
        
        self.hand_raised_start_time: float = 0.0
        self.current_gesture: Optional[str] = None
        self.gesture_start_time: float = 0.0
        
        self.last_executed_gesture: Optional[str] = None
        self.cooldown_end_time: float = 0.0
        self.last_volume_trigger_time: float = 0.0

    def process(self, 
                gesture: Optional[str], 
                is_intent_valid: bool = True, 
                standby_reason: str = "Ready (No Gesture)") -> Tuple[Optional[str], str]:
        """
        Processes gesture inputs subject to the 1-Second Raised Hand Engagement Gate.
        """
        current_time = time.time()
            
        # 1. Standby Check (Keyboard area, Face/Chin rest, Motion, or No Hand)
        if not is_intent_valid or gesture is None:
            self.hand_raised_start_time = 0.0
            self.current_gesture = None
            self.gesture_start_time = current_time
            self.last_executed_gesture = None
            self.last_volume_trigger_time = 0.0
            return None, f"Standby ({standby_reason})"
            
        # 2. Stage 1: 1-Second Raised Hand Engagement Gate
        if self.hand_raised_start_time == 0.0:
            self.hand_raised_start_time = current_time
            
        raised_duration = current_time - self.hand_raised_start_time
        if raised_duration < self.hand_raised_gate_time:
            return None, f"Raising Hand ({raised_duration:.1f}s/1.0s)"
            
        # 3. Stage 2: Hand Engaged - Gesture Transition
        if gesture != self.current_gesture:
            logger.info(f"Gesture changed: {self.current_gesture} -> {gesture}. Starting stabilization.")
            self.current_gesture = gesture
            self.gesture_start_time = current_time
            self.last_volume_trigger_time = 0.0
            return None, f"Stabilizing {gesture}..."
            
        # 4. Gesture Constant - Check Hold Duration
        held_duration = current_time - self.gesture_start_time
        
        if held_duration >= self.stabilization_time:
            is_volume = gesture in ["Volume Up", "Volume Down"]
            
            if is_volume:
                if self.last_volume_trigger_time == 0.0:
                    logger.info(f"Volume gesture stabilized! Triggering: {gesture}")
                    self.last_volume_trigger_time = current_time
                    self.last_executed_gesture = gesture
                    self.cooldown_end_time = current_time + self.volume_repeat_interval
                    return gesture, f"Triggered {gesture}!"
                elif current_time >= self.cooldown_end_time:
                    self.cooldown_end_time = current_time + self.volume_repeat_interval
                    return gesture, f"Stepping {gesture}..."
                else:
                    remaining_repeat = self.cooldown_end_time - current_time
                    return None, f"Stepping {gesture} ({remaining_repeat:.1f}s wait)"
            else:
                if current_time < self.cooldown_end_time:
                    remaining = self.cooldown_end_time - current_time
                    return None, f"Cooldown ({remaining:.1f}s)"
                    
                if gesture == self.last_executed_gesture:
                    return None, f"Active {gesture} (Hold)"
                    
                logger.info(f"Gesture stabilized! Triggering: {gesture}")
                self.last_executed_gesture = gesture
                self.cooldown_end_time = current_time + self.cooldown_time
                return gesture, f"Triggered {gesture}!"
            
        return None, f"Stabilizing {gesture} ({held_duration:.2f}s)"

    @property
    def engagement_progress(self) -> float:
        """
        Returns 0.0 to 1.0 representing hand engagement progress (1.0s gate).
        """
        if self.hand_raised_start_time == 0.0:
            return 0.0
        current_time = time.time()
        elapsed = current_time - self.hand_raised_start_time
        return max(0.0, min(1.0, elapsed / self.hand_raised_gate_time))

    @property
    def cooldown_progress(self) -> float:
        """
        Returns 0.0 to 1.0 representing cooldown progress.
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
