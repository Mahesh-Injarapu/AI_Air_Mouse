import numpy as np
import time

class CursorSmoother:
    def __init__(self, alpha=0.25, prediction=0.15):
        self.alpha = alpha
        self.prediction = prediction

        self.prev_x = None
        self.prev_y = None
        self.prev_time = None

        self.vel_x = 0
        self.vel_y = 0

    def smooth(self, x, y):
        current_time = time.time()

        if self.prev_x is None:
            self.prev_x, self.prev_y = x, y
            self.prev_time = current_time
            return x, y

        dt = max(current_time - self.prev_time, 1e-6)

        # velocity
        self.vel_x = (x - self.prev_x) / dt
        self.vel_y = (y - self.prev_y) / dt

        # prediction (reduces lag)
        pred_x = x + self.vel_x * self.prediction
        pred_y = y + self.vel_y * self.prediction

        # EMA smoothing
        smooth_x = self.alpha * pred_x + (1 - self.alpha) * self.prev_x
        smooth_y = self.alpha * pred_y + (1 - self.alpha) * self.prev_y

        self.prev_x, self.prev_y = smooth_x, smooth_y
        self.prev_time = current_time

        return int(smooth_x), int(smooth_y)
