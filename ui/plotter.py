import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk


class PerformancePlotter:
    def __init__(self, parent_frame: ctk.CTkFrame):
        """
        Inputs: The UI frame where the graph should be drawn.
        Sets up an empty Matplotlib figure inside the desktop app.
        """
        self.figure, self.ax = plt.subplots(figsize=(5, 4), facecolor="#2b2b2b")
        self.ax.set_facecolor("#2b2b2b")  # Matches the dark theme
        self.ax.tick_params(colors="white")

        # Create the canvas and embed it into the CustomTkinter frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_plot(self, n_sizes: list, runtimes: list, detected_complexity: str):
        """
        Clears the old graph and plots the new runtime curve.
        """
        # TODO: Member 4 should add the logic to plot n_sizes (X) vs runtimes (Y)
        # TODO: Add title, labels, and maybe color-code based on best/worst case
        color_map = {
            "O(1)": "green",
            "O(log n)": "blue",
            "O(n)": "cyan",
            "O(n log n)": "orange",
            "O(n^2)": "yellow",
            "O(n^3)": "red",
            "O(2^n)": "magenta",
        }

        plot_color = color_map.get(detected_complexity, "white")

        self.ax.clear()
        self.ax.set_facecolor("#2b2b2b")

        self.ax.plot(
            n_sizes,
            runtimes,
            marker="o",
            linewidth=2,
            color=plot_color,
            label=f"Runtime ({detected_complexity})",
        )

        self.ax.set_title("Runtime vs Input Size", color="white", fontsize=14)
        self.ax.set_xlabel("Input Size (n)", color="white")
        self.ax.set_ylabel("Runtime (ns)", color="white")

        self.ax.tick_params(axis="x", colors="white")
        self.ax.tick_params(axis="y", colors="white")

        self.ax.grid(True, linestyle="--", alpha=0.3)

        self.ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()

        # self.ax.clear()
        # self.ax.plot(
        #     n_sizes, runtimes, label=f"Runtime ({detected_complexity})", color="cyan"
        # )
        # self.ax.legend()
        # self.canvas.draw()
