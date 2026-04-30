"""
Application entry point for the Algorithm Performance Evaluator.
Handles environment configuration and initializes the main application loop.
"""

import customtkinter as ctk
import sys
from ui.main_window import App


def setup_environment():
    """Configures UI scaling and default theme settings."""
    # Enable high-DPI awareness on Windows to prevent blurry rendering
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass 

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def main():
    """Initializes and runs the main application."""
    setup_environment()
    
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Critical execution error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()