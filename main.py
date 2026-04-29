"""
===========================================================================
Algorithm Performance Evaluator - Main Entry Point
===========================================================================
This script is the "starter motor" for the application. It does not contain 
the algorithm logic itself. Instead, it sets the visual theme and launches 
the main GUI window built by the UI team.
"""

import customtkinter as ctk
from ui.main_window import App

def initialize_app():
    """
    Configures the environment and starts the desktop application.
    """
    print("Starting Algorithm Performance Evaluator...")
    
    # 1. Set the Global Theme
    # The project requires a professional and intuitive GUI.
    # This forces the dark mode aesthetic seen in the Figure 1 Demo Image.
    ctk.set_appearance_mode("dark")  
    ctk.set_default_color_theme("blue") 
    
    # 2. Create the Window Object
    # This calls the 'App' class from our ui/main_window.py file.
    # It constructs the Input Panel, Control Panel, and Results Panel.
    app = App()
    
    # 3. Start the Event Loop
    # This is a mandatory function for desktop apps. It keeps the window 
    # open on the screen and waits for the user to click "Run Analysis".
    app.mainloop()

# =========================================================================
# Execution Guard
# =========================================================================
# This ensures the app only runs if this specific file is executed directly 
# (e.g., typing 'python main.py' in the terminal). 
if __name__ == "__main__":
    try:
        initialize_app()
    except Exception as e:
        print(f"Critical Error Starting Application: {e}")