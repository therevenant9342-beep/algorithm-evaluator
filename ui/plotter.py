import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import PchipInterpolator
import customtkinter as ctk

# UI Color Theme Constants
_BEST_COLOR = "#00d4aa"
_AVG_COLOR = "#4d9fff"
_WORST_COLOR = "#ff8c42"
_BG = "#0f1117"
_PANEL = "#1a1d27"
_GRID = "#1f2335"
_TICK = "#3a3f55"
_TICK_LABEL = "#5a6080"


def _smooth(x: list, y: list, points: int = 300):
    """
    Interpolates data points in log-log space using PCHIP.
    Returns smoothed (x, y) arrays for plotting non-linear asymptotic growth.
    """
    x_arr = np.array(x, dtype=float)
    y_arr = np.array(y, dtype=float)

    y_safe = np.maximum(y_arr, 1e-10)

    log_x = np.log(x_arr)
    log_y = np.log(y_safe)

    spline = PchipInterpolator(log_x, log_y)

    x_new = np.linspace(x_arr[0], x_arr[-1], points)
    log_x_new = np.log(x_new)

    y_new = np.exp(spline(log_x_new))

    return x_new, y_new


def _apply_style(ax, figure):
    """Applies the dark theme and grid formatting to the matplotlib axes."""
    ax.set_facecolor(_BG)
    figure.patch.set_facecolor(_PANEL)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(axis="both", colors=_TICK_LABEL, labelsize=7, length=0)
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    ax.yaxis.grid(True, color=_GRID, linewidth=0.8, linestyle="-")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_compact_ns))


def _compact_ns(val, _pos):
    """Formats nanosecond values with K or M suffixes for the Y-axis."""
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val/1_000:.0f}K"
    return f"{int(val)}"


class PerformancePlotter:
    """Manages the matplotlib canvas embedded within the CustomTkinter UI."""

    def __init__(self, parent_frame: ctk.CTkFrame):
        self.figure, self.ax = plt.subplots(figsize=(5, 2.6), dpi=100)
        _apply_style(self.ax, self.figure)
        self.figure.subplots_adjust(left=0.13, right=0.97, top=0.88, bottom=0.22)

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)
        self.canvas.get_tk_widget().configure(bg=_PANEL, highlightthickness=0)

    def update_plot(
        self,
        sizes: list,
        best_times: list,
        avg_times: list,
        worst_times: list,
        best_complexity: str = "",
        avg_complexity: str = "",
        worst_complexity: str = "",
        main_complexity: str = "",
    ):
        """Redraws the performance graph with best, average, and worst case execution times."""
        self.ax.clear()
        _apply_style(self.ax, self.figure)

        import statistics

        sx = np.linspace(sizes[0], sizes[-1], 300)

        def process_series(times, comp):
            if comp in ["O(1)", "Ω(1)", "Θ(1)"]:
                flat_val = float(statistics.median(times))
                return np.full_like(sx, flat_val)
            else:
                _, sy = _smooth(sizes, times)
                return sy

        sy_best = process_series(best_times, best_complexity)
        sy_avg = process_series(avg_times, avg_complexity)
        sy_worst = process_series(worst_times, worst_complexity)

        self.ax.fill_between(sx, sy_avg, sy_worst, alpha=0.06, color=_WORST_COLOR)
        self.ax.fill_between(sx, sy_best, sy_avg, alpha=0.07, color=_AVG_COLOR)
        self.ax.fill_between(sx, 0, sy_best, alpha=0.08, color=_BEST_COLOR)

        self.ax.plot(sx, sy_best, color=_BEST_COLOR, linewidth=1.8, linestyle="-")
        self.ax.plot(sx, sy_avg, color=_AVG_COLOR, linewidth=1.8, linestyle="-")
        self.ax.plot(
            sx,
            sy_worst,
            color=_WORST_COLOR,
            linewidth=1.8,
            linestyle="--",
            dashes=(5, 3),
        )

        self.ax.scatter(sizes, best_times, color=_BEST_COLOR, s=22, zorder=5)
        self.ax.scatter(sizes, avg_times, color=_AVG_COLOR, s=22, zorder=5)
        self.ax.scatter(sizes, worst_times, color=_WORST_COLOR, s=22, zorder=5)

        self.ax.set_xticks(sizes)
        self.ax.set_xticklabels([str(s) for s in sizes], fontsize=7, color=_TICK_LABEL)

        if sizes:
            ymin, ymax = self.ax.get_ylim()
            pad = (ymax - ymin) * 0.13
            self.ax.annotate(
                f"n={sizes[0]}",
                xy=(sizes[0], ymin),
                xytext=(sizes[0], ymin - pad),
                fontsize=7,
                color=_TICK,
                ha="center",
                clip_on=False,
            )
            self.ax.annotate(
                f"n={sizes[-1]}",
                xy=(sizes[-1], ymin),
                xytext=(sizes[-1], ymin - pad),
                fontsize=7,
                color=_TICK,
                ha="center",
                clip_on=False,
            )

        if main_complexity:
            self.ax.text(
                0.02,
                0.95,
                main_complexity,
                transform=self.ax.transAxes,
                fontsize=9,
                fontweight="bold",
                color=_BEST_COLOR,
                va="top",
                ha="left",
                alpha=0.85,
            )

        self.figure.subplots_adjust(left=0.13, right=0.97, top=0.88, bottom=0.22)
        self.canvas.draw()

    def clear_plot(self):
        """Clears the plot area, leaving a blank styled canvas."""
        self.ax.clear()
        _apply_style(self.ax, self.figure)
        self.figure.subplots_adjust(left=0.13, right=0.97, top=0.88, bottom=0.22)
        self.canvas.draw()
