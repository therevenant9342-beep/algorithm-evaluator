import customtkinter as ctk
import threading
import re
from core import executor, analyzer
from core.code_generator import (
    get_template,
    list_template_names,
    validate_code,
    DEFAULT_TEMPLATE,
)
from ui.plotter import PerformancePlotter

# UI Color Theme Constants
_BG_DEEP = "#0f1117"
_BG_PANEL = "#1a1d27"
_BG_CARD = "#1e2235"
_BG_HEADER = "#13151f"
_ACCENT = "#4d9fff"
_GREEN = "#00d4aa"
_ORANGE = "#ff8c42"
_RED = "#ff4d6d"
_TEXT_DIM = "#4a5070"
_TEXT_MID = "#7880a0"
_TEXT_HI = "#c8cde0"
_TEXT_WH = "#ffffff"

_BEST_COLOR = _GREEN
_AVG_COLOR = _ACCENT
_WORST_COLOR = _ORANGE

# Big-O complexity classifications for UI descriptions
_COMPLEXITY_DESC = {
    "O(1)": "Constant — independent of input size",
    "O(n)": "Linear — scales directly with input",
    "O(n log n)": "Linearithmic — efficient divide & conquer",
    "O(n^2)": "Quadratic — nested loop pattern detected",
    "O(n^3)": "Cubic — triple nested loops detected",
    "O(2^n)": "Exponential — combinatorial blowup",
}


def _ns_to_str(ns: float) -> str:
    """Converts a time duration in nanoseconds to a human-readable string (ns, µs, or ms)."""
    if ns < 1_000:
        return f"{ns:.0f} ns"
    if ns < 1_000_000:
        return f"{ns/1_000:.1f} µs"
    return f"{ns/1_000_000:.2f} ms"


