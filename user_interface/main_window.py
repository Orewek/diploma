# -*- coding: utf-8 -*-
"""Main window of the map."""
import multiprocessing

from crypto_engine import search_worker

import customtkinter as ctk

from settings_window import SettingsWindow

import trio


class BooleanAnfApp(ctk.CTk):
    """Main graphical user interface application.
    Manages multiprocess computation coordination, parameter filtering inputs,
    and dynamic runtime application font scaling configurations.
    """

    def __init__(self) -> None:
        """Initialize main window, default settings, and multiprocessing components."""
        # initialization
        super().__init__()
        self.title('Boolean Function Analyzer')
        self.geometry('1200x850')
        # global settings, how app looks after initialization
        self.app_font_size: int = 24
        self.output_font_size: int = 24
        self.search_timeout: int = 60
        # s
        self.output_font = ctk.CTkFont(family='Courier', size=self.output_font_size)
        # prepare for multiprocessing
        self.processes: list[multiprocessing.Process] = []
        self.queue: multiprocessing.Queue = multiprocessing.Queue()
        # Start the interface build
        self._setup_left_panel()
        self._setup_right_panel()

    def _setup_left_panel(self) -> None:
        """Build the left control panel with inputs, segmented buttons, and action buttons."""
        # Create and place main panel
        self.left_panel = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.left_panel.pack(side='left', fill='y', padx=10, pady=10)
        self.left_panel.columnconfigure(0, weight=1)
        self.left_panel.columnconfigure(1, weight=1)

        # Variables
        ctk.CTkLabel(self.left_panel, text='Variables (n)', font=('Arial', 14)).grid(
            row=0, column=0, padx=10, pady=10, sticky='w',
        )
        self.var_entry = ctk.CTkEntry(self.left_panel)
        self.var_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        self.var_entry.insert(0, '5')

        # SAC
        ctk.CTkLabel(self.left_panel, text='SAC(l)', font=('Arial', 14)).grid(
            row=1, column=0, padx=10, pady=10, sticky='w',
        )
        sac_frame = ctk.CTkFrame(self.left_panel, fg_color='transparent')
        sac_frame.grid(row=1, column=1, sticky='ew')
        self.l_min_entry = ctk.CTkEntry(sac_frame, width=60)
        self.l_min_entry.pack(side='left', padx=2)
        self.l_max_entry = ctk.CTkEntry(sac_frame, width=60)
        self.l_max_entry.pack(side='right', padx=2)
        self.l_min_entry.insert(0, '1')
        self.l_max_entry.insert(0, '2')

        # Without forbidden
        ctk.CTkLabel(self.left_panel, text='Without Forbidden', font=('Arial', 14)).grid(
            row=2, column=0, padx=10, pady=10, sticky='w',
        )
        self.forbidden_var = ctk.StringVar(value='Any')
        self.forbidden_segmented = ctk.CTkSegmentedButton(
            self.left_panel, values=['True', 'False', 'Any'], variable=self.forbidden_var,
        )
        self.forbidden_segmented.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        # Rho and Theta
        ctk.CTkLabel(self.left_panel, text='Rho and Theta', font=('Arial', 14)).grid(
            row=3, column=0, padx=10, pady=10, sticky='w',
        )
        self.rt_var = ctk.StringVar(value='Any')
        self.rt_segmented = ctk.CTkSegmentedButton(
            self.left_panel, values=['Exist', 'Not', 'Any'], variable=self.rt_var,
        )
        self.rt_segmented.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

        # Analyze / Stop
        button_frame = ctk.CTkFrame(self.left_panel, fg_color='transparent')
        button_frame.grid(row=4, column=0, columnspan=2, pady=20, padx=10, sticky='ew')
        self.btn_analyze = ctk.CTkButton(
            button_frame, text='Analyze', command=self.start_analysis, height=40,
        )
        self.btn_analyze.pack(side='left', expand=True, fill='x', padx=5)
        self.btn_stop = ctk.CTkButton(
            button_frame,
            text='Stop',
            command=self.stop_analysis,
            fg_color='red',
            height=40,
            state='disabled',
        )
        self.btn_stop.pack(side='right', expand=True, fill='x', padx=5)

        # Settings
        self.btn_settings = ctk.CTkButton(
            self.left_panel,
            text='Settings',
            command=self.open_settings_window,
            height=40,
        )
        self.btn_settings.grid(row=5, column=0, columnspan=2, pady=20, padx=10, sticky='ew')

    def _setup_right_panel(self) -> None:
        """Build and pack the right output panel with a monospaced text box for results."""
        self.right_panel = ctk.CTkFrame(self, corner_radius=0)
        self.right_panel.pack(side='right', fill='both', padx=20, pady=20, expand=True)
        self.txt_output = ctk.CTkTextbox(
            self.right_panel, font=self.output_font,
        )
        self.txt_output.pack(fill='both', expand=True, padx=25, pady=25)

    def start_analysis(self) -> None:
        """Validate input parameters, toggle UI controls, & spawn parallel worker processes.

        Raises:
        --------
            ValueError: Silent error exception to not drop the app
        """
        try:
            amount_of_variables: int = int(self.var_entry.get())
            l_criteria_min: int = int(self.l_min_entry.get())
            l_criteria_max: int = int(self.l_max_entry.get())
            # get the value from the button
            without_forbidden_status: str | None = self.forbidden_var.get()
            without_forbidden_filter: bool | None = None
            if without_forbidden_status == 'True':
                without_forbidden_filter = True
            elif without_forbidden_status == 'False':
                without_forbidden_filter = False
            # get the value from the button
            rho_theta_filter: str = self.rt_var.get()

        except ValueError:
            return

        # block analyze button
        self.btn_analyze.configure(state='disabled')
        self.btn_stop.configure(state='normal')
        self.txt_output.delete('1.0', 'end')

        # clear old process before start a new analyze
        self.processes = []

        num_cores = multiprocessing.cpu_count()
        for _ in range(num_cores):
            process = multiprocessing.Process(
                target=search_worker,
                args=(
                    self.queue,
                    amount_of_variables,
                    l_criteria_min,
                    l_criteria_max,
                    self.search_timeout,
                    without_forbidden_filter,
                    rho_theta_filter,
                ),
            )
            self.processes.append(process)
            process.start()

        self.check_queue()

    def check_queue(self) -> None:
        """Scan the multiprocessing queue for calculation results and monitor process status."""
        if not self.queue.empty():
            res = self.queue.get()
            self.txt_output.insert('1.0', res['text'])
            self.stop_analysis()

        # check is any process alive
        elif any(process.is_alive() for process in self.processes):
            # freeze for 100ms, so user can interact with interface
            self.after(100, self.check_queue)
        else:
            self.reset_ui()

    def stop_analysis(self) -> None:
        """Signal all active background processes to shut down & wait for their termination."""
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()

        self.processes = []
        self.reset_ui()

    def reset_ui(self) -> None:
        """Restore the main window buttons back to their original idle state."""
        # analyze button to normal state
        self.btn_analyze.configure(state='normal')
        # stop button is disabled
        self.btn_stop.configure(state='disabled')

    def open_settings_window(self) -> None:
        """Open the modal settings window configuration as a child layer over the main app."""
        SettingsWindow(
            self,
            self.app_font_size,
            self.output_font_size,
            self.search_timeout,
            self.update_settings_from_child,
        )

    def update_settings_from_child(self, setting_type: str, value: int | float) -> None:
        """Receive updated configuration data from the child window & apply updates immediately.

        Args:
        -----
            setting_type: What setting are we about to change
            value: font widht
        """
        # change font for output
        if setting_type == 'output_font':
            self.output_font = ctk.CTkFont(family='Courier', size=value)
            self.txt_output.configure(font=self.output_font)
        # change font for interface
        elif setting_type == 'app_font':
            # Добавляем обработку для Apply to App
            self.app_font_size = value
            self.update_main_ui_font(value)
        # change timeout time
        elif setting_type == 'timeout':
            self.search_timeout = value

    def update_main_ui_font(self, size: int) -> None:
        """Change font for all widgets on the left panel by recursion.

        Args:
        -----
            size: font width
        """
        new_font: tuple[str, int] = ('Arial', size)

        def _apply_font_recursive(widget: ctk.CTkBaseClass) -> None:
            """Recursively apply the new font to the current widget and all its inner children.

            Args:
            -----
                widget: widget

            Raises:
            -------
                trio.Cancelled: Silent error exception to not drop the app & multiprocess
            """
            # check is the element has method .configure()
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(font=new_font)

                # some widgets might not support font
                except trio.Cancelled:
                    raise

                except:
                    pass

            # going through elements in the tree by recursion
            for child in widget.winfo_children():
                _apply_font_recursive(child)

        _apply_font_recursive(self.left_panel)


if __name__ == '__main__':
    app = BooleanAnfApp()
    app.mainloop()
