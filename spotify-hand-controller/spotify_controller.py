# spotify_controller.py
"""
Spotify controller module using Windows media keys and hotkeys.
"""

import keyboard
import logging
import time
import ctypes
from typing import Dict

logger = logging.getLogger(__name__)

class SpotifyController:
    def __init__(self):
        """
        Initializes the SpotifyController and defines the action-to-key mappings.
        """
        # Map our gesture action strings to keyboard keys/hotkeys
        self.action_map: Dict[str, str] = {
            "Play/Pause": "play/pause media",
            "Next Track": "next track",
            "Previous Track": "previous track",
            "Volume Up": "volume up",
            "Volume Down": "volume down",
            "Like Song": "alt+shift+b",
            "Shuffle": "ctrl+s",
            "Enable Repeat": "ctrl+r"
        }
        logger.info("Spotify controller initialized with media keys and hotkey mappings.")

    def focus_spotify(self) -> bool:
        """
        Finds the desktop Spotify window and brings it to the foreground.
        Necessary for standard application-level hotkeys to work.
        
        Returns:
            bool: True if Spotify was successfully focused, False otherwise.
        """
        try:
            # Find the Spotify window handle by its specific class name
            hwnd = ctypes.windll.user32.FindWindowW("SpotifyMainWindow", None)
            if hwnd:
                # Restore the window if minimized (9 = SW_RESTORE)
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                # Set as foreground window
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                logger.info("Spotify Desktop window focused.")
                return True
            else:
                logger.warning("Spotify Desktop window not found.")
                return False
        except Exception as e:
            logger.error(f"Failed to focus Spotify window: {e}")
            return False

    def execute_action(self, action: str) -> bool:
        """
        Sends the appropriate media key command to the OS for the given action.
        
        Args:
            action: The name of the action to execute.
            
        Returns:
            bool: True if key was sent successfully, False otherwise.
        """
        key_name = self.action_map.get(action)
        if not key_name:
            logger.warning(f"Attempted to execute unknown action: {action}")
            return False
            
        # These hotkeys require the Spotify window to be in focus to trigger
        hotkey_actions = ["Like Song", "Shuffle", "Enable Repeat"]
        
        try:
            if action in hotkey_actions:
                # Attempt to bring Spotify to focus before sending hotkey
                focused = self.focus_spotify()
                if not focused:
                    logger.warning(f"Could not focus Spotify. Hotkey '{key_name}' might not register.")
                time.sleep(0.1)  # Brief pause to let window focus settle
                
            logger.info(f"Executing action '{action}': Sending key/hotkey '{key_name}'")
            
            if action == "Previous Track":
                # Spotify requires two presses in quick succession to skip to the previous song
                # if the current song has been playing for more than a few seconds.
                keyboard.send(key_name)
                time.sleep(0.15)
                keyboard.send(key_name)
            else:
                # Send the key command globally
                keyboard.send(key_name)
            return True
        except Exception as e:
            logger.error(f"Failed to send key '{key_name}' for action '{action}': {e}")
            return False
