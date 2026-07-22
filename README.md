# 🖐️ SmartGesture - Spotify Hand Controller

A real-time hand gesture recognition application built with **Python**, **OpenCV**, and **MediaPipe** to control Spotify and system media playback seamlessly on Windows.

---

## 📌 Overview

**SmartGesture** captures a live webcam feed, tracks hand landmarks using MediaPipe, recognizes defined finger gestures, and sends system media key commands and Spotify hotkeys without requiring active app focus. It features dual-hand control support, gesture stabilization, continuous volume control, and a modern glassmorphic HUD dashboard overlay.

---

## ✨ Key Features

- **Dual-Hand Control System**: Different gesture actions assigned based on physical hand detection (Right Hand for playback/volume, Left Hand for Spotify hotkeys).
- **Hand Label Stabilizer**: Uses majority voting across a sliding window of frames to eliminate rapid Left/Right hand classification flickering.
- **Gesture Stabilization & Cooldown**: Implements configurable hold-time stabilization (700 ms) and post-action cooldown (1000 ms) to prevent accidental or duplicate triggers.
- **Continuous Volume Stepping**: Holding Volume Up or Volume Down continuously steps the volume at smooth 300 ms intervals.
- **Spotify Auto-Focus & Status Monitor**: Detects if `Spotify.exe` is running and automatically brings the Spotify desktop window into focus when executing advanced hotkeys.
- **Glassmorphic HUD Dashboard**: Real-time camera overlay showing FPS, Spotify connection status, active hand, current gesture, status messages, and visual cooldown bar.
- **Standalone Binary Build Support**: Includes PyInstaller configuration (`SpotifyHandController.spec`) to build a single executable (`.exe`).

---

## 🖐️ Supported Gestures & Actions

### 🖐️ Physical Right Hand — Playback & Volume Controls
| Gesture | Action | Shortcut / Command | Description |
| :--- | :--- | :--- | :--- |
| ☝️ **1 Finger** | **Play / Pause** | Media Key | Toggles playback state |
| ✌️ **2 Fingers** | **Next Track** | Media Key | Skips to the next song |
| 🖖 **4 Fingers** | **Previous Track** | Media Key | Returns to previous track (double-taps automatically) |
| 🖐️ **5 Fingers** | **Volume Up** | Media Key | Increases system volume (repeatable on hold) |
| ✊ **0 Fingers (Fist)** | **Volume Down** | Media Key | Decreases system volume (repeatable on hold) |

### 🤚 Physical Left Hand — Advanced Spotify Hotkeys
| Gesture | Action | Hotkey | Description |
| :--- | :--- | :--- | :--- |
| ☝️ **1 Finger** | **Like Song** | `Alt + Shift + B` | Saves current song to your Library |
| ✌️ **2 Fingers** | **Shuffle** | `Ctrl + S` | Toggles shuffle mode |
| 🖖 **4 Fingers** | **Enable Repeat** | `Ctrl + R` | Toggles repeat mode |

---

## 🛠️ Prerequisites & Requirements

- **Operating System**: Windows 10 / 11
- **Python**: Version 3.12+
- **Hardware**: Standard Webcam
- **Dependencies**: OpenCV, MediaPipe, `keyboard` module

---

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/NurAhmad1102/spotify-smartgesture.git
   cd spotify-smartgesture
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**
   ```bash
   pip install -r spotify-hand-controller/requirements.txt
   ```

---

## 🎮 How to Run

### Option 1: Run via Python
```bash
python spotify-hand-controller/main.py
```

### Option 2: Build Standalone Executable (.exe)
You can bundle the application into a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller SpotifyHandController.spec
```
The resulting executable will be located in the `dist/SpotifyHandController.exe` directory.

### Controls & Exit:
- Show your hand to the camera to trigger media controls.
- Press **`q`** or **`Esc`** on the preview window to exit the application cleanly.

---

## ⚙️ Configuration (`config.py`)

You can customize camera settings, confidence thresholds, and gesture timings in `spotify-hand-controller/config.py`:

- `CAMERA_INDEX`: Camera device index (default: `0`).
- `FRAME_WIDTH` / `FRAME_HEIGHT`: Frame resolution (default: `640x480`).
- `GESTURE_STABILIZATION_MS`: Gesture hold duration before triggering (default: `700` ms).
- `GESTURE_COOLDOWN_MS`: Cooldown duration between regular actions (default: `1000` ms).
- `VOLUME_REPEAT_INTERVAL_MS`: Volume stepping repeat interval on hold (default: `300` ms).
- `MIN_DETECTION_CONFIDENCE` / `MIN_TRACKING_CONFIDENCE`: MediaPipe confidence thresholds (default: `0.7`).

---

## 📂 Project Structure

```text
spotify-smartgesture/
│
├── spotify-hand-controller/
│   ├── main.py                   # Application entry point & main event loop
│   ├── camera.py                 # OpenCV webcam video stream handler
│   ├── hand_detector.py          # MediaPipe hand tracking & landmark extraction
│   ├── finger_counter.py         # Finger state detection & counting logic
│   ├── gesture_detector.py       # Dual-hand gesture mapping & stabilizer engine
│   ├── spotify_controller.py     # Media key and Spotify hotkey automation
│   ├── overlay.py                # Modern glassmorphic HUD dashboard UI
│   ├── config.py                 # Application configuration & parameters
│   ├── utils.py                  # FPS counter & process checking utilities
│   └── requirements.txt          # Python dependencies
│
├── SpotifyHandController.spec    # PyInstaller build specification
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

