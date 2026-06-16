"""
Mouse Controller Module for AI Air Mouse
Controls system mouse based on hand gestures with multi-monitor support
"""

import pyautogui
import time
import numpy as np
from screeninfo import get_monitors

class MouseController:
    def __init__(self, frame_reduction=100, smoothing_factor=0.3, dead_zone=5):
        """
        Initialize the mouse controller with multi-monitor support
        
        Args:
            frame_reduction (int): Margin to reduce frame area for better control
            smoothing_factor (float): EMA smoothing factor (0-1) - converted to alpha
            dead_zone (int): Dead zone radius in pixels to ignore small movements
        """
        self.frame_reduction = frame_reduction
        
        # Get monitor information for multi-monitor support
        self.monitors = get_monitors()
        if not self.monitors:
            # Fallback to primary monitor detection
            self.screen_width, self.screen_height = pyautogui.size()
            self.monitor_offset_x = 0
            self.monitor_offset_y = 0
            self.primary_monitor = type('Monitor', (), {
                'width': self.screen_width,
                'height': self.screen_height,
                'x': 0,
                'y': 0
            })()
        else:
            # Use primary monitor (usually the first one)
            self.primary_monitor = self.monitors[0]
            self.screen_width = self.primary_monitor.width
            self.screen_height = self.primary_monitor.height
            self.monitor_offset_x = self.primary_monitor.x
            self.monitor_offset_y = self.primary_monitor.y
        
        # Initialize cursor smoother
        # Convert smoothing_factor (0-1) to alpha for CursorSmoother
        # Higher smoothing_factor = less smoothing = higher alpha
        alpha = max(0.01, min(0.99, smoothing_factor))  # Clamp between 0.01 and 0.99
        from utils.cursor_smoother import CursorSmoother
        self.cursor_smoother = CursorSmoother(
            alpha=alpha,
            prediction=0.15  # Default prediction value
        )
        
        # Store dead zone for use in movement processing
        self.dead_zone = dead_zone
        
        # Previous location for additional smoothing
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        
        # Set pyautogui failsafe and pause
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.001  # Minimal pause for maximum responsiveness
        
        # Click state tracking
        self.left_click_active = False
        self.right_click_active = False
        self.drag_active = False
        self.last_click_time = 0
        self.click_cooldown = 0.1  # Reduced for better responsiveness
        
    def move_mouse(self, x1, y1, frame_width, frame_height):
        """
        Move mouse based on index finger position with smoothing and prediction
        
        Args:
            x1, y1: Index finger tip coordinates
            frame_width, frame_height: Camera frame dimensions
        """
        # Convert coordinates to screen coordinates (relative to primary monitor)
        x3 = np.interp(x1, (self.frame_reduction, frame_width - self.frame_reduction), 
                      (0, self.screen_width))
        y3 = np.interp(y1, (self.frame_reduction, frame_height - self.frame_reduction), 
                      (0, self.screen_height))
        
        # Apply smoothing and prediction through cursor smoother
        smoothed_x, smoothed_y = self.cursor_smoother.smooth(x3, y3)
        
        # Apply dead-zone filtering to reduce jitter
        dx = smoothed_x - self.plocX
        dy = smoothed_y - self.plocY
        distance = np.sqrt(dx*dx + dy*dy)
        
        if distance < self.dead_zone:
            # If movement is within dead zone, use previous position
            smoothed_x, smoothed_y = self.plocX, self.plocY
        
        # Additional smoothing for very responsive movement
        self.clocX = self.plocX + (smoothed_x - self.plocX) * 0.7
        self.clocY = self.plocY + (smoothed_y - self.plocY) * 0.7
        
        # Move mouse (accounting for monitor offset)
        screen_x = self.monitor_offset_x + (self.screen_width - self.clocX)
        screen_y = self.monitor_offset_y + self.clocY
        
        pyautogui.moveTo(screen_x, screen_y)
        
        # Update previous location
        self.plocX, self.plocY = self.clocX, self.clocY
    
    def click(self, button='left'):
        """
        Perform mouse click
        
        Args:
            button (str): 'left', 'right', or 'middle'
        """
        if button == 'left':
            pyautogui.click()
        elif button == 'right':
            pyautogui.rightClick()
        elif button == 'middle':
            pyautogui.middleClick()
    
    def mouse_down(self, button='left'):
        """
        Press mouse button down (for drag and drop)
        
        Args:
            button (str): 'left', 'right', or 'middle'
        """
        if button == 'left':
            pyautogui.mouseDown(button='left')
        elif button == 'right':
            pyautogui.mouseDown(button='right')
        elif button == 'middle':
            pyautogui.mouseDown(button='middle')
    
    def mouse_up(self, button='left'):
        """
        Release mouse button
        
        Args:
            button (str): 'left', 'right', or 'middle'
        """
        if button == 'left':
            pyautogui.mouseUp(button='left')
        elif button == 'right':
            pyautogui.mouseUp(button='right')
        elif button == 'middle':
            pyautogui.mouseUp(button='middle')
    
    def double_click(self):
        """Perform double mouse click"""
        pyautogui.doubleClick()
    
    def scroll(self, amount):
        """
        Scroll mouse wheel
        
        Args:
            amount (int): Scroll amount (positive for up, negative for down)
        """
        pyautogui.scroll(amount)
    
    def get_monitor_info(self):
        """
        Get information about all connected monitors
        
        Returns:
            list: List of monitor dictionaries with width, height, x, y
        """
        return [{
            'width': m.width,
            'height': m.height,
            'x': m.x,
            'y': m.y
        } for m in self.monitors]