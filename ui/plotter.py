import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

class PerformancePlotter:
    def __init__(self, parent_frame: ctk.CTkFrame):
        """
        Inputs: The UI frame where the graph should be drawn.
        Sets up an empty Matplotlib figure inside the desktop app.
        """
        self.figure, self.ax = plt.subplots(figsize=(5, 4), facecolor='#2b2b2b')
        self.ax.set_facecolor('#2b2b2b') # Matches the dark theme
        self.ax.tick_params(colors='white')
        
        # Create the canvas and embed it into the CustomTkinter frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_plot(self, n_sizes: list, runtimes: list, detected_complexity: str):
        """
        Clears the old graph and plots the new runtime curve.
        """
        # TODO: Member 4 should add the logic to plot n_sizes (X) vs runtimes (Y)
        # TODO: Add title, labels, and maybe color-code based on best/worst case
        
        self.ax.clear()
        self.ax.plot(n_sizes, runtimes, label=f"Runtime ({detected_complexity})", color='cyan')
        self.ax.legend()
        self.canvas.draw()