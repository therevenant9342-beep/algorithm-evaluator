import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Algorithm Performance Evaluator")
        self.geometry("1100x700")

        # --- LEFT PANEL: CODE INPUT ---
        self.code_label = ctk.CTkLabel(self, text="Paste Python Code Here:")
        self.code_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.code_editor = ctk.CTkTextbox(self, width=500, height=400)
        self.code_editor.grid(row=1, column=0, padx=20, pady=10)
        # Pre-fill with a template for the user 
        self.code_editor.insert("0.0", "def my_algorithm(arr):\n    # Write code here\n    return arr")

        # --- RIGHT PANEL: RESULTS ---
        self.results_frame = ctk.CTkFrame(self, width=400)
        self.results_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        self.res_label = ctk.CTkLabel(self.results_frame, text="ANALYSIS RESULTS", font=("Arial", 20, "bold"))
        self.res_label.pack(pady=20)

        # --- CONTROL BUTTONS ---
        self.run_btn = ctk.CTkButton(self, text="Run Analysis", command=self.on_run_click)
        self.run_btn.grid(row=2, column=0, columnspan=2, pady=20)

    def on_run_click(self):
        # This is where me will connect the UI to the Logic later!
        print("Analysis started...")