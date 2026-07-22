# main.py
"""
Spotify Hand Gesture Controller
Main application entry point.
"""

import cv2
import logging
import sys
from camera import Camera
from hand_detector import HandDetector
from finger_counter import FingerCounter
from gesture_detector import GestureDetector, GestureStabilizer, HandLabelStabilizer
from spotify_controller import SpotifyController
from overlay import HUDOverlay
from utils import FPSCounter, is_spotify_running
import config

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Main")

def main():
    logger.info("Initializing Spotify Hand Gesture Controller...")
    
    # Initialize Camera
    camera = Camera(
        index=config.CAMERA_INDEX,
        width=config.FRAME_WIDTH,
        height=config.FRAME_HEIGHT
    )
    
    # Initialize Hand Detector
    detector = HandDetector(
        max_num_hands=config.MAX_NUM_HANDS,
        min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
    )
    
    # Initialize Gesture Stabilizer
    stabilizer = GestureStabilizer(
        stabilization_ms=config.GESTURE_STABILIZATION_MS,
        cooldown_ms=config.GESTURE_COOLDOWN_MS,
        volume_repeat_ms=config.VOLUME_REPEAT_INTERVAL_MS
    )
    
    # Initialize Spotify Controller
    spotify = SpotifyController()
    
    # Initialize HUD Overlay & FPS Counter
    hud = HUDOverlay()
    fps_counter = FPSCounter()
    label_stabilizer = HandLabelStabilizer(window_size=12)
    
    if not camera.start():
        logger.error("Could not start camera. Exiting.")
        sys.exit(1)
        
    logger.info("Webcam started. Press 'q' in the window to quit.")
    
    frame_count = 0
    spotify_running = False
    
    try:
        while True:
            # 1. Capture camera frame
            success, frame = camera.read_frame()
            if not success or frame is None:
                logger.error("Failed to read frame from camera. Exiting loop.")
                break
                
            # 2. Mirror frame horizontally for natural user interface
            if config.FLIP_HORIZONTAL:
                frame = cv2.flip(frame, 1)
                
            # 3. Periodically check if Spotify is running (every 60 frames ~ 2 seconds)
            # Running this check every frame would drop the FPS significantly.
            if frame_count % 60 == 0:
                spotify_running = is_spotify_running()
            frame_count += 1
            
            # 4. Calculate FPS
            fps = fps_counter.update()
            
            # 5. Detect hand landmarks
            frame, hands_data = detector.find_hands(frame, draw=True)
            
            raw_gesture = None
            raw_label = hands_data[0]["label"] if hands_data else None
            stable_label = label_stabilizer.process(raw_label)
            
            if hands_data:
                hand_data = hands_data[0]
                # Run finger counter
                finger_results = FingerCounter.count_fingers(hand_data)
                
                # Detect gesture using smoothed stable_label
                raw_gesture = GestureDetector.detect_gesture(finger_results, stable_label)
                
            # 6. Process gesture stabilization & cooldown
            triggered_action, status_msg = stabilizer.process(raw_gesture)
            
            # 7. Execute action if triggered
            if triggered_action:
                logger.info(f"*** ACTION TRIGGERED: {triggered_action} ***")
                spotify.execute_action(triggered_action)
                
            # 8. Draw HUD Dashboard on the frame
            frame = hud.draw(
                frame=frame,
                fps=fps,
                spotify_running=spotify_running,
                stable_label=stable_label,
                raw_gesture=raw_gesture,
                status_msg=status_msg,
                cooldown_progress=stabilizer.cooldown_progress
            )
            
            # 9. Display the frame in the window
            cv2.imshow("Spotify Hand Gesture Controller", frame)
            
            # Break loop if 'q' is pressed (wait 1ms)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("'q' pressed. Shutting down...")
                break
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        # Graceful cleanup
        camera.release()
        detector.close()
        cv2.destroyAllWindows()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
