"""
Hand Tracking Module for AI Air Mouse
Stable MediaPipe Tasks API implementation (FULL VERSION FIXED)
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import os


class HandTracker:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # MediaPipe Tasks imports (correct way)
        self.mp = mp
        self.BaseOptions = mp.tasks.BaseOptions
        self.HandLandmarker = mp.tasks.vision.HandLandmarker
        self.HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        self.RunningMode = mp.tasks.vision.RunningMode

        # Model path
        self.model_path = os.path.join(
            os.path.dirname(__file__),
            "hand_landmarker.task"
        )

        # Results storage
        self.results = None

        # Hand connections (for drawing)
        self.HAND_CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17)
        ]

        # Initialize landmarker
        try:
            options = self.HandLandmarkerOptions(
                base_options=self.BaseOptions(
                    model_asset_path=self.model_path
                ),
                running_mode=self.RunningMode.IMAGE,
                num_hands=self.maxHands,
                min_hand_detection_confidence=self.detectionCon,
                min_hand_presence_confidence=self.detectionCon,
                min_tracking_confidence=self.trackCon
            )

            self.landmarker = self.HandLandmarker.create_from_options(options)
            self.use_landmarker = True

            print("INFO: MediaPipe HandLandmarker initialized successfully")

        except Exception as e:
            self.landmarker = None
            self.use_landmarker = False
            print(f"WARNING: HandLandmarker failed -> {e}")

    # ---------------------------
    # MAIN HAND DETECTION
    # ---------------------------
    def find_hands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.use_landmarker:
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=imgRGB
            )

            self.results = self.landmarker.detect(mp_image)

        if draw:
            img = self._draw_landmarks(img)

        return img

    # ---------------------------
    # DRAW LANDMARKS
    # ---------------------------
    def _draw_landmarks(self, img):
        if not self.results or not hasattr(self.results, "hand_landmarks"):
            return img

        h, w, _ = img.shape

        for hand in self.results.hand_landmarks:

            # draw points
            for lm in hand:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            # draw lines
            for a, b in self.HAND_CONNECTIONS:
                if a < len(hand) and b < len(hand):
                    x1, y1 = int(hand[a].x * w), int(hand[a].y * h)
                    x2, y2 = int(hand[b].x * w), int(hand[b].y * h)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)

        return img

    # ---------------------------
    # GET LANDMARK POSITIONS
    # ---------------------------
    def find_position(self, img, handNo=0, draw=True):
        lmList = []

        if not self.results or not hasattr(self.results, "hand_landmarks"):
            return lmList

        if len(self.results.hand_landmarks) <= handNo:
            return lmList

        hand = self.results.hand_landmarks[handNo]
        h, w, _ = img.shape

        for id, lm in enumerate(hand):
            cx, cy = int(lm.x * w), int(lm.y * h)
            cz = lm.z
            lmList.append([id, cx, cy, cz])

            if draw:
                cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        return lmList

    # ---------------------------
    # DISTANCE BETWEEN POINTS
    # ---------------------------
    def find_distance(self, p1, p2, img=None):
        x1, y1 = p1[1], p1[2]
        x2, y2 = p2[1], p2[2]

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = np.hypot(x2 - x1, y2 - y1)

        if img is not None:
            cv2.circle(img, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

        return length, [x1, y1, x2, y2, cx, cy], img
