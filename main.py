"""
AI Air Mouse - Main Entry Point
"""

from src.controllers.app_controller import AppController


def main():
    print("AI Air Mouse - Starting...")
    print("Show index finger to move cursor.")
    print("Push index finger forward for left click.")
    print("Push middle finger forward for right click.")
    print("Move three fingers up/down for scrolling.")
    print("Press Q to quit.")

    app = AppController()
    app.run()


if __name__ == "__main__":
    main()