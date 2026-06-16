# 🚀 AI Air Mouse – Next Generation Gesture-Based Computer Control

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)
![AI](https://img.shields.io/badge/AI-Gesture%20Recognition-purple)
![License](https://img.shields.io/badge/License-MIT-red)

Control your computer using nothing but hand gestures.

AI Air Mouse transforms any webcam into an intelligent gesture recognition system capable of controlling the mouse cursor, performing clicks, scrolling and navigation without touching a physical mouse.

Inspired by modern spatial-computing systems such as Apple Vision Pro, this project creates a futuristic touchless human-computer interaction experience.

---

## 🎥 Demo

📹 Full Demo Video:

[Watch AI Air Mouse Demo](assets/ai_air_mouse_demo.mp4)

---

## ✨ Features

### 🖐 AI Hand Tracking

* Real-time 21-point hand landmark detection
* MediaPipe-powered gesture tracking
* High accuracy hand recognition
* Vision Pro inspired interaction

### 🎯 Smart Cursor Control

* Cursor movement using index finger
* Exponential Moving Average smoothing
* Dead-zone anti-shake stabilization
* Predictive motion algorithms
* Low latency response

### 🖱 Gesture Controls

| Gesture                              | Action           |
| ------------------------------------ | ---------------- |
| Move Index Finger Left/Right/Up/Down | Move Cursor      |
| Push Index Finger Toward Camera      | Left Click       |
| Push Middle Finger Toward Camera     | Right Click      |
| Three Fingers Move Up → Down         | Scroll Down      |
| Three Fingers Move Down → Up         | Scroll Up        |
| Press Q                              | Exit Application |

### ⚡ Performance

* Optimized for 60 FPS
* Smooth cursor movement
* Low CPU usage
* Real-time processing pipeline

### 🖥 Multi-Monitor Support

* Automatic monitor detection
* ScreenInfo integration
* Expandable multi-display architecture

---

## 🏗 System Architecture

Camera Input

↓

MediaPipe Hand Tracking

↓

Gesture Recognition Engine

↓

Cursor Smoothing Engine

↓

Mouse Controller

↓

Operating System Interaction

---

## 🛠 Technology Stack

* Python
* OpenCV
* MediaPipe
* PyAutoGUI
* NumPy
* SciPy
* ScreenInfo

---

## 📂 Project Structure

AI_Air_Mouse/

├── assets/

│ └── ai_air_mouse_demo.mp4

├── src/

│ ├── controllers/

│ ├── models/

│ ├── utils/

│ └── views/

├── main.py

├── requirements.txt

└── README.md

---

## ⚙ Installation

```bash
git clone https://github.com/YOUR_USERNAME/AI_Air_Mouse.git

cd AI_Air_Mouse

pip install -r requirements.txt

python main.py
```

---

## 🎮 How To Use

1. Launch the application.
2. Stand in front of the webcam.
3. Raise your index finger.
4. Move your finger to control the cursor.
5. Push your index finger toward the camera to perform a left click.
6. Push your middle finger toward the camera to perform a right click.
7. Move three fingers downward to scroll down.
8. Move three fingers upward to scroll up.
9. Press Q to quit.

---

## 🔬 Future Enhancements

* Custom Gesture Training
* Voice Assistant Integration
* Virtual Keyboard
* Multi-Hand Interaction
* Eye Tracking Support
* AR/VR Control Layer
* AI Gesture Learning

---

## 👨‍💻 Developer

**Mahesh Injarapu**

B.Tech – CSE (AI & ML)

Passionate about Artificial Intelligence, Computer Vision, Automation and Human-Computer Interaction.

---

⭐ If you found this project useful, please consider giving it a star.
