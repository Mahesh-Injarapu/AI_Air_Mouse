"""
Advanced AI Air Mouse Controller

Controls:
1. Index finger moves cursor
2. Push index finger forward = left click
3. Push middle finger forward = right click
4. Three fingers up/down movement = scroll
5. Press Q to quit
"""

import os
import time
import cv2
import numpy as np
import pyautogui
import mediapipe as mp


class SmoothCursor:
    def __init__(self, alpha=0.22, dead_zone=3, prediction=0.10):
        self.alpha = alpha
        self.dead_zone = dead_zone
        self.prediction = prediction

        self.prev_x = None
        self.prev_y = None
        self.prev_time = None
        self.vel_x = 0
        self.vel_y = 0

    def update(self, x, y):
        now = time.time()

        if self.prev_x is None:
            self.prev_x = x
            self.prev_y = y
            self.prev_time = now
            return int(x), int(y)

        dx = x - self.prev_x
        dy = y - self.prev_y

        if abs(dx) < self.dead_zone and abs(dy) < self.dead_zone:
            return int(self.prev_x), int(self.prev_y)

        dt = max(now - self.prev_time, 1e-6)

        self.vel_x = dx / dt
        self.vel_y = dy / dt

        predicted_x = x + self.vel_x * self.prediction
        predicted_y = y + self.vel_y * self.prediction

        smooth_x = self.alpha * predicted_x + (1 - self.alpha) * self.prev_x
        smooth_y = self.alpha * predicted_y + (1 - self.alpha) * self.prev_y

        self.prev_x = smooth_x
        self.prev_y = smooth_y
        self.prev_time = now

        return int(smooth_x), int(smooth_y)


