# utils.py
"""
Utility functions, including FPS calculation and process status checks.
"""

import cv2
import time
import subprocess
import logging

logger = logging.getLogger(__name__)

class FPSCounter:
    def __init__(self):
        """
        Initializes the FPS counter.
        """
        self.prev_time = time.time()
        self.fps = 0.0

    def update(self) -> float:
        """
        Calculates and returns the current FPS based on the time elapsed.
        """
        curr_time = time.time()
        time_diff = curr_time - self.prev_time
        if time_diff > 0:
            self.fps = 1.0 / time_diff
        self.prev_time = curr_time
        return self.fps


def is_spotify_running() -> bool:
    """
    Checks if the Spotify Desktop process is currently running on Windows.
    
    Returns:
        bool: True if 'Spotify.exe' is running, False otherwise.
    """
    try:
        # Run tasklist command filtering by Spotify.exe
        output = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq Spotify.exe" /NH',
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )
        # Check if Spotify process is listed in the output
        return "Spotify.exe" in output
    except Exception as e:
        logger.debug(f"Error checking Spotify process: {e}")
        return False
