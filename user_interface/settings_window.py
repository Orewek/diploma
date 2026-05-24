# -*- coding: utf-8 -*-
"""Setting window module."""
import contextlib
from typing import TYPE_CHECKING

import customtkinter as ctk

if TYPE_CHECKING:
    from collections.abc import Callable


class SettingsWindow(ctk.CTkToplevel):
    """Modal  window for configuring app font sizes & worker process search timeout limits."""

    def __init__(
            self,
            parent: ctk.CTk,
            current_app_size: int,
            current_out_size: int,
            current_timeout: int | float,
            use_sac: bool,       # НОВОЕ: текущее состояние SAC
            use_forbidden: bool, # НОВОЕ: текущее состояние Forbidden
            use_rt: bool,        # НОВОЕ: текущее состояние Rho and Theta
            on_apply_callback: 'Callable[[str, int | float], None]',
    ) -> None:
        """Initialize settings configuration layout, center modal window & map control triggers.

        Args:
        -----
            parent:
            current_app_size: font size for app
            current_out_size: font size for output
            current_timeout: time cap for calculation
            on_apply_callback:
        """
        # setup a window
        super().__init__(parent)
        self.title('Settings')
        self.geometry('650x400')
        self.resizable(False, False)
        # save callback to send changes back to main window
        self.on_apply_callback = on_apply_callback
        # make a window as the module
        self.transient(parent)
        # stop all operations till windows pops up on the screen
        self.wait_visibility()
        # grab all inputs, while window is open, user can interact with main window
        self.grab_set()

        # pop the window on the center of the main window
        parent.update_idletasks()
        p_width = parent.winfo_width()
        p_height = parent.winfo_height()
        p_x = parent.winfo_x()
        p_y = parent.winfo_y()

        x = p_x + (p_width // 2) - (650 // 2)
        y = p_y + (p_height // 2) - (300 // 2)
        self.geometry(f'+{x}+{y}')

        # font settings
        self.lbl_title = ctk.CTkLabel(
            self, text='Font Size configuration:', font=ctk.CTkFont(weight='bold', size=14),
        )
        self.lbl_title.pack(pady=(20, 5), padx=20, anchor='w')

        self.row_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.row_frame.pack(pady=5, padx=20, fill='x')

        self.size_entry = ctk.CTkEntry(self.row_frame, font=('Arial', 16), width=80, height=40)
        self.size_entry.pack(side='left', padx=(0, 10))
        self.size_entry.insert(0, str(current_app_size))

        self.btn_apply_output = ctk.CTkButton(
            self.row_frame, text='Apply to Output', height=40, width=150,
            command=lambda: self.apply_setting('output_font'),
        )
        self.btn_apply_output.pack(side='left', padx=10)

        self.btn_apply_app = ctk.CTkButton(
            self.row_frame, text='Apply to App', height=40, width=150,
            command=lambda: self.apply_setting('app_font'),
        )
        self.btn_apply_app.pack(side='left', padx=10)

        self.lbl_timeout_title = ctk.CTkLabel(
            self,
            text='Search Timeout configuration (seconds):',
            font=ctk.CTkFont(weight='bold', size=14),
        )
        self.lbl_timeout_title.pack(pady=(20, 5), padx=20, anchor='w')

        self.timeout_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.timeout_frame.pack(pady=5, padx=20, fill='x')

        self.timeout_entry = ctk.CTkEntry(
            self.timeout_frame, font=('Arial', 16), width=80, height=40,
        )
        self.timeout_entry.pack(side='left', padx=(0, 10))
        self.timeout_entry.insert(0, str(current_timeout))

        self.btn_apply_timeout = ctk.CTkButton(
            self.timeout_frame, text='Save Timeout', height=40, width=320,
            command=lambda: self.apply_setting('timeout'),
        )
        self.btn_apply_timeout.pack(side='left', padx=10)

        self.lbl_toggles_title = ctk.CTkLabel(
            self, text='Enable / Disable properties:', font=ctk.CTkFont(weight='bold', size=14)
        )
        self.lbl_toggles_title.pack(pady=(20, 5), padx=20, anchor='w')

        self.toggles_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.toggles_frame.pack(pady=5, padx=20, fill='x')

        self.sac_var = ctk.BooleanVar(value=use_sac)
        self.cb_sac = ctk.CTkCheckBox(self.toggles_frame, text="SAC", variable=self.sac_var, command=self.apply_toggles)
        self.cb_sac.pack(side='left', padx=10)

        self.forbidden_var = ctk.BooleanVar(value=use_forbidden)
        self.cb_forbidden = ctk.CTkCheckBox(self.toggles_frame, text="Without Forbidden", variable=self.forbidden_var, command=self.apply_toggles)
        self.cb_forbidden.pack(side='left', padx=10)

        self.rt_var = ctk.BooleanVar(value=use_rt)
        self.cb_rt = ctk.CTkCheckBox(self.toggles_frame, text="Rho and Theta", variable=self.rt_var, command=self.apply_toggles)
        self.cb_rt.pack(side='left', padx=10)


    def apply_setting(self, setting_type: str) -> None:
        """Method to validate and save settings."""
        # ignore the error to not drop the program
        with contextlib.suppress(ValueError):
            if setting_type in ('output_font', 'app_font'):
                font_width: int = int(self.size_entry.get().strip())
                if font_width <= 4:
                    raise ValueError

                # raise callback
                self.on_apply_callback(setting_type, font_width)
                # animate success
                btn = self.btn_apply_output if setting_type == 'output_font' else self.btn_apply_app
                self._animate_success(
                    btn, 'Apply to Output' if setting_type == 'output_font' else 'Apply to App',
                )

            elif setting_type == 'timeout':
                timeout_time: int = int(self.timeout_entry.get().strip())
                if timeout_time <= 0:
                    raise ValueError

                self.on_apply_callback('timeout', timeout_time)
                self._animate_success(self.btn_apply_timeout, 'Save Timeout')

    def _animate_success(self, button: ctk.CTkButton, default_text: str) -> None:
        """Animation for successful changes & saves in settings."""
        original_color = button.cget('fg_color')
        original_hover = button.cget('hover_color')

        button.configure(text='Saved!', fg_color='#2ca02c', hover_color='#238023')

        def reset() -> None:
            """Restore targeted settings button configuration back to its original state."""
            # if user closes the window before 1.5s elapsed, button will no longer exist
            if self.winfo_exists():
                button.configure(
                    text=default_text, fg_color=original_color, hover_color=original_hover,
                )

        # how long saved! need to be shown on the screen
        self.after(1500, reset)

    def apply_toggles(self) -> None:
        """Передает состояние чекбоксов в главное окно при любом клике по ним."""
        self.on_apply_callback('toggles', {
            'sac': self.sac_var.get(),
            'forbidden': self.forbidden_var.get(),
            'rt': self.rt_var.get()
        })