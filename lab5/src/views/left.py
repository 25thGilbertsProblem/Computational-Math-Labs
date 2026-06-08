from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import List, Tuple

from data.file_reader import read_table_from_file
from data.presets import FUNCTIONS, PRESET_TABLES, function_names
from utils.checks import parse_float, sort_and_validate_points


class ScrollableFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, height: int = 240):
        super().__init__(master)

        self.canvas = tk.Canvas(self, highlightthickness=0, height=height)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_inner_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        if self.winfo_ismapped():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class LeftPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, on_calculate, on_help):
        super().__init__(master, padding=10)
        self.on_calculate = on_calculate
        self.on_help = on_help

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Параметры интерполяции", font=("Arial", 12, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.mode_var = tk.StringVar(value="Клавиатура")
        self.source_mode = ttk.Combobox(
            self,
            textvariable=self.mode_var,
            values=["Клавиатура", "Файл", "Функция"],
            state="readonly",
        )
        self.source_mode.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.source_mode.bind("<<ComboboxSelected>>", lambda _event: self._switch_mode())

        self.container = ttk.Frame(self)
        self.container.grid(row=2, column=0, sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self._build_keyboard_page()
        self._build_file_page()
        self._build_function_page()

        self.keyboard_page.grid(row=0, column=0, sticky="nsew")
        self.file_page.grid(row=0, column=0, sticky="nsew")
        self.function_page.grid(row=0, column=0, sticky="nsew")
        self._switch_mode()

        settings = ttk.LabelFrame(self, text="Параметры расчёта")
        settings.grid(row=3, column=0, sticky="ew", pady=(10, 8))
        settings.columnconfigure(1, weight=1)

        ttk.Label(settings, text="x0:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.x0_var = tk.StringVar(value="1.051")
        ttk.Entry(settings, textvariable=self.x0_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(settings, text="Метод:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.method_var = tk.StringVar(value="Все")
        ttk.Combobox(
            settings,
            textvariable=self.method_var,
            values=[
                "Все",
                "Лагранж",
                "Ньютон (разделённые разности)",
                "Ньютон (конечные разности)",
                "Гаусс",
            ],
            state="readonly",
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.notice_var = tk.StringVar(value="")
        self.notice_label = ttk.Label(self, textvariable=self.notice_var, foreground="#aa0000", wraplength=420)
        self.notice_label.grid(row=4, column=0, sticky="ew", pady=(0, 6))

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, sticky="ew")
        btn_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(btn_frame, text="Рассчитать", command=self._calculate).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(btn_frame, text="Справка", command=self.on_help).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(btn_frame, text="Очистить", command=self._clear_inputs).grid(row=0, column=2, sticky="ew", padx=2)

    def _build_keyboard_page(self) -> None:
        self.keyboard_page = ttk.LabelFrame(self.container, text="Ввод с клавиатуры")
        self.keyboard_page.columnconfigure(0, weight=1)
        self.keyboard_page.rowconfigure(2, weight=1)
        self.keyboard_page.rowconfigure(4, weight=1)

        top = ttk.Frame(self.keyboard_page)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        top.columnconfigure(0, weight=1)

        ttk.Label(top, text="Введите x и y в отдельных ячейках.").grid(row=0, column=0, sticky="w")

        control = ttk.Frame(top)
        control.grid(row=0, column=1, sticky="e")
        ttk.Button(control, text="+ строка", command=self._add_keyboard_row).grid(row=0, column=0, padx=(0, 4))
        ttk.Button(control, text="− строка", command=self._remove_keyboard_row).grid(row=0, column=1)

        header = ttk.Frame(self.keyboard_page)
        header.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        header.columnconfigure((0, 1), weight=1)
        ttk.Label(header, text="x", anchor="center").grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Label(header, text="y", anchor="center").grid(row=0, column=1, sticky="ew", padx=2)

        self.entry_scroll = ScrollableFrame(self.keyboard_page, height=180)
        self.entry_scroll.grid(row=2, column=0, sticky="nsew")
        self.entry_rows_frame = self.entry_scroll.inner
        self.entry_rows_frame.columnconfigure(0, weight=1)
        self.entry_rows_frame.columnconfigure(1, weight=1)

        preview_title = ttk.Label(self.keyboard_page, text="Таблица введённых данных", font=("Arial", 10, "bold"))
        preview_title.grid(row=3, column=0, sticky="w", pady=(8, 4))

        preview_frame = ttk.Frame(self.keyboard_page)
        preview_frame.grid(row=4, column=0, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview_tree = ttk.Treeview(preview_frame, columns=("x", "y"), show="headings", height=8)
        self.preview_tree.heading("x", text="x")
        self.preview_tree.heading("y", text="y")
        self.preview_tree.column("x", width=120, anchor="center")
        self.preview_tree.column("y", width=120, anchor="center")
        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scroll.set)
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        preview_scroll.grid(row=0, column=1, sticky="ns")

        actions = ttk.Frame(self.keyboard_page)
        actions.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        actions.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(actions, text="Заполнить вариант 4", command=self._fill_variant4).grid(row=0, column=0, sticky="ew",
                                                                                          padx=2)
        ttk.Button(actions, text="Очистить таблицу", command=self._clear_keyboard_rows).grid(row=0, column=1,
                                                                                             sticky="ew", padx=2)
        ttk.Button(actions, text="Добавить пустую строку", command=self._add_keyboard_row).grid(row=0, column=2,
                                                                                                sticky="ew", padx=2)

        self.keyboard_rows = []
        default_rows = PRESET_TABLES["Вариант 4"]
        i = 0
        while i < len(default_rows[0]):
            self._add_keyboard_row(str(default_rows[0][i]), str(default_rows[1][i]))
            i += 1

        self._refresh_preview_table()
    def _add_keyboard_row(self, x_value: str = "", y_value: str = "") -> None:
        row_index = len(self.keyboard_rows)
        x_var = tk.StringVar(value=x_value)
        y_var = tk.StringVar(value=y_value)
        ttk.Entry(self.entry_rows_frame, textvariable=x_var).grid(row=row_index, column=0, sticky="ew", padx=2, pady=2)
        ttk.Entry(self.entry_rows_frame, textvariable=y_var).grid(row=row_index, column=1, sticky="ew", padx=2, pady=2)
        self.keyboard_rows.append((x_var, y_var))
        self._refresh_preview_table()

    def _remove_keyboard_row(self) -> None:
        if len(self.keyboard_rows) <= 2:
            return
        self.keyboard_rows.pop()
        self._rebuild_keyboard_rows()
        self._refresh_preview_table()

    def _rebuild_keyboard_rows(self) -> None:
        widgets = self.entry_rows_frame.winfo_children()
        index = 0
        while index < len(widgets):
            widgets[index].destroy()
            index += 1

        index = 0
        while index < len(self.keyboard_rows):
            x_var, y_var = self.keyboard_rows[index]
            ttk.Entry(self.entry_rows_frame, textvariable=x_var).grid(row=index, column=0, sticky="ew", padx=2, pady=2)
            ttk.Entry(self.entry_rows_frame, textvariable=y_var).grid(row=index, column=1, sticky="ew", padx=2, pady=2)
            index += 1

    def _clear_keyboard_rows(self) -> None:
        self.keyboard_rows = []
        self._add_keyboard_row()
        self._add_keyboard_row()
        self._refresh_preview_table()

    def _fill_variant4(self) -> None:
        self.keyboard_rows = []
        x_vals, y_vals = PRESET_TABLES["Вариант 4"]
        index = 0
        while index < len(x_vals):
            self.keyboard_rows.append((tk.StringVar(value=str(x_vals[index])), tk.StringVar(value=str(y_vals[index]))))
            index += 1
        self._rebuild_keyboard_rows()
        self._refresh_preview_table()

    def _refresh_preview_table(self, x_values=None, y_values=None) -> None:
        if not hasattr(self, "preview_tree"):
            return

        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        parsed_x = []
        parsed_y = []

        if x_values is not None and y_values is not None:
            parsed_x = list(x_values)
            parsed_y = list(y_values)
        else:
            i = 0
            while i < len(self.keyboard_rows):
                x_text = self.keyboard_rows[i][0].get().strip()
                y_text = self.keyboard_rows[i][1].get().strip()

                if x_text == "" and y_text == "":
                    i += 1
                    continue

                if x_text != "" and y_text != "":
                    try:
                        parsed_x.append(parse_float(x_text))
                        parsed_y.append(parse_float(y_text))
                    except Exception:
                        parsed_x = []
                        parsed_y = []
                        break
                else:
                    parsed_x = []
                    parsed_y = []
                    break

                i += 1

            if len(parsed_x) >= 2:
                try:
                    parsed_x, parsed_y = sort_and_validate_points(parsed_x, parsed_y)
                except Exception:
                    parsed_x = []
                    parsed_y = []

        i = 0
        while i < len(parsed_x):
            self.preview_tree.insert("", tk.END, values=(f"{parsed_x[i]:.6f}", f"{parsed_y[i]:.6f}"))
            i += 1

    def _build_file_page(self) -> None:
        self.file_page = ttk.LabelFrame(self.container, text="Ввод из файла")
        self.file_page.columnconfigure(0, weight=1)
        self.file_page.columnconfigure(1, weight=0)

        self.file_path_var = tk.StringVar()
        ttk.Entry(self.file_page, textvariable=self.file_path_var).grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Button(self.file_page, text="Обзор...", command=self._browse_file).grid(row=0, column=1, padx=5)
        ttk.Label(self.file_page, text="Файл должен содержать пары x y в каждой строке.").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )

    def _build_function_page(self) -> None:
        self.function_page = ttk.LabelFrame(self.container, text="Генерация по функции")
        self.function_page.columnconfigure(1, weight=1)

        ttk.Label(self.function_page, text="Функция:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.func_var = tk.StringVar(value=function_names()[0])
        ttk.Combobox(self.function_page, textvariable=self.func_var, values=function_names(), state="readonly").grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )

        ttk.Label(self.function_page, text="a:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.a_var = tk.StringVar(value="0.0")
        ttk.Entry(self.function_page, textvariable=self.a_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.function_page, text="b:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.b_var = tk.StringVar(value="3.14")
        ttk.Entry(self.function_page, textvariable=self.b_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(self.function_page, text="Количество точек:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.n_var = tk.StringVar(value="7")
        ttk.Entry(self.function_page, textvariable=self.n_var).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    def _switch_mode(self) -> None:
        self.keyboard_page.grid_remove()
        self.file_page.grid_remove()
        self.function_page.grid_remove()

        mode = self.mode_var.get()
        if mode == "Клавиатура":
            self.keyboard_page.grid(row=0, column=0, sticky="nsew")
        elif mode == "Файл":
            self.file_page.grid(row=0, column=0, sticky="nsew")
        else:
            self.function_page.grid(row=0, column=0, sticky="nsew")

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.file_path_var.set(path)

    def _clear_inputs(self) -> None:
        self.notice_var.set("")
        self.file_path_var.set("")
        self.x0_var.set("1.051")
        self.method_var.set("Все")
        self.mode_var.set("Клавиатура")
        self._fill_variant4()
        self._switch_mode()

    def _collect_keyboard_data(self):
        x_values = []
        y_values = []

        index = 0
        while index < len(self.keyboard_rows):
            x_text = self.keyboard_rows[index][0].get().strip()
            y_text = self.keyboard_rows[index][1].get().strip()

            if x_text == "" and y_text == "":
                index += 1
                continue

            if x_text == "" or y_text == "":
                raise ValueError("Каждая заполненная строка должна содержать и x, и y.")

            x_values.append(parse_float(x_text))
            y_values.append(parse_float(y_text))
            index += 1

        return sort_and_validate_points(x_values, y_values)

    def _collect_file_data(self):
        path = self.file_path_var.get().strip()
        if path == "":
            raise ValueError("Не выбран файл.")
        x_values, y_values = read_table_from_file(path)
        return sort_and_validate_points(x_values, y_values)

    def _collect_function_data(self):
        func_name = self.func_var.get()
        if func_name not in FUNCTIONS:
            raise ValueError("Не выбрана функция.")

        a = parse_float(self.a_var.get())
        b = parse_float(self.b_var.get())
        n = int(parse_float(self.n_var.get()))

        if n < 2:
            raise ValueError("Количество точек должно быть не меньше 2.")
        if a >= b:
            raise ValueError("Левая граница интервала должна быть меньше правой.")

        func = FUNCTIONS[func_name]
        step = (b - a) / (n - 1)

        x_values = []
        y_values = []
        index = 0
        while index < n:
            xi = a + index * step
            x_values.append(xi)
            y_values.append(func(xi))
            index += 1

        return sort_and_validate_points(x_values, y_values)

    def _calculate(self) -> None:
        try:
            x0 = parse_float(self.x0_var.get())
            mode = self.mode_var.get()

            if mode == "Клавиатура":
                x_values, y_values = self._collect_keyboard_data()
            elif mode == "Файл":
                x_values, y_values = self._collect_file_data()
            else:
                x_values, y_values = self._collect_function_data()

            self.notice_var.set("")
            self._refresh_preview_table(x_values, y_values)
            self.on_calculate(x_values, y_values, x0, self.method_var.get())
        except Exception as exc:
            message = str(exc)
            self.notice_var.set(message)
            self.on_calculate([], [], None, self.method_var.get(), error=message)
