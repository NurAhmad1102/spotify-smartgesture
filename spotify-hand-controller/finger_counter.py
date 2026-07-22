# finger_counter.py
"""
Finger counting logic based on MediaPipe hand landmarks.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class FingerCounter:
    @staticmethod
    def count_fingers(hand_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines which fingers are raised based on landmark positions.
        
        Args:
            hand_data: A dictionary containing hand information from HandDetector.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'count': (int) total number of raised fingers (0-5).
                - 'fingers': (List[bool]) True/False status for [thumb, index, middle, ring, pinky].
        """
        landmarks = hand_data["landmarks_pixel"]
        label = hand_data["label"]  # "Left" or "Right" as classified by MediaPipe

        # A valid hand must have exactly 21 landmarks
        if len(landmarks) < 21:
            logger.warning("Incomplete hand landmarks data received.")
            return {"count": 0, "fingers": [False] * 5}

        # Index, Middle, Ring, Pinky state list
        # We check if the tip is above (smaller y) the PIP joint.
        # Tips: Index (8), Middle (12), Ring (16), Pinky (20)
        # PIPs: Index (6), Middle (10), Ring (14), Pinky (18)
        fingers_up = [False] * 5

        # Index Finger
        if landmarks[8][1] < landmarks[6][1]:
            fingers_up[1] = True

        # Middle Finger
        if landmarks[12][1] < landmarks[10][1]:
            fingers_up[2] = True

        # Ring Finger
        if landmarks[16][1] < landmarks[14][1]:
            fingers_up[3] = True

        # Pinky Finger
        if landmarks[20][1] < landmarks[18][1]:
            fingers_up[4] = True

        # Thumb Finger
        # We compare the X coordinate of the thumb tip (4) to the thumb MCP joint (2).
        # For a "Right" hand (thumb points left in image): Tip X < MCP X means extended
        # For a "Left" hand (thumb points right in image): Tip X > MCP X means extended
        if label == "Right":
            if landmarks[4][0] < landmarks[2][0]:
                fingers_up[0] = True
        else:  # "Left"
            if landmarks[4][0] > landmarks[2][0]:
                fingers_up[0] = True

        count = sum(fingers_up)
        return {
            "count": count,
            "fingers": fingers_up
        }
