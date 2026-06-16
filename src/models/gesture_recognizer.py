"""
Gesture Recognition Module for AI Air Mouse
Recognizes hand gestures for mouse control with enhanced gesture set
"""

import math

class GestureRecognizer:
    def __init__(self):
        """Initialize the gesture recognizer"""
        pass
    
    def fingers_up(self, lmList):
        """
        Determine which fingers are up based on landmark positions
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            fingers: List indicating which fingers are up [thumb, index, middle, ring, pinky]
        """
        fingers = []
        
        # Thumb - check if thumb tip is to the right of thumb IP (for right hand)
        # Using x-coordinate comparison
        if lmList[4][1] > lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Four fingers - check if tip is above PIP joint (y-coordinate comparison)
        # Tip IDs: 8 (index), 12 (middle), 16 (ring), 20 (pinky)
        # PIP IDs: 6 (index), 10 (middle), 14 (ring), 18 (pinky)
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]
        
        for tip_id, pip_id in zip(tip_ids, pip_ids):
            if lmList[tip_id][2] < lmList[pip_id][2]:  # Tip above PIP (lower y = higher on screen)
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers
    
    def get_gesture(self, lmList):
        """
        Recognize gesture based on finger positions
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            gesture: String representing the recognized gesture
        """
        if len(lmList) == 0:
            return "none"
        
        fingers = self.fingers_up(lmList)
        totalFingers = fingers.count(1)
        
        # Gesture recognition logic
        if totalFingers == 0:
            return "fist"
        elif totalFingers == 1 and fingers[1] == 1:  # Only index finger
            return "point"
        elif totalFingers == 2 and fingers[1] == 1 and fingers[2] == 1:  # Index and middle
            return "peace"
        elif totalFingers == 3 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:  # Three fingers (index, middle, ring)
            return "three_fingers"
        elif totalFingers == 4 and fingers[0] == 0:  # All except thumb
            return "four"
        elif totalFingers == 5:  # All fingers
            return "open_palm"
        elif fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:  # Only thumb
            return "thumb"
        elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:  # Thumb and index
            return "thumb_index"
        else:
            return "unknown"
    
    def is_pinch_gesture(self, lmList, finger1_tip, finger2_tip, threshold=40):
        """
        Check if two fingers are pinched together
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            finger1_tip: Tip landmark ID of first finger
            finger2_tip: Tip landmark ID of second finger
            threshold: Distance threshold for pinch detection
            
        Returns:
            bool: True if fingers are pinched
        """
        if len(lmList) == 0:
            return False
            
        # Get the tip positions
        tip1 = None
        tip2 = None
        
        for lm in lmList:
            if lm[0] == finger1_tip:
                tip1 = lm
            if lm[0] == finger2_tip:
                tip2 = lm
                
        if tip1 is None or tip2 is None:
            return False
            
        # Calculate distance between fingertips
        distance = ((tip1[1] - tip2[1]) ** 2 + (tip1[2] - tip2[2]) ** 2) ** 0.5
        return distance < threshold
    
    def is_index_middle_pinch(self, lmList):
        """
        Check if index and middle fingers are pinched (for left click/drag)
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            bool: True if index and middle fingers are pinched
        """
        return self.is_pinch_gesture(lmList, 8, 12, threshold=40)
    
    def is_index_ring_pinch(self, lmList):
        """
        Check if index and ring fingers are pinched (for right click)
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            bool: True if index and ring fingers are pinched
        """
        return self.is_pinch_gesture(lmList, 8, 16, threshold=40)
    
    def is_three_fingers_up(self, lmList):
        """
        Check if three fingers (index, middle, ring) are up
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            bool: True if three fingers are up
        """
        if len(lmList) == 0:
            return False
            
        fingers = self.fingers_up(lmList)
        # Check if index, middle, and ring fingers are up
        return fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[0] == 0 and fingers[4] == 0
    
    def is_pinky_up(self, lmList):
        """
        Check if only pinky finger is up
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            bool: True if only pinky is up
        """
        if len(lmList) == 0:
            return False
            
        fingers = self.fingers_up(lmList)
        # Check if only pinky is up
        return fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1
    
    def is_index_up(self, lmList):
        """
        Check if only index finger is up (for pointing/movement)
        
        Args:
            lmList: List of landmark positions [id, x, y, z]
            
        Returns:
            bool: True if only index finger is up
        """
        if len(lmList) == 0:
            return False
            
        fingers = self.fingers_up(lmList)
        # Check if only index finger is up
        return fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0