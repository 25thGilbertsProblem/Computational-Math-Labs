import math
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from typing import List, Tuple, Any, Dict

import matplotlib.pyplot as plt

from lab4_comp_math.funcs import (
    linear_approx,
    f_linear,
    pearson_r,
    r2_score,
    residuals,
    sse,
    rmse,
    r2_message,
    polinom_approx,
    f_poly3,
    exponential_approx,
    f_exp,
    logarithmic_approx,
    f_log,
    power_approx,
    f_power,
    f_poly2,
)

try:
    import platform

    if platform.system() == "Darwin":
        import os
        os.environ["TK_SILENCE_DEPRECATION"] = "1"
except Exception:
    pass


class ApproximationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("МНК: аппроксимация функций")
        self.geometry("1420x880")
        self.minsize(1280, 780)

        self.x_vals: List[float] = []
        self.y_vals: List[float] = []
        self.results: Dict[str, Dict[str, Any]] = {}
        self.row_vars: List[Tuple[tk.StringVar, tk.StringVar]] = []
        self.row_frames: List[tk.Frame] = []

        self._setup_style()
        self._build_ui()
        self.add_rows(11, fill_sample=True)

    def _setup_style(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(bg="#0b0f14")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#0b0f14")
        style.configure("Card.TFrame", background="#111827", relief="flat")
        style.configure("TLabel", background="#0b0f14", foreground="#f3f4f6", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#0b0f14", foreground="#f9fafb", font=("Segoe UI", 17, "bold"))
        style.configure("Subtitle.TLabel", background="#0b0f14", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#111827", foreground="#f9fafb", font=("Segoe UI", 11, "bold"))
        style.configure(
            "Treeview",
            background="#111827",
            fieldbackground="#111827",
            foreground="#f3f4f6",
            font=("Segoe UI", 10),
            rowheight=28,
        )
        style.configure("Treeview.Heading", background="#1f2937", foreground="#f9fafb", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(16, 14), style="TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Программная реализация МНК", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="Клевцов Александр Сергеевич", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=10)

        left = ttk.Frame(body, style="Card.TFrame", padding=14)
        right = ttk.Frame(body, style="Card.TFrame", padding=14)
        body.add(left, weight=2)
        body.add(right, weight=3)

        self._build_input_panel(left)
        self._build_results_panel(right)

        status_bar = tk.Frame(self, bg="#0b0f14")
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Готово")
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            bg="#0b0f14",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=6)

    def _build_input_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        ttk.Label(parent, text="Ввод данных", style="Header.TLabel").grid(row=0, column=0, sticky="w")

        hint = (
            "Нужно от 8 до 12 точек. Каждая строка — одна пара x и y. "
            "Дублирующиеся точки и пары с одинаковым x, но разным y, будут отклонены. "
            "Логарифмическая, экспоненциальная и степенная модели доступны только при подходящих знаках данных."
        )
        tk.Label(
            parent,
            text=hint,
            bg="#111827",
            fg="#cbd5e1",
            wraplength=460,
            justify="left",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(6, 10))

        controls = tk.Frame(parent, bg="#111827")
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for c in range(4):
            controls.columnconfigure(c, weight=1)

        self._add_colored_button(controls, "Загрузить из файла", self.load_from_file, "#1d4ed8").grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=2)
        self._add_colored_button(controls, "Пример данных", self.fill_sample, "#0f766e").grid(row=0, column=1, sticky="ew", padx=4, pady=2)
        self._add_colored_button(controls, "Очистить", self.clear_table, "#6b7280").grid(row=0, column=2, sticky="ew", padx=4, pady=2)
        self._add_colored_button(controls, "Добавить строку", self.add_row, "#7c3aed").grid(row=0, column=3, sticky="ew", padx=(4, 0), pady=2)
        self._add_colored_button(controls, "Удалить строку", self.remove_row, "#b45309").grid(row=1, column=3, sticky="ew", padx=(4, 0), pady=2)

        table_card = tk.Frame(parent, bg="#111827", highlightbackground="#374151", highlightthickness=1)
        table_card.grid(row=3, column=0, sticky="nsew")
        parent.rowconfigure(3, weight=1)

        canvas = tk.Canvas(table_card, bg="#111827", highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=canvas.yview)
        self.table_inner = tk.Frame(canvas, bg="#111827")
        self.table_window = canvas.create_window((0, 0), window=self.table_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_frame_configure(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(self.table_window, width=event.width)

        self.table_inner.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        header_row = tk.Frame(self.table_inner, bg="#111827")
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header_row.columnconfigure(1, weight=1)
        header_row.columnconfigure(2, weight=1)

        tk.Label(header_row, text="#", bg="#111827", fg="#f9fafb", font=("Segoe UI", 10, "bold"), width=4).grid(row=0, column=0, padx=4, sticky="w")
        tk.Label(header_row, text="x", bg="#111827", fg="#f9fafb", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, padx=4, sticky="w")
        tk.Label(header_row, text="y", bg="#111827", fg="#f9fafb", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, padx=4, sticky="w")

        self.rows_container = tk.Frame(self.table_inner, bg="#111827")
        self.rows_container.grid(row=1, column=0, sticky="ew")

        action_row = tk.Frame(parent, bg="#111827")
        action_row.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        action_row.columnconfigure(0, weight=1)
        action_row.columnconfigure(1, weight=1)

        self._add_colored_button(action_row, "Вычислить", self.compute, "#16a34a").grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self._add_colored_button(action_row, "Построить графики", self.plot, "#7c3aed").grid(row=0, column=1, sticky="ew", padx=(4, 0))
        self._add_colored_button(action_row, "Сохранить результат", self.save_results, "#dc2626").grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _build_results_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        ttk.Label(parent, text="Результаты вычислений", style="Header.TLabel").grid(row=0, column=0, sticky="w")

        table_frame = tk.Frame(parent, bg="#111827", highlightbackground="#374151", highlightthickness=1)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 12))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("model", "params", "sse", "rmse", "r2", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        headings = {
            "model": ("Модель", 160),
            "params": ("Коэффициенты", 280),
            "sse": ("S", 110),
            "rmse": ("σ", 110),
            "r2": ("R²", 100),
            "status": ("Комментарий", 290),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        output_frame = tk.Frame(parent, bg="#111827", highlightbackground="#374151", highlightthickness=1)
        output_frame.grid(row=2, column=0, sticky="nsew")
        parent.rowconfigure(2, weight=1)
        ttk.Label(output_frame, text="Подробный вывод", style="Header.TLabel").pack(anchor="w", padx=10, pady=(8, 6))

        self.output = tk.Text(
            output_frame,
            wrap="word",
            height=15,
            bg="#0f172a",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            font=("Consolas", 10),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#374151",
            highlightcolor="#60a5fa",
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _add_colored_button(self, parent, text, command, bg):
        return ctk.CTkButton(
            master=parent,
            text=text,
            command=command,
            fg_color=bg,
            text_color="white",
            hover_color=self._darken(bg, 0.85),
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
        )

    @staticmethod
    def _darken(hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _create_row(self, index: int, x_value: str = "", y_value: str = ""):
        row = tk.Frame(self.rows_container, bg="#111827")
        row.grid(row=index, column=0, sticky="ew", pady=3)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)

        tk.Label(row, text=str(index + 1), bg="#111827", fg="#cbd5e1", width=4, font=("Segoe UI", 10)).grid(row=0, column=0, padx=4, sticky="w")
        x_var = tk.StringVar(value=x_value)
        y_var = tk.StringVar(value=y_value)
        x_entry = tk.Entry(
            row,
            textvariable=x_var,
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#f9fafb",
            insertbackground="#f9fafb",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#60a5fa",
        )
        y_entry = tk.Entry(
            row,
            textvariable=y_var,
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#f9fafb",
            insertbackground="#f9fafb",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#60a5fa",
        )
        x_entry.grid(row=0, column=1, padx=4, sticky="ew")
        y_entry.grid(row=0, column=2, padx=4, sticky="ew")

        self.row_vars.append((x_var, y_var))
        self.row_frames.append(row)

    def _rebuild_rows(self):
        for w in self.rows_container.winfo_children():
            w.destroy()
        old_values = [(x.get(), y.get()) for x, y in self.row_vars]
        self.row_vars = []
        self.row_frames = []
        for i, (xv, yv) in enumerate(old_values):
            self._create_row(i, xv, yv)

    def add_row(self, fill_sample: bool = False):
        if len(self.row_vars) >= 12:
            self.status_var.set("Нельзя добавить больше 12 строк")
            messagebox.showwarning("Ограничение", "Таблица может содержать не более 12 точек.")
            return
        self._create_row(len(self.row_vars))
        self.status_var.set(f"Добавлена строка №{len(self.row_vars)}")
        if fill_sample:
            self.status_var.set("Загружен пример данных")

    def remove_row(self):
        if len(self.row_vars) <= 8:
            self.status_var.set("Нельзя удалить строки ниже 8")
            messagebox.showwarning("Ограничение", "Таблица должна содержать не менее 8 точек.")
            return
        self.row_vars.pop()
        self._rebuild_rows()
        self.status_var.set(f"Удалена последняя строка. Осталось {len(self.row_vars)}")

    def add_rows(self, count: int, fill_sample: bool = False):
        for _ in range(count):
            if len(self.row_vars) < 12:
                self._create_row(len(self.row_vars))
        if fill_sample:
            self.fill_sample()

    def fill_sample(self):
        sample = [
            (-4.0, -0.230769),
            (-3.6, -0.313979),
            (-3.2, -0.441341),
            (-2.8, -0.641648),
            (-2.4, -0.968023),
            (-2.0, -1.500000),
            (-1.6, -2.273723),
            (-1.2, -2.964387),
            (-0.8, -2.721088),
            (-0.4, -1.490403),
            (0.0, 0.0),
        ]
        self.clear_table(keep_rows=True)
        if len(self.row_vars) < len(sample):
            for _ in range(len(sample) - len(self.row_vars)):
                self._create_row(len(self.row_vars))
        for i, (xv, yv) in enumerate(sample):
            self.row_vars[i][0].set(str(xv))
            self.row_vars[i][1].set(str(yv))
        self.status_var.set("Загружен пример данных для варианта")

    def clear_table(self, keep_rows: bool = False):
        if keep_rows:
            for x_var, y_var in self.row_vars:
                x_var.set("")
                y_var.set("")
        else:
            self.row_vars = []
            self.row_frames = []
            for w in self.rows_container.winfo_children():
                w.destroy()
            for _ in range(11):
                self._create_row(len(self.row_vars))
        self._clear_output()
        self.results = {}
        self.status_var.set("Таблица очищена")

    def load_from_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().replace(",", ".")
            rows = []
            for line_no, line in enumerate(content.splitlines(), start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError(f"Строка {line_no}: нужно ровно два числа x и y. Получено: '{line}'")
                try:
                    xv = float(parts[0])
                    yv = float(parts[1])
                except ValueError:
                    raise ValueError(f"Строка {line_no}: не удалось преобразовать в число. Проверьте запись: '{line}'")
                rows.append((xv, yv))

            if not (8 <= len(rows) <= 12):
                raise ValueError("Файл должен содержать от 8 до 12 точек.")

            self._validate_points(rows)

            self.clear_table(keep_rows=False)
            if len(self.row_vars) < len(rows):
                for _ in range(len(rows) - len(self.row_vars)):
                    self._create_row(len(self.row_vars))
            for i, (xv, yv) in enumerate(rows):
                self.row_vars[i][0].set(str(xv))
                self.row_vars[i][1].set(str(yv))

            self.status_var.set(f"Данные загружены из файла: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def _clear_output(self):
        self.output.delete("1.0", tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _append_output(self, text: str):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    @staticmethod
    def _parse_number(value: str, row_no: int, col_name: str) -> float:
        raw = value.strip().replace(",", ".")
        if raw == "":
            raise ValueError(f"Строка {row_no}, столбец {col_name}: ячейка пустая.")
        try:
            return float(raw)
        except ValueError:
            raise ValueError(f"Строка {row_no}, столбец {col_name}: значение '{value}' не является числом.")

    def _read_table_data(self) -> Tuple[List[float], List[float]]:
        x_vals: List[float] = []
        y_vals: List[float] = []
        filled_rows = 0

        for idx, (x_var, y_var) in enumerate(self.row_vars, start=1):
            xs = x_var.get().strip()
            ys = y_var.get().strip()
            if xs == "" and ys == "":
                continue
            if xs == "" or ys == "":
                raise ValueError(f"Строка {idx}: заполнены не оба поля. Укажите x и y или оставьте строку пустой.")
            x_vals.append(self._parse_number(xs, idx, "x"))
            y_vals.append(self._parse_number(ys, idx, "y"))
            filled_rows += 1

        if filled_rows < 8:
            raise ValueError("Нужно ввести не менее 8 точек.")
        if filled_rows > 12:
            raise ValueError("Нельзя вводить более 12 точек.")

        self._validate_points(list(zip(x_vals, y_vals)))
        return x_vals, y_vals

    @staticmethod
    def _to_real(value, tol: float = 1e-12):
        if isinstance(value, complex):
            if abs(value.imag) > tol:
                return None
            value = value.real

        try:
            value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(value):
            return None

        return value
    @staticmethod
    def _validate_points(points: List[Tuple[float, float]]):
        seen_exact = set()
        x_to_y: Dict[float, float] = {}

        for idx, (x, y) in enumerate(points, start=1):
            exact_key = (x, y)
            if exact_key in seen_exact:
                raise ValueError(
                    f"Обнаружена повторяющаяся точка на позиции {idx}: ({x}, {y}). "
                    "Удалите дубликат."
                )
            seen_exact.add(exact_key)

            if x in x_to_y:
                prev_y = x_to_y[x]
                if abs(prev_y - y) < 1e-12:
                    raise ValueError(
                        f"Обнаружена повторяющаяся точка на позиции {idx}: ({x}, {y}). "
                        "Удалите дубликат."
                    )
                raise ValueError(
                    f"Обнаружены точки с одинаковым x = {x}, но разными y: {prev_y} и {y}. "
                    "Для аппроксимации требуется, чтобы каждому x соответствовало единственное y."
                )
            x_to_y[x] = y

    def compute(self):
        try:
            self.x_vals, self.y_vals = self._read_table_data()
        except Exception as e:
            messagebox.showerror("Ошибка ввода", str(e))
            self.status_var.set("Ошибка ввода данных")
            return

        self._clear_output()
        self.results = {}

        x = self.x_vals
        y = self.y_vals
        n = len(x)

        self._append_output(f"Количество точек: {n}")
        self._append_output(f"x = {self._list_to_str(x)}")
        self._append_output(f"y = {self._list_to_str(y)}")
        self._append_output("")

        try:
            c = linear_approx(x, y, n)
            y_hat = [f_linear(xi, c) for xi in x]
            r = pearson_r(x, y)
            r2 = r2_score(y, y_hat)
            self.results["Линейная"] = {
                "params": c,
                "y_hat": y_hat,
                "eps": residuals(y, y_hat),
                "sse": sse(y, y_hat),
                "rmse": rmse(y, y_hat),
                "r2": r2,
                "func": lambda t, c=c: f_linear(t, c),
                "status": f"r={r:.6f}; {r2_message(r2)}",
            }
        except Exception as e:
            self.results["Линейная"] = {"status": f"Ошибка: {e}"}

        try:
            c = polinom_approx(x, y, n, 3)
            y_hat = [f_poly2(xi, c) for xi in x]
            r2 = r2_score(y, y_hat)
            self.results["Полином 2-й степени"] = {
                "params": c,
                "y_hat": y_hat,
                "eps": residuals(y, y_hat),
                "sse": sse(y, y_hat),
                "rmse": rmse(y, y_hat),
                "r2": r2,
                "func": lambda t, c=c: f_poly2(t, c),
                "status": r2_message(r2),
            }
        except Exception as e:
            self.results["Полином 2-й степени"] = {"status": f"Ошибка: {e}"}

        try:
            c = polinom_approx(x, y, n, 4)
            y_hat = [f_poly3(xi, c) for xi in x]
            r2 = r2_score(y, y_hat)
            self.results["Полином 3-й степени"] = {
                "params": c,
                "y_hat": y_hat,
                "eps": residuals(y, y_hat),
                "sse": sse(y, y_hat),
                "rmse": rmse(y, y_hat),
                "r2": r2,
                "func": lambda t, c=c: f_poly3(t, c),
                "status": r2_message(r2),
            }
        except Exception as e:
            self.results["Полином 3-й степени"] = {"status": f"Ошибка: {e}"}

        try:
            c = exponential_approx(x, y, n)
            y_hat = [f_exp(xi, c) for xi in x]
            r2 = r2_score(y, y_hat)
            self.results["Экспоненциальная"] = {
                "params": c,
                "y_hat": y_hat,
                "eps": residuals(y, y_hat),
                "sse": sse(y, y_hat),
                "rmse": rmse(y, y_hat),
                "r2": r2,
                "func": lambda t, c=c: f_exp(t, c),
                "status": r2_message(r2),
            }
        except Exception as e:
            self.results["Экспоненциальная"] = {"status": f"Недоступна: {e}"}

        try:
            c = logarithmic_approx(x, y, n)
            y_hat = [f_log(xi, c) for xi in x]
            r2 = r2_score(y, y_hat)
            self.results["Логарифмическая"] = {
                "params": c,
                "y_hat": y_hat,
                "eps": residuals(y, y_hat),
                "sse": sse(y, y_hat),
                "rmse": rmse(y, y_hat),
                "r2": r2,
                "func": lambda t, c=c: f_log(t, c),
                "status": r2_message(r2),
            }
        except Exception as e:
            self.results["Логарифмическая"] = {"status": f"Недоступна: {e}"}

        try:
            c = power_approx(x, y, n)
            y_hat = [f_power(xi, c) for xi in x]
            r2 = r2_score(y, y_hat)
            self.results["Степенная"] = {
                "params": c,
                "y_hat": y_hat,
                "eps": residuals(y, y_hat),
                "sse": sse(y, y_hat),
                "rmse": rmse(y, y_hat),
                "r2": r2,
                "func": lambda t, c=c: f_power(t, c),
                "status": r2_message(r2),
            }
        except Exception as e:
            self.results["Степенная"] = {"status": f"Недоступна: {e}"}

        available = {name: res for name, res in self.results.items() if "rmse" in res}
        best_name = None
        best_rmse = float("inf")
        for name, res in available.items():
            if res["rmse"] < best_rmse:
                best_rmse = res["rmse"]
                best_name = name

        self._append_output("РЕЗУЛЬТАТЫ:")
        for name, res in self.results.items():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    name,
                    self._format_params(res.get("params")),
                    self._fmt(res.get("sse")),
                    self._fmt(res.get("rmse")),
                    self._fmt(res.get("r2")),
                    res.get("status", ""),
                ),
            )

            self._append_output(f"[{name}]")
            if "params" in res:
                self._append_output(f"  коэффициенты: {self._format_params(res['params'])}")
                self._append_output(f"  S = {self._fmt(res['sse'])}")
                self._append_output(f"  RMSE = {self._fmt(res['rmse'])}")
                self._append_output(f"  R^2 = {self._fmt(res['r2'])}")
                if name == "Линейная":
                    self._append_output(f"  r (Пирсон) = {self._fmt(pearson_r(x, y))}")
                self._append_output("  x_i = " + self._list_to_str(x))
                self._append_output("  y_i = " + self._list_to_str(y))
                self._append_output("  φ(x_i) = " + self._list_to_str(res['y_hat']))
                self._append_output("  ε_i = " + self._list_to_str(res['eps']))
                self._append_output(f"  {res.get('status', '')}")
            else:
                self._append_output(f"  {res.get('status', '')}")
            self._append_output("")

        if best_name is not None:
            self._append_output(f"Лучшее приближение: {best_name} (RMSE = {best_rmse:.6f})")
            self.status_var.set(f"Лучшее приближение: {best_name}")
        else:
            self._append_output("Не удалось выбрать лучшее приближение: нет доступных моделей.")
            self.status_var.set("Нет доступных моделей")

    def plot(self):
        if not self.results:
            messagebox.showinfo("Информация", "Сначала выполните вычисления.")
            return

        available = {name: res for name, res in self.results.items() if "func" in res}
        if not available:
            messagebox.showinfo("Информация", "Нет доступных моделей для построения графика.")
            return

        x_min = min(self.x_vals)
        x_max = max(self.x_vals)
        span = x_max - x_min
        margin = 0.2 * span if span > 0 else 1.0
        x_left = x_min - margin
        x_right = x_max + margin

        xs = [x_left + i * (x_right - x_left) / 600 for i in range(601)]

        fig = plt.figure(figsize=(11.5, 7.0))
        ax = fig.add_subplot(111)
        ax.grid(True, alpha=0.35)
        ax.set_title("Графики аппроксимаций", fontsize=14)
        ax.set_xlabel("x")
        ax.set_ylabel("y")

        ax.scatter(self.x_vals, self.y_vals, s=34, label="Точки таблицы", zorder=4)

        y_all = list(self.y_vals)

        for name, res in available.items():
            try:
                plot_xs = xs
                if name in ("Логарифмическая", "Степенная"):
                    plot_xs = [xi for xi in xs if xi > 0]

                series_x = []
                series_y = []

                for xi in plot_xs:
                    try:
                        yi = res["func"](xi)
                    except Exception:
                        continue

                    yi_real = self._to_real(yi)
                    if yi_real is None:
                        continue

                    series_x.append(xi)
                    series_y.append(yi_real)

                if series_x:
                    ax.plot(series_x, series_y, linewidth=1.8, label=name)
                    y_all.extend(series_y)

            except Exception:
                pass

        if y_all:
            y_min = min(y_all)
            y_max = max(y_all)
            y_margin = 0.15 * (y_max - y_min) if y_max > y_min else 1.0
            ax.set_ylim(y_min - y_margin, y_max + y_margin)

        ax.legend()
        fig.tight_layout()
        plt.show()

    def save_results(self):
        if not self.results:
            messagebox.showinfo("Информация", "Сначала выполните вычисления.")
            return

        path = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output.get("1.0", tk.END))
            self.status_var.set(f"Результаты сохранены в {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    @staticmethod
    def _fmt(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            if math.isnan(value):
                return "nan"
            return f"{value:.6f}"
        return str(value)

    @staticmethod
    def _list_to_str(lst: List[float]) -> str:
        return "[" + ", ".join(f"{v:.6f}" for v in lst) + "]"

    @staticmethod
    def _format_params(params: Any) -> str:
        if params is None:
            return ""
        if isinstance(params, tuple):
            return "(" + ", ".join(f"{p:.6f}" if isinstance(p, float) else str(p) for p in params) + ")"
        return str(params)


if __name__ == "__main__":
    app = ApproximationApp()
    app.mainloop()
