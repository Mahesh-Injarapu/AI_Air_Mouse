"""
Test script to verify AI Air Mouse installation and basic functionality
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print(f"[OK] OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"[ERROR] Failed to import OpenCV: {e}")
        return False
    
    try:
        import mediapipe as mp
        print(f"[OK] MediaPipe version: {mp.__version__}")
    except ImportError as e:
        print(f"[ERROR] Failed to import MediaPipe: {e}")
        return False
    
    try:
        import pyautogui
        print(f"[OK] PyAutoGUI version: {pyautogui.__version__}")
    except ImportError as e:
        print(f"[ERROR] Failed to import PyAutoGUI: {e}")
        return False
    
    try:
        import numpy as np
        print(f"[OK] NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"[ERROR] Failed to import NumPy: {e}")
        return False
    
    try:
        import screeninfo
        # screeninfo doesn't have __version__ attribute, so we'll just check if it imports
        print("[OK] ScreenInfo imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import ScreenInfo: {e}")
        return False
    
    try:
        import scipy
        print(f"[OK] SciPy version: {scipy.__version__}")
    except ImportError as e:
        print(f"[ERROR] Failed to import SciPy: {e}")
        return False
    
    # Test local modules
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from utils.hand_tracker import HandTracker
        from utils.cursor_smoother import CursorSmoother
        from controllers.mouse_controller import MouseController
        from models.gesture_recognizer import GestureRecognizer
        from controllers.app_controller import AppController
        print("[OK] All local modules imported successfully")
    except ImportError as e:
        print(f"[ERROR] Failed to import local modules: {e}")
        return False
    
    return True

def test_camera():
    """Test that camera can be accessed"""
    print("\nTesting camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("[OK] Camera accessed successfully")
                cap.release()
                return True
            else:
                print("[ERROR] Could not read frame from camera")
                cap.release()
                return False
        else:
            print("[ERROR] Could not open camera")
            cap.release()
            return False
    except Exception as e:
        print(f"[ERROR] Error accessing camera: {e}")
        return False

def test_monitors():
    """Test monitor detection"""
    print("\nTesting monitor detection...")
    try:
        from screeninfo import get_monitors
        monitors = get_monitors()
        print(f"[OK] Detected {len(monitors)} monitor(s)")
        for i, m in enumerate(monitors):
            print(f"  Monitor {i+1}: {m.width}x{m.height} at ({m.x}, {m.y})")
        return len(monitors) > 0
    except Exception as e:
        print(f"[ERROR] Error detecting monitors: {e}")
        return False

def main():
    """Run all tests"""
    print("AI Air Mouse Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_camera,
        test_monitors
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[OK] All tests passed! Installation is ready.")
        return 0
    else:
        print("[ERROR] Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())