class _LineNumberedEditor(ctk.CTkFrame):
    """Custom text editor widget featuring dynamic line numbers and basic Python syntax highlighting."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=_BG_DEEP, corner_radius=8)

        # Initialize header with language badge
        hdr = ctk.CTkFrame(self, fg_color=_BG_CARD, corner_radius=0, height=28)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr,
            text="CODE EDITOR",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_TEXT_DIM,
        ).pack(side="left", padx=12)
        ctk.CTkLabel(
            hdr,
            text="Python",
            font=ctk.CTkFont(size=10),
            fg_color="#2a3050",
            text_color=_ACCENT,
            corner_radius=4,
        ).pack(side="left", padx=(0, 8), pady=4)

        # Initialize main editor body
        body = ctk.CTkFrame(self, fg_color=_BG_DEEP, corner_radius=0)
        body.pack(fill="both", expand=True)

        self.line_box = ctk.CTkTextbox(
            body,
            width=36,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=_TEXT_DIM,
            fg_color=_BG_CARD,
            activate_scrollbars=False,
            state="disabled",
            corner_radius=0,
        )
        self.line_box.pack(side="left", fill="y")

        self.code_box = ctk.CTkTextbox(
            body,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=_TEXT_HI,
            fg_color=_BG_DEEP,
            corner_radius=0,
        )
        self.code_box.pack(side="left", fill="both", expand=True)

        # Configure Tkinter text tags for syntax highlighting
        tb = self.code_box._textbox
        tb.tag_configure("keyword", foreground="#c678dd")
        tb.tag_configure("function", foreground="#61afef")
        tb.tag_configure("builtin", foreground="#56b6c2")
        tb.tag_configure("string", foreground="#98c379")
        tb.tag_configure("number", foreground="#d19a66")
        tb.tag_configure("comment", foreground="#7f848e")

        # Bind events for text formatting and scroll synchronization
        self.code_box.bind("<KeyRelease>", lambda e: self._on_code_change())
        self.code_box.bind("<MouseWheel>", lambda e: self.after(5, self._sync_scroll))
        self.code_box._textbox.configure(yscrollcommand=self._on_yscroll)

        self.code_box.insert("0.0", DEFAULT_TEMPLATE)
        self._sync_lines()
        self._highlight_syntax()

    def _highlight_syntax(self):
        """Applies regex-based syntax highlighting to the current code block."""
        tb = self.code_box._textbox
        code = self.code_box.get("1.0", "end-1c")

        for tag in ["keyword", "function", "builtin", "string", "number", "comment"]:
            tb.tag_remove(tag, "1.0", "end")

        patterns = {
            "function": r"\bdef\s+([a-zA-Z_]\w*)",
            "keyword": r"\b(def|return|if|elif|else|for|while|break|continue|import|from|class|pass|True|False|None|and|or|not|in|is|try|except|finally|with|as|yield|lambda)\b",
            "builtin": r"\b(len|print|range|min|max|sum|sorted|int|float|str|list|dict|set|tuple|enumerate|zip|abs|any|all)\b",
            "number": r"\b(\d+\.?\d*)\b",
            "string": r"(['\"])(?:\\.|[^\\])*?\1",
            "comment": r"(#.*)",
        }

        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, code):
                group_idx = 1 if tag == "function" else 0
                if match.group(group_idx) is None:
                    continue
                start_pos = f"1.0 + {match.start(group_idx)} chars"
                end_pos = f"1.0 + {match.end(group_idx)} chars"
                tb.tag_add(tag, start_pos, end_pos)

        # Enforce tag priority to prevent pattern overlap issues
        tb.tag_raise("string")
        tb.tag_raise("comment")

    def _on_yscroll(self, first: str, last: str):
        self._sync_scroll()

    def _on_code_change(self):
        self._sync_lines()
        self._sync_scroll()
        self._highlight_syntax()

    def _sync_lines(self):
        """Updates the line number gutter based on the current code lines."""
        total = int(self.code_box.index("end-1c").split(".")[0])
        nums = "\n".join(str(i) for i in range(1, total + 1))
        self.line_box.configure(state="normal")
        self.line_box.delete("0.0", "end")
        self.line_box.insert("0.0", nums)
        self.line_box.configure(state="disabled")

    def _sync_scroll(self):
        self.line_box._textbox.yview_moveto(self.code_box._textbox.yview()[0])

    def get(self) -> str:
        return self.code_box.get("1.0", "end-1c")

    def set(self, text: str):
        self.code_box.delete("0.0", "end")
        self.code_box.insert("0.0", text)
        self._sync_lines()
        self._sync_scroll()
        self._highlight_syntax()


class _CandidateBar(ctk.CTkFrame):
    """UI component displaying a progress bar representing complexity prediction confidence."""

    def __init__(
        self, parent, label: str, rel_score: float, abs_score: float, highlight: bool
    ):
        super().__init__(parent, fg_color="transparent")
        color = _ACCENT if highlight else _TEXT_DIM
        ctk.CTkLabel(
            self,
            text=label,
            width=90,
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=_TEXT_WH if highlight else _TEXT_MID,
        ).pack(side="left")
        ctk.CTkLabel(
            self,
            text=f"{abs_score * 100:.0f}%",
            width=38,
            anchor="e",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=_TEXT_WH if highlight else _TEXT_MID,
        ).pack(side="right", padx=(0, 4))

        track = ctk.CTkFrame(self, fg_color="#1e2235", height=6, corner_radius=3)
        track.pack(side="left", fill="x", expand=True, padx=(6, 6), pady=6)
        track.pack_propagate(False)
        ctk.CTkFrame(
            track,
            fg_color=color,
            height=6,
            width=max(int(rel_score * 180), 4),
            corner_radius=3,
        ).place(x=0, y=0, relheight=1.0)


class _StatCard(ctk.CTkFrame):
    """Dashboard card for displaying runtime statistics (Best, Avg, Worst)."""

    def __init__(self, parent, title: str, value: str, dot_color: str):
        super().__init__(parent, fg_color=_BG_CARD, corner_radius=6)
        ctk.CTkFrame(self, width=8, height=8, fg_color=dot_color, corner_radius=4).pack(
            anchor="nw", padx=10, pady=(10, 0)
        )
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_TEXT_DIM,
        ).pack(anchor="w", padx=10)
        self.val_lbl = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=_TEXT_WH,
        )
        self.val_lbl.pack(anchor="w", padx=10, pady=(0, 2))
        self.sub_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=dot_color,
        )
        self.sub_lbl.pack(anchor="w", padx=10, pady=(0, 8))

    def update(self, value: str, subtitle: str = ""):
        self.val_lbl.configure(text=value)
        self.sub_lbl.configure(text=subtitle)


class App(ctk.CTk):
    """Main application window managing UI layout, thread execution, and data presentation."""

    def __init__(self):
        super().__init__()
        self.title("Algorithm Performance Evaluator")
        self.geometry("1280x820")
        self.configure(fg_color=_BG_DEEP)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=9)

        self._build_header()
        self._build_editor_panel()
        self._build_results_panel()

    def _build_header(self):
        """Constructs the top toolbar containing execution controls and template selection."""
        hdr = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color=_BG_HEADER)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.pack_propagate(False)

        title_f = ctk.CTkFrame(hdr, fg_color="transparent")
        title_f.pack(side="left", padx=20, pady=12)
        ctk.CTkLabel(
            title_f,
            text="Algorithm ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=_TEXT_WH,
        ).pack(side="left")
        ctk.CTkLabel(
            title_f,
            text="Performance Evaluator",
            font=ctk.CTkFont(size=18),
            text_color=_ACCENT,
        ).pack(side="left")

        self.run_btn = ctk.CTkButton(
            hdr,
            text="▶  Run Analysis",
            fg_color=_ACCENT,
            text_color="#000000",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=140,
            height=32,
            corner_radius=6,
            command=self.on_run_click,
        )
        self.run_btn.pack(side="right", padx=20, pady=10)

        self.mode_toggle = ctk.CTkSegmentedButton(
            hdr,
            values=["Manual", "Auto"],
            font=ctk.CTkFont(size=12),
            fg_color=_BG_CARD,
            selected_color=_ACCENT,
            height=32,
            command=self._on_mode_change,
        )
        self.mode_toggle.set("Auto")
        self.mode_toggle.pack(side="right", padx=(0, 12), pady=10)

        self.template_var = ctk.StringVar(value="Load Template...")
        ctk.CTkOptionMenu(
            hdr,
            variable=self.template_var,
            values=list_template_names(),
            command=self._on_template_selected,
            fg_color=_BG_CARD,
            button_color="#2a3050",
            text_color=_TEXT_MID,
            width=170,
            height=32,
        ).pack(side="right", padx=(0, 12), pady=10)

    def _build_editor_panel(self):
        """Constructs the left panel holding the code editor and manual input fields."""
        outer = ctk.CTkFrame(self, fg_color=_BG_PANEL, corner_radius=0)
        outer.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

        self.editor = _LineNumberedEditor(outer)
        self.editor.pack(fill="both", expand=True, padx=12, pady=12)

        self.array_row = ctk.CTkFrame(
            outer, fg_color=_BG_CARD, corner_radius=6, height=38
        )
        self.array_row.pack_propagate(False)
        ctk.CTkLabel(
            self.array_row,
            text="Array input:",
            text_color=_TEXT_DIM,
            font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=10)

        self.array_entry = ctk.CTkEntry(
            self.array_row,
            placeholder_text="e.g. 5, 3, 8, 1",
            fg_color=_BG_DEEP,
            border_color=_BG_DEEP,
            text_color=_TEXT_HI,
            font=ctk.CTkFont(size=11),
        )
        self.array_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)

    def _on_mode_change(self, mode: str):
        """Toggles the visibility of manual input fields based on execution mode."""
        (
            self.array_row.pack(fill="x", padx=12, pady=(0, 12))
            if mode == "Manual"
            else self.array_row.pack_forget()
        )

    def _build_results_panel(self):
        """Constructs the right panel dashboard displaying metrics, graphs, and candidate scores."""
        outer = ctk.CTkFrame(self, fg_color=_BG_PANEL, corner_radius=0)
        outer.grid(row=1, column=1, sticky="nsew", padx=(0, 1), pady=1)

        ctk.CTkLabel(
            outer,
            text="ANALYSIS RESULTS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_TEXT_DIM,
        ).pack(anchor="nw", padx=16, pady=(14, 0))

        det_card = ctk.CTkFrame(outer, fg_color=_BG_CARD, corner_radius=8)
        det_card.pack(fill="x", padx=12, pady=(6, 0))
        ctk.CTkLabel(
            det_card,
            text="DETECTED COMPLEXITY",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=_TEXT_DIM,
        ).pack(anchor="nw", padx=14, pady=(10, 0))

        self.complexity_display = ctk.CTkLabel(
            det_card,
            text="—",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=_GREEN,
        )
        self.complexity_display.pack(anchor="nw", padx=14, pady=(0, 2))
        self.desc_label = ctk.CTkLabel(
            det_card,
            text="Run an algorithm to see results",
            font=ctk.CTkFont(size=11),
            text_color=_TEXT_MID,
        )
        self.desc_label.pack(anchor="nw", padx=14, pady=(0, 4))

        conf_row = ctk.CTkFrame(det_card, fg_color="transparent")
        conf_row.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkLabel(
            conf_row, text="Confidence", font=ctk.CTkFont(size=10), text_color=_TEXT_DIM
        ).pack(side="left")

        self._conf_track = ctk.CTkFrame(
            conf_row, fg_color="#1a1d27", height=6, corner_radius=3
        )
        self._conf_track.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self._conf_track.pack_propagate(False)
        self._conf_fill = ctk.CTkFrame(
            self._conf_track, fg_color=_GREEN, height=6, width=0, corner_radius=3
        )
        self._conf_fill.place(x=0, y=0, relheight=1.0)

        self._cand_card = ctk.CTkFrame(outer, fg_color=_BG_CARD, corner_radius=8)
        self._cand_card.pack(fill="x", padx=12, pady=(8, 0))
        self._cand_inner = ctk.CTkFrame(self._cand_card, fg_color="transparent")
        self._cand_inner.pack(fill="x", padx=14, pady=(0, 10))

        # Output card — shown only in Manual mode
        self._output_card = ctk.CTkFrame(outer, fg_color=_BG_CARD, corner_radius=8)
        self._output_card.pack(fill="x", padx=12, pady=(8, 0))
        ctk.CTkLabel(
            self._output_card,
            text="OUTPUT",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=_TEXT_DIM,
        ).pack(anchor="nw", padx=14, pady=(10, 4))

        self._output_box = ctk.CTkTextbox(
            self._output_card,
            height=90,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color=_GREEN,
            fg_color=_BG_DEEP,
            corner_radius=6,
            state="disabled",
            wrap="word",
        )
        self._output_box.pack(fill="x", padx=14, pady=(0, 12))
        self._output_card.pack_forget()   # hidden until Manual run

        self._chart_card = ctk.CTkFrame(outer, fg_color=_BG_CARD, corner_radius=8)
        chart_card = self._chart_card
        chart_card.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        self._stat_row = ctk.CTkFrame(chart_card, fg_color="transparent")
        stat_row = self._stat_row
        stat_row.pack(side="bottom", fill="x", padx=10, pady=(4, 10))
        stat_row.grid_columnconfigure((0, 1, 2), weight=1)

        self._stat_best = _StatCard(stat_row, "BEST", "—", _BEST_COLOR)
        self._stat_avg = _StatCard(stat_row, "AVG", "—", _AVG_COLOR)
        self._stat_worst = _StatCard(stat_row, "WORST", "—", _WORST_COLOR)
        self._stat_best.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._stat_avg.grid(row=0, column=1, sticky="ew", padx=2)
        self._stat_worst.grid(row=0, column=2, sticky="ew", padx=(4, 0))

        self.plotter = PerformancePlotter(
            ctk.CTkFrame(chart_card, fg_color="transparent")
        )
        self.plotter.canvas.get_tk_widget().master.pack(
            fill="both", expand=True, padx=6, pady=(0, 4)
        )

    def _finalize_ui(self, payload: dict, mode: str):
        """Callback to parse execution results and update UI metrics."""
        # Handle execution exceptions
        if payload.get("type") == "error":
            self._output_card.pack_forget()
            self._stat_row.pack_forget() if mode == "Manual" else None
            self.complexity_display.configure(text="Execution Error", text_color=_RED)
            self.desc_label.configure(text=payload.get("message", "Unknown error"))
            self.plotter.clear_plot()
            return

        if mode == "Auto":
            # Hide output card, show stat row
            self._output_card.pack_forget()
            self._stat_row.pack(side="bottom", fill="x", padx=10, pady=(4, 10))

            # Parse automated benchmarking metrics
            m = payload["metrics"]
            res_b = analyzer.identify_complexity(m["sizes"], m["sorted_times"])
            res_a = analyzer.identify_complexity(m["sizes"], m["random_times"])
            res_w = analyzer.identify_complexity(m["sizes"], m["reversed_times"])

            big_o = res_w[0]
            self.complexity_display.configure(text=big_o, text_color=_GREEN)
            self.desc_label.configure(text=_COMPLEXITY_DESC.get(big_o, ""))
            self._update_confidence(max(res_w[1].values()) if res_w[1] else 1.0, _GREEN)
            self._update_candidate_bars(res_w[1], big_o)

            # Adjust standard Big-O notation contextually for Best (Ω) and Avg (Θ) cases
            comp_b = res_b[0].replace("O(", "Ω(")
            comp_a = res_a[0].replace("O(", "Θ(")

            self._stat_best.update(_ns_to_str(m["sorted_times"][-1]), subtitle=comp_b)
            self._stat_avg.update(_ns_to_str(m["random_times"][-1]), subtitle=comp_a)
            self._stat_worst.update(_ns_to_str(m["reversed_times"][-1]), subtitle=big_o)

            self.plotter.update_plot(
                m["sizes"],
                m["sorted_times"],
                m["random_times"],
                m["reversed_times"],
                comp_b,
                comp_a,
                big_o,
                big_o,
            )

        elif mode == "Manual":
            # Parse singular execution results
            r = payload["results"]
            t = r["runtime_ns"]
            self.complexity_display.configure(text="Manual ✓", text_color=_ACCENT)
            self.desc_label.configure(text=f"Runtime: {_ns_to_str(t)}")

            self._stat_row.pack_forget()
            self.plotter.clear_plot()

            # Build output text: return value + any console output
            ret_val = r.get("output")
            console = r.get("console_output", "").strip()
            lines = []
            if ret_val is not None:
                lines.append(f"Return value:  {ret_val!r}")
            if console:
                lines.append(f"\nConsole output:\n{console}")
            output_text = "\n".join(lines) if lines else "(no return value)"

            self._output_box.configure(state="normal")
            self._output_box.delete("1.0", "end")
            self._output_box.insert("1.0", output_text)
            self._output_box.configure(state="disabled")

            # Show output card just above the chart card
            self._output_card.pack(fill="x", padx=12, pady=(8, 0),
                                   before=self._chart_card)

    def _update_confidence(self, score: float, color: str):
        self._conf_track.update_idletasks()
        self._conf_fill.configure(
            width=max(4, int(score * self._conf_track.winfo_width())), fg_color=color
        )

    def _update_candidate_bars(self, candidates: dict, winner: str):
        for w in self._cand_inner.winfo_children():
            w.destroy()
        if not candidates:
            return

        max_s = max(candidates.values())
        for l, s in candidates.items():
            _CandidateBar(
                self._cand_inner, l, (s / max_s) if max_s > 0 else 0.0, s, l == winner
            ).pack(fill="x", pady=2)

    def on_run_click(self):
        """Initiates the code evaluation sequence."""
        raw = self.editor.get()

        # Pre-execution validation
        v, r = validate_code(raw)
        if not v:
            self.complexity_display.configure(text="Error", text_color=_RED)
            self.desc_label.configure(text=r)
            return

        self.complexity_display.configure(text="Running…", text_color="#f39c12")
        self.run_btn.configure(state="disabled", text="⌛ Processing…")

        manual_arr = None
        if self.mode_toggle.get() == "Manual":
            manual_arr, err = self._parse_manual_array()
            if manual_arr is None:
                self._show_input_error(err)
                self.run_btn.configure(state="normal", text="▶ Run Analysis")
                return

        # Offload execution to background thread to preserve UI responsiveness
        threading.Thread(
            target=lambda: self._finalize_ui(
                executor.run_evaluation(
                    raw, self.mode_toggle.get(), manual_input=manual_arr
                ),
                self.mode_toggle.get(),
            )
            or self.run_btn.configure(state="normal", text="▶ Run Analysis"),
            daemon=True,
        ).start()

    def _parse_manual_array(self):
        raw = self.array_entry.get().strip()
        if not raw:
            # Replaced the default array with an error trigger
            return None, "Please enter an array first."
        try:
            return [int(x.strip()) for x in raw.split(",")], ""
        except ValueError:
            return None, "Invalid array input. Use comma-separated integers."

    def _show_input_error(self, m: str):
        self.complexity_display.configure(text="Input Error", text_color=_ORANGE)
        self.desc_label.configure(text=m)

    def _on_template_selected(self, name: str):
        self.editor.set(get_template(name))