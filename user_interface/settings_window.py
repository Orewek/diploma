import tkinter as tk

class SettingsWindow(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("650x280")
        self.resizable(False, False)
        self.configure(bg="#242424")
        
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        parent.update_idletasks()
        p_width = parent.winfo_width()
        p_height = parent.winfo_height()
        p_x = parent.winfo_x()
        p_y = parent.winfo_y()
        
        x = p_x + (p_width // 2) - (650 // 2)
        y = p_y + (p_height // 2) - (280 // 2)
        self.geometry(f"650x280+{x}+{y}")

        self.lbl_title = tk.Label(
            self, text="Font Size configuration:", 
            font=("Arial", 14, "bold"), bg="#242424", fg="#ffffff"
        )
        self.lbl_title.pack(pady=(15, 5), padx=20, anchor="w")

        self.row_frame = tk.Frame(self, bg="#242424")
        self.row_frame.pack(pady=5, padx=20, fill="x")

        self.size_entry = tk.Entry(
            self.row_frame, font=("Arial", 16), bg="#1d1e1e", fg="#ffffff",
            insertbackground="white", relief="flat", bd=2, width=8
        )
        self.size_entry.pack(side="left", padx=(10, 10), ipady=8)
        self.size_entry.insert(0, str(parent.app_font_size))

        self.btn_apply_output = tk.Button(
            self.row_frame, text="Apply to Output", command=self.apply_font_output,
            font=("Arial", 14), bg="#2b2b2b", fg="#ffffff", 
            activebackground="#404040", activeforeground="#ffffff",
            relief="flat", bd=0, cursor="hand2", width=16
        )
        self.btn_apply_output.pack(side="left", padx=10, ipady=6)

        self.btn_apply_app = tk.Button(
            self.row_frame, text="Apply to App", command=self.apply_font_app,
            font=("Arial", 14, "bold"), bg="#1f77b4", fg="#ffffff",
            activebackground="#145a8a", activeforeground="#ffffff",
            relief="flat", bd=0, cursor="hand2", width=16
        )
        self.btn_apply_app.pack(side="left", padx=10, ipady=6)

        self.lbl_timeout_title = tk.Label(
            self, text="Search Timeout configuration (seconds):", 
            font=("Arial", 14, "bold"), bg="#242424", fg="#ffffff"
        )
        self.lbl_timeout_title.pack(pady=(20, 5), padx=20, anchor="w")

        self.timeout_frame = tk.Frame(self, bg="#242424")
        self.timeout_frame.pack(pady=5, padx=20, fill="x")

        self.timeout_entry = tk.Entry(
            self.timeout_frame, font=("Arial", 16), bg="#1d1e1e", fg="#ffffff",
            insertbackground="white", relief="flat", bd=2, width=8
        )
        self.timeout_entry.pack(side="left", padx=(10, 10), ipady=8)
        self.timeout_entry.insert(0, str(parent.search_timeout))

        self.btn_apply_timeout = tk.Button(
            self.timeout_frame, text="Save Timeout", command=self.apply_timeout,
            font=("Arial", 14, "bold"), bg="#1f77b4", fg="#ffffff",
            activebackground="#145a8a", activeforeground="#ffffff",
            relief="flat", bd=0, cursor="hand2", width=34
        )
        self.btn_apply_timeout.pack(side="left", padx=10, ipady=6)

    def apply_font_output(self):
        user_size = self.size_entry.get().strip()
        if not user_size.isdigit() or int(user_size) <= 4:
            return
            
        self.btn_apply_output.config(text="Saved!", bg="#2ca02c")
        
        def reset():
            if self.winfo_exists():
                self.btn_apply_output.config(text="Apply to Output", bg="#2b2b2b")
        self.after(1500, reset)
        
        self.update_idletasks()
        
        try:
            self.parent.output_font_size = int(user_size)
            self.parent.txt_output.configure(font=("Courier", self.parent.output_font_size))
        except Exception as e:
            pass

    def apply_font_app(self):
        user_size = self.size_entry.get().strip()
        if not user_size.isdigit() or int(user_size) <= 4:
            return
            
        self.btn_apply_app.config(text="Saved!", bg="#2ca02c")
        
        def reset():
            if self.winfo_exists():
                self.btn_apply_app.config(text="Apply to App", bg="#1f77b4")
        self.after(1500, reset)
        
        self.update_idletasks()
        
        try:
            self.parent.update_application_font(int(user_size))
        except Exception as e:
            pass

    def _animate_success(self, button, default_text, default_bg):
            button.config(text="Saved!", bg="#2ca02c")

            def reset():
                if self.winfo_exists():
                    button.config(text=default_text, bg=default_bg)

            self.after(1500, reset)
            self.update_idletasks()

    def apply_timeout(self):
            user_timeout = self.timeout_entry.get().strip()
            if not user_timeout.isdigit() or int(user_timeout) <= 0:
                return
                
            self._animate_success(self.btn_apply_timeout, "Save Timeout", "#1f77b4")
            
            try:
                self.parent.search_timeout = int(user_timeout)
            except Exception as e:
                print(f"Error applying timeout: {e}")