class AppController:
    def __init__(self, camera_id=0, width=640, height=480, target_fps=60):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self.frame_delay = 1.0 / target_fps

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

        self.screen_w, self.screen_h = pyautogui.size()

        self.cursor_smoother = SmoothCursor(
            alpha=0.22,
            dead_zone=3,
            prediction=0.10
        )

        self.last_left_click_time = 0
        self.last_right_click_time = 0
        self.click_cooldown = 0.65

        self.index_push_base = None
        self.middle_push_base = None
        self.push_threshold = 0.055

        self.scroll_prev_y = None
        self.scroll_cooldown_time = 0
        self.scroll_cooldown = 0.18
        self.scroll_threshold = 18

        self.current_fps = 0
        self.fps_count = 0
        self.fps_time = time.time()

        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            raise RuntimeError("Camera not opened. Check webcam permission or camera_id.")

        self._init_mediapipe()

    def _init_mediapipe(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "utils", "hand_landmarker.task")

        print("Looking for model:")
        print(model_path)

        BaseOptions = mp.tasks.BaseOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.detector = HandLandmarker.create_from_options(options)

        print("MediaPipe HandLandmarker loaded successfully.")

    def _detect_hand(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )
        result = self.detector.detect(mp_image)

        if not result.hand_landmarks:
            return None

        return result.hand_landmarks[0]

    def _lm_to_pixel(self, lm):
        return int(lm.x * self.width), int(lm.y * self.height)

    def _finger_is_up(self, landmarks, tip_id, pip_id):
        return landmarks[tip_id].y < landmarks[pip_id].y

    def _move_cursor(self, landmarks, frame):
        index_tip = landmarks[8]

        cam_x = index_tip.x
        cam_y = index_tip.y

        margin_x = 0.12
        margin_y = 0.12

        norm_x = np.interp(cam_x, [margin_x, 1 - margin_x], [0, self.screen_w])
        norm_y = np.interp(cam_y, [margin_y, 1 - margin_y], [0, self.screen_h])

        norm_x = max(0, min(self.screen_w - 1, norm_x))
        norm_y = max(0, min(self.screen_h - 1, norm_y))

        smooth_x, smooth_y = self.cursor_smoother.update(norm_x, norm_y)
        pyautogui.moveTo(smooth_x, smooth_y)

        ix, iy = self._lm_to_pixel(index_tip)
        cv2.circle(frame, (ix, iy), 12, (255, 0, 255), cv2.FILLED)
        cv2.putText(frame, "MOVE", (ix + 15, iy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

    def _handle_push_clicks(self, landmarks, frame):
        now = time.time()

        index_tip = landmarks[8]
        index_mcp = landmarks[5]

        middle_tip = landmarks[12]
        middle_mcp = landmarks[9]

        index_depth = index_tip.z - index_mcp.z
        middle_depth = middle_tip.z - middle_mcp.z

        if self.index_push_base is None:
            self.index_push_base = index_depth

        if self.middle_push_base is None:
            self.middle_push_base = middle_depth

        index_push_amount = self.index_push_base - index_depth
        middle_push_amount = self.middle_push_base - middle_depth

        index_up = self._finger_is_up(landmarks, 8, 6)
        middle_up = self._finger_is_up(landmarks, 12, 10)

        if index_up and index_push_amount > self.push_threshold:
            if now - self.last_left_click_time > self.click_cooldown:
                pyautogui.click(button="left")
                self.last_left_click_time = now
                self.index_push_base = index_depth

                cv2.putText(frame, "LEFT CLICK", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        if middle_up and middle_push_amount > self.push_threshold:
            if now - self.last_right_click_time > self.click_cooldown:
                pyautogui.click(button="right")
                self.last_right_click_time = now
                self.middle_push_base = middle_depth

                cv2.putText(frame, "RIGHT CLICK", (30, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    def _handle_three_finger_scroll(self, landmarks, frame):
        now = time.time()

        index_up = self._finger_is_up(landmarks, 8, 6)
        middle_up = self._finger_is_up(landmarks, 12, 10)
        ring_up = self._finger_is_up(landmarks, 16, 14)
        pinky_up = self._finger_is_up(landmarks, 20, 18)

        three_finger_mode = index_up and middle_up and ring_up and not pinky_up

        if not three_finger_mode:
            self.scroll_prev_y = None
            return

        y_avg = (
            landmarks[8].y +
            landmarks[12].y +
            landmarks[16].y
        ) / 3.0

        y_pixel = int(y_avg * self.height)

        if self.scroll_prev_y is None:
            self.scroll_prev_y = y_pixel
            return

        dy = y_pixel - self.scroll_prev_y

        if abs(dy) > self.scroll_threshold and now - self.scroll_cooldown_time > self.scroll_cooldown:
            if dy > 0:
                pyautogui.scroll(-5)
                cv2.putText(frame, "SCROLL DOWN", (30, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 3)
            else:
                pyautogui.scroll(5)
                cv2.putText(frame, "SCROLL UP", (30, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 3)

            self.scroll_cooldown_time = now
            self.scroll_prev_y = y_pixel

    def _draw_landmarks(self, frame, landmarks):
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]

        for lm in landmarks:
            x, y = self._lm_to_pixel(lm)
            cv2.circle(frame, (x, y), 4, (0, 255, 255), cv2.FILLED)

        for a, b in connections:
            x1, y1 = self._lm_to_pixel(landmarks[a])
            x2, y2 = self._lm_to_pixel(landmarks[b])
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

    def _update_fps(self):
        self.fps_count += 1
        now = time.time()

        if now - self.fps_time >= 1:
            self.current_fps = self.fps_count
            self.fps_count = 0
            self.fps_time = now

    def run(self):
        print("Advanced AI Air Mouse running...")
        print("Press Q to quit.")

        while True:
            loop_start = time.time()

            success, frame = self.cap.read()
            if not success:
                print("Camera frame not received.")
                break

            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (self.width, self.height))

            landmarks = self._detect_hand(frame)

            if landmarks is not None:
                self._draw_landmarks(frame, landmarks)

                index_up = self._finger_is_up(landmarks, 8, 6)

                if index_up:
                    self._move_cursor(landmarks, frame)

                self._handle_push_clicks(landmarks, frame)
                self._handle_three_finger_scroll(landmarks, frame)

            else:
                self.index_push_base = None
                self.middle_push_base = None
                self.scroll_prev_y = None
                cv2.putText(frame, "Show your hand", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            self._update_fps()

            cv2.putText(frame, f"FPS: {self.current_fps}", (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            cv2.putText(frame, "Index: move | Index push: left click | Middle push: right click",
                        (15, self.height - 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

            cv2.putText(frame, "Three fingers move up/down: scroll | Q: quit",
                        (15, self.height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

            cv2.imshow("AI Air Mouse - Advanced", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_delay - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.cap.release()
        cv2.destroyAllWindows()
        print("AI Air Mouse stopped.")