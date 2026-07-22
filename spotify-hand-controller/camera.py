# camera.py
"""
Webcam management module using OpenCV.
"""

import cv2
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, index: int = 0, width: int = 640, height: int = 480):
        """
        Initializes the Camera settings.
        
        Args:
            index: The device index of the webcam.
            width: The desired capture width.
            height: The desired capture height.
        """
        self.index = index
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        """
        Opens the webcam and configures dimensions.
        
        Returns:
            bool: True if webcam is opened successfully, False otherwise.
        """
        logger.info(f"Starting camera at index {self.index}...")
        self.cap = cv2.VideoCapture(self.index)
        
        if not self.cap.isOpened():
            logger.error(f"Could not open camera at index {self.index}.")
            self.cap = None
            return False
        
        # Configure width and height
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Log actual width/height (camera might fall back to defaults)
        actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.info(f"Camera started. Resolution: {actual_w}x{actual_h}")
        return True

    def read_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """
        Captures a frame from the webcam.
        
        Returns:
            Tuple[bool, Optional[cv2.Mat]]: Success flag and the frame image.
        """
        if self.cap is None or not self.cap.isOpened():
            logger.warning("Attempted to read frame from closed camera.")
            return False, None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to grab frame.")
            return False, None
            
        return True, frame

    def release(self) -> None:
        """
        Releases the webcam resources.
        """
        if self.cap is not None:
            logger.info("Releasing camera resource.")
            self.cap.release()
            self.cap = None
