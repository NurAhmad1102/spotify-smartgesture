# config.py
"""
Configuration module containing all constant values, thresholds, and mappings.
"""

# Camera Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FLIP_HORIZONTAL = True  # Mirror the camera input for natural interaction

# MediaPipe Hand Detection Settings
MAX_NUM_HANDS = 1
MODEL_COMPLEXITY = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Gesture Stabilization & Cooldown
GESTURE_STABILIZATION_MS = 700
GESTURE_COOLDOWN_MS = 1000
VOLUME_REPEAT_INTERVAL_MS = 300  # Interval (in ms) to repeat volume up/down while held

# Gestures configuration
# 0 fingers = Closed fist -> Volume Down
# 1 finger = Play/Pause
# 2 fingers = Next Track
# 3 fingers = Previous Track
# 5 fingers = Volume Up
GESTURE_VOLUME_DOWN = 0
GESTURE_PLAY_PAUSE = 1
GESTURE_NEXT_TRACK = 2
GESTURE_PREV_TRACK = 3
GESTURE_VOLUME_UP = 5

# HUD Color System (BGR Format)
# Using a sleek premium color palette
COLOR_BACKGROUND = (30, 30, 30)       # Dark theme panel background
COLOR_BORDER = (80, 80, 80)           # Slate grey panel border
COLOR_TEXT_PRIMARY = (240, 240, 240)   # Off-white for general text
COLOR_TEXT_MUTED = (160, 160, 160)     # Muted grey for subtext
COLOR_ACCENT = (29, 185, 84)           # Spotify Green for active/trigger states
COLOR_COOLDOWN = (0, 165, 255)         # Orange for cooldown/timer states
COLOR_WARNING = (0, 0, 255)            # Red for alerts/warnings
