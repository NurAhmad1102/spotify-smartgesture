# config.py
"""
Configuration module containing all constant values, thresholds, and mappings.
"""

# Camera Settings (Upgraded to 720p HD for superior 1-2m long-distance detection)
CAMERA_INDEX = 1  # 0 as default camera, 1 as second camera, etc.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FLIP_HORIZONTAL = True  # Mirror the camera input for natural interaction

# MediaPipe Hand Detection Settings (Optimized for 1-2m range)
MAX_NUM_HANDS = 1
MODEL_COMPLEXITY = 1
MIN_DETECTION_CONFIDENCE = 0.45  # Lowered to 0.45 to catch small hands at 1-2m distance
MIN_TRACKING_CONFIDENCE = 0.45   # Lowered to 0.45 for continuous long-distance tracking

# Smart Intent & Anti-False-Positive Parameters
SPATIAL_ZONE_MAX_Y = 0.60       # Hand wrist must be above y=0.60 (ignores lower 40% keyboard area)
HAND_RAISED_GATE_MS = 300       # Reduced to 300ms (0.3s) for near-instant response
MAX_MOTION_VELOCITY = 0.15      # Motion velocity threshold adjusted for 720p scaling
FACE_CLEARANCE_RATIO = 0.45     # Dynamic face clearance margin (scaled to face size)

# Gesture Stabilization & Cooldown
GESTURE_STABILIZATION_MS = 700
GESTURE_COOLDOWN_MS = 1000
VOLUME_REPEAT_INTERVAL_MS = 300  # Interval (in ms) to repeat volume up/down while held

# Gestures configuration
GESTURE_VOLUME_DOWN = 0
GESTURE_PLAY_PAUSE = 1
GESTURE_NEXT_TRACK = 2
GESTURE_PREV_TRACK = 4
GESTURE_VOLUME_UP = 5

# HUD Color System (BGR Format)
COLOR_BACKGROUND = (30, 30, 30)        # Dark theme panel background
COLOR_BORDER = (80, 80, 80)            # Slate grey panel border
COLOR_TEXT_PRIMARY = (240, 240, 240)    # Off-white for general text
COLOR_TEXT_MUTED = (160, 160, 160)      # Muted grey for subtext
COLOR_ACCENT = (29, 185, 84)            # Spotify Green for active/trigger states
COLOR_COOLDOWN = (0, 165, 255)          # Orange for cooldown/timer states
COLOR_WARNING = (0, 0, 255)             # Red for alerts/warnings
COLOR_STANDBY = (120, 120, 120)         # Grey for standby state
COLOR_LINE = (70, 70, 70)               # Neutral grey for boundary line
