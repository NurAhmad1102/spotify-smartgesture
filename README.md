# 🖐️ SmartGesture - Spotify Hand Controller

A real-time hand gesture recognition application built with **Python**, **OpenCV**, and **MediaPipe** to control Spotify and system media playback seamlessly on Windows.

---

## 📌 Overview

**SmartGesture** captures live camera feed, tracks hand landmarks using MediaPipe, recognizes defined finger gestures, and sends system media key commands to control playback (Play/Pause, Next, Previous, Volume Control) on Spotify without needing active app focus.

---

## ✨ Features

- **Real-Time Hand Tracking**: Uses MediaPipe Hands for accurate 21-landmark tracking.
- **Gesture Stabilization**: Implements time-based holding (700 ms) and post-action cooldown (1000 ms) to prevent accidental or duplicate triggers.
- **HUD & Visual Overlay**: Real-time display of FPS, detection confidence, active gesture, action performed, and cooldown timers.
- **System-Wide Media Keys**: Controls Spotify and Windows background media playback directly.

---

## 🖐️ Supported Gestures & Actions

| Gesture | Action | Description |
| :--- | :--- | :--- |
| ☝️ **1 Finger** | **Play / Pause** | Toggles playback state |
| ✌️ **2 Fingers** | **Next Track** | Skips to the next song |
| 🤟 **3 Fingers** | **Previous Track** | Goes back to previous song |
| 🖐️ **5 Fingers** | **Volume Up** | Increases system/media volume |
| ✊ **Closed Fist (0 Fingers)** | **Volume Down** | Decreases system/media volume |

---

## 🛠️ Prerequisites & Requirements

- **Operating System**: Windows 10 / 11
- **Python**: Version 3.12+
- **Hardware**: Standard Webcam

---

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/smartGesture.git
   cd smartGesture
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

Run the application using Python:

```bash
python spotify-hand-controller/main.py
```

### Controls:
- Show your hand to the camera to trigger media controls.
- Press **`q`** or **`Esc`** on the preview window to exit the application cleanly.

---

## 📂 Project Structure

```text
smartGesture/
│
├── spotify-hand-controller/
│   ├── main.py                   # Application entry point & main loop
│   ├── camera.py                 # OpenCV webcam stream handler
│   ├── hand_detector.py          # MediaPipe hand tracking integration
│   ├── finger_counter.py         # Landmark logic to count open fingers
│   ├── gesture_detector.py       # Gesture matching & stabilization logic
│   ├── spotify_controller.py     # Windows media keys controller
│   ├── overlay.py                # Visual HUD display on camera frame
│   ├── config.py                 # System configurations & parameters
│   ├── utils.py                  # Helper functions
│   └── requirements.txt          # Project Python dependencies
│
├── BRD.md                        # Business Requirements Document
├── PRD.md                        # Product Requirements Document
├── Technical-Architect.md        # Architecture overview
├── GUIDE.md                      # System usage guide
├── .gitignore                    # Git ignore file
└── README.md                     # Project documentation
```

---

## ⚙️ Dependencies

- `opencv-python` / `opencv-contrib-python`: Camera capture and frame manipulation
- `mediapipe`: Real-time hand landmark estimation
- `keyboard`: Windows virtual keystroke generation

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
