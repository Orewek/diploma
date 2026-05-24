import threading
import tkinter as tk
import customtkinter as ctk
from crypto_engine import analyze_boolean_function_stream
from settings_window import SettingsWindow

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class BooleanAnfApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1. Базовые настройки окна
        self.title("Boolean Function Analyzer (SageMath)")
        self.geometry("1200x850")

        # 2. Переменные состояния приложения
        self.font_name = "AnfAppFont"
        self.app_font_size = 24
        self.output_font_size = 24
        self.search_timeout = 60
        
        # Создаем глобальный шрифт для Tkinter
        self.tk.call("font", "create", self.font_name, "-family", "Courier", "-size", self.app_font_size)

        # 3. Инициализация интерфейса (вынесена в отдельные методы для чистоты кода)
        self._setup_left_panel()
        self._setup_right_panel()

        # 4. Применение шрифта ко всем созданным элементам
        self.update_application_font(self.app_font_size)


    def _setup_left_panel(self):
        """Создает левую панель с настройками и кнопками."""
        self.left_panel = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.left_panel.pack(side="left", fill="y", padx=20, pady=20, expand=False)
        self.left_panel.pack_propagate(False)

        # Количество переменных
        self.lbl_vars = ctk.CTkLabel(self.left_panel, text="Enter number of variables (n):")
        self.lbl_vars.pack(pady=(20, 5), padx=20, fill="x")

        self.var_entry = ctk.CTkEntry(self.left_panel, height=50, corner_radius=0)
        self.var_entry.pack(pady=5, padx=20, fill="x")
        self.var_entry.insert(0, "5")

        # SAC пределы
        self.lbl_sac = ctk.CTkLabel(self.left_panel, text="SAC order l (min / max):")
        self.lbl_sac.pack(pady=(15, 5), padx=20, fill="x")

        self.sac_frame = tk.Frame(self.left_panel, bg="#2b2b2b")
        self.sac_frame.pack(pady=5, padx=20, fill="x")

        self.l_min_entry = ctk.CTkEntry(self.sac_frame, height=45, corner_radius=0, width=140)
        self.l_min_entry.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.l_min_entry.insert(0, "1")

        self.l_max_entry = ctk.CTkEntry(self.sac_frame, height=45, corner_radius=0, width=140)
        self.l_max_entry.pack(side="right", padx=(10, 0), expand=True, fill="x")
        self.l_max_entry.insert(0, "2")

        # Кнопка анализа
        self.btn_analyze = ctk.CTkButton(
            self.left_panel, text="Generate & Analyze", command=self.start_analysis_thread,
            fg_color="#1f77b4", hover_color="#145a8a", corner_radius=0, height=65
        )
        self.btn_analyze.pack(pady=35, padx=20, fill="x")

        # Информационные лейблы внизу
        self.lbl_copyright = ctk.CTkLabel(self.left_panel, text="Copyright © 2026", font=("Arial", 12), text_color="gray")
        self.lbl_copyright.pack(side="bottom", pady=(2, 20), fill="x")

        self.lbl_madi = ctk.CTkLabel(self.left_panel, text="MADI", font=("Arial", 14, "bold"), text_color="gray")
        self.lbl_madi.pack(side="bottom", pady=2, fill="x")

        self.lbl_info = ctk.CTkLabel(self.left_panel, text="SageMath Engine", font=("Arial", 14), text_color="gray")
        self.lbl_info.pack(side="bottom", pady=2, fill="x")

        # Кнопка настроек
        self.btn_settings = ctk.CTkButton(
            self.left_panel, text="Settings", command=self.open_settings_window,
            height=40, fg_color="transparent", hover_color="#2b2b2b", text_color="gray",
            border_width=1, border_color="gray", font=("Arial", 16), corner_radius=0
        )
        self.btn_settings.pack(side="bottom", pady=10, padx=20, fill="x")


    def _setup_right_panel(self):
        """Создает правую панель для вывода результатов."""
        self.right_panel = ctk.CTkFrame(self, corner_radius=0)
        self.right_panel.pack(side="right", fill="both", padx=20, pady=20, expand=True)

        self.lbl_result = ctk.CTkLabel(self.right_panel, text="Analysis Results:")
        self.lbl_result.pack(pady=(30, 10), padx=25, anchor="w")

        self.txt_output = tk.Text(
            self.right_panel, wrap="word", bg="#1d1e1e", fg="#ffffff",
            insertbackground="white", relief="flat", bd=0, font=("Courier", self.output_font_size)
        )
        self.txt_output.pack(fill="both", expand=True, padx=25, pady=25)


    def open_settings_window(self):
        """Открывает модальное окно настроек."""
        SettingsWindow(self)


    def update_application_font(self, font_size):
        """Динамически обновляет размер шрифта в левой панели."""
        self.app_font_size = font_size
        self.tk.call("font", "configure", self.font_name, "-size", self.app_font_size)
        
        self.lbl_vars.configure(font=("Courier", self.app_font_size))
        self.var_entry.configure(font=("Courier", self.app_font_size))
        self.lbl_sac.configure(font=("Courier", self.app_font_size))
        self.l_min_entry.configure(font=("Courier", self.app_font_size))
        self.l_max_entry.configure(font=("Courier", self.app_font_size))
        self.btn_analyze.configure(font=("Courier", self.app_font_size, "bold"))
        self.lbl_result.configure(font=("Courier", self.app_font_size))
        
        self.update_idletasks()


    def start_analysis_thread(self):
        """Подготавливает UI и запускает анализ в отдельном потоке."""
        self.btn_analyze.configure(state="disabled", text="Calculating...")
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", "Calculating... Please wait.")
        
        # Запуск в фоновом потоке, чтобы интерфейс не зависал
        threading.Thread(target=self.run_analysis, daemon=True).start()


    def run_analysis(self):
        """Основная логика подготовки данных и запуска генератора (работает в фоне)."""
        try:
            # Чтение и валидация ввода
            user_input = self.var_entry.get().strip()
            l_min_in = self.l_min_entry.get().strip()
            l_max_in = self.l_max_entry.get().strip()
            
            if not user_input.isdigit() or int(user_input) <= 0:
                raise ValueError("Please enter a valid positive integer for n.")
            if not l_min_in.isdigit() or not l_max_in.isdigit():
                raise ValueError("SAC limits must be positive integers.")

            n_vars = int(user_input)
            l_min = int(l_min_in)
            l_max = int(l_max_in)
            
            if n_vars > 16:
                raise ValueError("Values above 16 require too much memory.")
            if l_min > l_max or l_max > n_vars:
                raise ValueError("Invalid SAC limits [min, max] configuration.")

            # Запуск математического движка
            for func_idx, text_value in analyze_boolean_function_stream(n_vars, l_min, l_max, self.search_timeout):
                # Безопасное обновление UI из фонового потока
                self.after(0, lambda t=text_value: self.refresh_output_display(t))

        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.show_error_message(error_msg))
            
        finally:
            # Возвращаем кнопку в исходное состояние
            self.after(0, lambda: self.btn_analyze.configure(state="normal", text="Generate & Analyze"))


    def refresh_output_display(self, text_value):
        """Обновляет текстовое поле с результатами."""
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", text_value)
        self.update_idletasks()


    def show_error_message(self, message):
        """Выводит сообщение об ошибке (или таймауте) в текстовое поле."""
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", f"Error during calculation:\n{message}")