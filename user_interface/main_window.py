# -*- coding: utf-8 -*-
"""Main window of the map."""
import multiprocessing

from crypto_engine import search_worker

import customtkinter as ctk

from settings_window import SettingsWindow

import trio

import os
import signal


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

        self.use_sac = True
        self.use_forbidden = True
        self.use_rt = True

        self.output_font = ctk.CTkFont(family='Courier', size=self.output_font_size)
        # prepare for multiprocessing
        self.processes: list[multiprocessing.Process] = []
        self.queue: multiprocessing.Queue = multiprocessing.Queue()
        # Start the interface build
        self._setup_left_panel()
        self._setup_right_panel()

        self.show_sac = True
        self.show_forbidden = True
        self.show_rt = True

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def refresh_left_panel(self):
        # Удаляем старые виджеты (или пересоздаем панель)
        for widget in self.left_panel.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.button_frame:
                widget.destroy()

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
        self.lbl_sac = ctk.CTkLabel(self.left_panel, text='SAC(l)', font=('Arial', 14))
        self.lbl_sac.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        self.sac_frame = ctk.CTkFrame(self.left_panel, fg_color='transparent')
        self.sac_frame.grid(row=1, column=1, sticky='ew')
        
        # Обратите внимание: здесь теперь self.sac_frame вместо просто sac_frame
        self.l_min_entry = ctk.CTkEntry(self.sac_frame, width=60)
        self.l_min_entry.pack(side='left', padx=2)
        self.l_max_entry = ctk.CTkEntry(self.sac_frame, width=60)
        self.l_max_entry.pack(side='right', padx=2)
        self.l_min_entry.insert(0, '1')
        self.l_max_entry.insert(0, '2')

        # Without forbidden
        self.lbl_forbidden = ctk.CTkLabel(self.left_panel, text='Without Forbidden', font=('Arial', 14))
        self.lbl_forbidden.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        
        self.forbidden_var = ctk.StringVar(value='Any')
        self.forbidden_segmented = ctk.CTkSegmentedButton(
            self.left_panel, values=['True', 'False', 'Any'], variable=self.forbidden_var,
        )
        self.forbidden_segmented.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        # Rho and Theta
        self.lbl_rt = ctk.CTkLabel(self.left_panel, text='Rho and Theta', font=('Arial', 14))
        self.lbl_rt.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        
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
            for p in self.processes:
                if p.is_alive():
                    p.terminate()
                    p.join(timeout=0.2)
                    if p.is_alive():
                        p.kill()
                        p.join()
        
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                
                except:
                    break
            
            search_params = {
                'use_sac': getattr(self, 'use_sac', True),
                'use_forbidden': getattr(self, 'use_forbidden', True),
                'use_rt': getattr(self, 'use_rt', True),
        }
            try:
                amount_of_variables: int = int(self.var_entry.get())
                l_criteria_min: int | None = int(self.l_min_entry.get()) if getattr(self, 'use_sac', True) else None
                l_criteria_max: int | None = int(self.l_max_entry.get()) if getattr(self, 'use_sac', True) else None

                # get the value from the button
                without_forbidden_status: str | None = self.forbidden_var.get() if getattr(self, 'use_forbidden', True) else 'Any'
                without_forbidden_filter: bool | None = None
                if without_forbidden_status == 'True':
                    without_forbidden_filter = True
                elif without_forbidden_status == 'False':
                    without_forbidden_filter = False

                # get the value from the button
                rho_theta_filter: str = self.rt_var.get() if getattr(self, 'use_rt', True) else 'Any'

            except ValueError:
                self.txt_output.delete('1.0', 'end')
                self.txt_output.insert('1.0', 'Error: Invalid input. Check your numbers.')
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
                        search_params,
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
            # freeze for 50ms, so user can interact with interface
            self.after(50, self.check_queue)
        else:
            current_text = self.txt_output.get('1.0', 'end-1c').strip()
            if not current_text:
                self.txt_output.insert(
                    '1.0', 
                    'Search finished: No function found.\n'
                    'The strict crypto properties were not met within the time limit.\n'
                    'Try increasing the timeout in Settings.'
                )
            self.reset_ui()

    def stop_analysis(self) -> None:
        """Signal all active background processes to shut down & wait for their termination."""
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=0.1)

                if process.is_alive():
                    os.kill(process.pid, signal.SIGKILL)
                    process.join()

        self.processes = []
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                break
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
            self.use_sac,        # ПЕРЕДАЕМ ТЕКУЩИЕ НАСТРОЙКИ
            self.use_forbidden,  # ПЕРЕДАЕМ ТЕКУЩИЕ НАСТРОЙКИ
            self.use_rt,         # ПЕРЕДАЕМ ТЕКУЩИЕ НАСТРОЙКИ
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
        elif setting_type == 'toggles':
            # НОВОЕ: Обработка чекбоксов
            self.update_toggles(value['sac'], value['forbidden'], value['rt'])

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

    def update_toggles(self, sac: bool, forbidden: bool, rt: bool) -> None:
        self.use_sac = sac
        self.use_forbidden = forbidden
        self.use_rt = rt
        
        # grid_remove() скрывает виджеты, сохраняя их настройки для последующего .grid()
        if self.use_sac:
            self.lbl_sac.grid()
            self.sac_frame.grid()
        else:
            self.lbl_sac.grid_remove()
            self.sac_frame.grid_remove()
            
        if self.use_forbidden:
            self.lbl_forbidden.grid()
            self.forbidden_segmented.grid()
        else:
            self.lbl_forbidden.grid_remove()
            self.forbidden_segmented.grid_remove()
            
        if self.use_rt:
            self.lbl_rt.grid()
            self.rt_segmented.grid()
        else:
            self.lbl_rt.grid_remove()
            self.rt_segmented.grid_remove()

    def on_closing(self):
        """Clean up processes before closing the app."""
        self.stop_analysis()
        self.destroy()

if __name__ == '__main__':
    app = BooleanAnfApp()
    app.mainloop()
