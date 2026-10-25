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
        Returns True if Spotify was successfully brought to focus.
        """
        try:
            hwnd = ctypes.windll.user32.FindWindowW("SpotifyMainWindow", None)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                time.sleep(0.05)
                fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
                if fg_hwnd == hwnd:
                    logger.info("Spotify Desktop window focused successfully.")
                    return True
                else:
                    logger.warning("Attempted to focus Spotify, but another window remains foreground.")
                    return False
            else:
                logger.warning("Spotify Desktop window ('SpotifyMainWindow') not found.")
                return False
        except Exception as e:
            logger.error(f"Failed to focus Spotify window: {e}")
            return False

    def execute_action(self, action: str) -> bool:
        """
        Sends the appropriate media key or hotkey command.
        """
        key_name = self.action_map.get(action)
        if not key_name:
            logger.warning(f"Attempted to execute unknown action: {action}")
            return False
            
        hotkey_actions = ["Like Song", "Shuffle", "Enable Repeat"]
        
        try:
            if action in hotkey_actions:
                focused = self.focus_spotify()
                if not focused:
                    logger.warning(
                        f"Spotify is not active/focused. Skipping hotkey '{key_name}' "
                        f"for action '{action}' to prevent accidental window Save/Screenshot."
                    )
                    return False
                time.sleep(0.05)
                
            logger.info(f"Executing action '{action}': Sending key/hotkey '{key_name}'")
            
            if action == "Previous Track":
                keyboard.send(key_name)
                time.sleep(0.15)
                keyboard.send(key_name)
            else:
                keyboard.send(key_name)
            return True
        except Exception as e:
            logger.error(f"Failed to send key '{key_name}' for action '{action}': {e}")
            return False
