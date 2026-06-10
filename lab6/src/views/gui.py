import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import matplotlib

from lab6_comp_math.src.funcs import PROBLEMS
from lab6_comp_math.src.methods.methods import is_finite_number, is_close, euler_method, runge_estimate, \
    improved_euler_method, adams_method, max_abs_error, build_grid

matplotlib.use('TkAgg')

class ODESolverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЛР №6 — Численное решение ОДУ")
        self.geometry("1320x840")
        self.minsize(1200, 780)

        self.problem_var = tk.StringVar()
        self.x0_var = tk.StringVar()
        self.y0_var = tk.StringVar()
        self.xn_var = tk.StringVar()
        self.h_var = tk.StringVar()
        self.eps_var = tk.StringVar()

        self.euler_var = tk.BooleanVar(value=True)
        self.improved_var = tk.BooleanVar(value=True)
        self.adams_var = tk.BooleanVar(value=True)

        self.current_problem_index = 0
        self._build_ui()
        self._set_default_problem(0)

    def _build_ui(self):
        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main, padding=10)
        right = ttk.Frame(main, padding=10)
        main.add(left, weight=1)
        main.add(right, weight=4)

        input_box = ttk.LabelFrame(left, text="Параметры задачи", padding=10)
        input_box.pack(fill=tk.X)

        ttk.Label(input_box, text="ОДУ:").grid(row=0, column=0, sticky="w", pady=4)
        self.problem_cb = ttk.Combobox(
            input_box,
            textvariable=self.problem_var,
            values=[PROBLEMS[0].name, PROBLEMS[1].name, PROBLEMS[2].name],
            state="readonly"
        )
        self.problem_cb.grid(row=0, column=1, sticky="ew", pady=4)
        self.problem_cb.bind("<<ComboboxSelected>>", self._on_problem_change)

        ttk.Label(input_box, text="Методы:").grid(row=1, column=0, sticky="nw", pady=4)
        methods_frame = ttk.Frame(input_box)
        methods_frame.grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Checkbutton(methods_frame, text="Эйлер", variable=self.euler_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(methods_frame, text="Эйлер с пересчетом", variable=self.improved_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(methods_frame, text="Адамс", variable=self.adams_var).grid(row=2, column=0, sticky="w")

        ttk.Label(input_box, text="x0:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(input_box, textvariable=self.x0_var).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(input_box, text="y0:").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(input_box, textvariable=self.y0_var).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(input_box, text="xn:").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(input_box, textvariable=self.xn_var).grid(row=4, column=1, sticky="ew", pady=4)

        ttk.Label(input_box, text="h:").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(input_box, textvariable=self.h_var).grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(input_box, text="eps:").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Entry(input_box, textvariable=self.eps_var).grid(row=6, column=1, sticky="ew", pady=4)

        input_box.columnconfigure(1, weight=1)

        button_box = ttk.Frame(left)
        button_box.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_box, text="Рассчитать", command=self.calculate).pack(fill=tk.X, pady=2)
        ttk.Button(button_box, text="Очистить", command=self.clear_all).pack(fill=tk.X, pady=2)

        notebook = ttk.Notebook(right)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.plot_tab = ttk.Frame(notebook)
        self.table_tab = ttk.Frame(notebook)
        self.log_tab = ttk.Frame(notebook)
        notebook.add(self.plot_tab, text="График")
        notebook.add(self.table_tab, text="Таблица")
        notebook.add(self.log_tab, text="Лог")

        self.figure = Figure(figsize=(8.5, 6), dpi=100)
        self.axis = self.figure.add_subplot(111)
        self.axis.set_title("Решение ОДУ")
        self.axis.set_xlabel("x")
        self.axis.set_ylabel("y")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_tab)
        self.toolbar.update()

        table_frame = ttk.Frame(self.table_tab)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("i", "x", "Euler", "Improved Euler", "Adams", "Exact")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        i = 0
        while i < len(columns):
            col = columns[i]
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
            i += 1

        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(self.log_tab, wrap="word")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _on_problem_change(self, event=None):
        name = self.problem_var.get()
        i = 0
        while i < len(PROBLEMS):
            if PROBLEMS[i].name == name:
                self._set_default_problem(i)
                break
            i += 1

    def _set_default_problem(self, index):
        self.current_problem_index = index
        p = PROBLEMS[index]
        self.problem_var.set(p.name)
        self.x0_var.set(str(p.x0_default))
        self.y0_var.set(str(p.y0_default))
        self.xn_var.set(str(p.xn_default))
        self.h_var.set(str(p.h_default))
        self.eps_var.set("1e-4")
        self.euler_var.set(True)
        self.improved_var.set(True)
        self.adams_var.set(True)

    def current_problem(self):
        return PROBLEMS[self.current_problem_index]

    def clear_all(self):
        self.axis.clear()
        self.axis.set_title("Решение ОДУ")
        self.axis.set_xlabel("x")
        self.axis.set_ylabel("y")
        self.canvas.draw()

        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)

        self.log_text.delete("1.0", tk.END)

    def log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def parse_float_field(self, value_str, field_name, allow_zero=True):
        text = value_str.strip()
        if text == "":
            raise ValueError("Поле '" + field_name + "' не должно быть пустым")

        try:
            value = float(text.replace(",", "."))
        except ValueError:
            raise ValueError("Поле '" + field_name + "' должно содержать число")

        if not is_finite_number(value):
            raise ValueError("Поле '" + field_name + "' не может быть NaN или бесконечностью")

        if not allow_zero and value == 0.0:
            raise ValueError("Поле '" + field_name + "' не может быть нулевым")

        return value

    def validate_inputs(self):
        x0 = self.parse_float_field(self.x0_var.get(), "x0")
        y0 = self.parse_float_field(self.y0_var.get(), "y0")
        xn = self.parse_float_field(self.xn_var.get(), "xn")
        h = self.parse_float_field(self.h_var.get(), "h", allow_zero=False)
        eps = self.parse_float_field(self.eps_var.get(), "eps", allow_zero=False)

        if h <= 0:
            raise ValueError("Шаг h должен быть строго положительным")
        if eps <= 0:
            raise ValueError("Точность eps должна быть строго положительной")
        if xn <= x0:
            raise ValueError("Должно выполняться xn > x0")

        n_float = (xn - x0) / h
        n = int(round(n_float))
        if n < 1:
            raise ValueError("На отрезке должен быть хотя бы один шаг")
        if not is_close(x0 + n * h, xn):
            raise ValueError("Шаг h должен делить отрезок [x0, xn] без остатка")

        return x0, y0, xn, h, eps

    def format_num(self, value):
        if value is None:
            return "—"
        text = f"{value:.8f}"
        while text.endswith("0") and "." in text:
            text = text[:-1]
        if text.endswith("."):
            text = text[:-1]
        return text

    def fill_table(self, xs, euler_ys, improved_ys, adams_ys, exact):
        for item in self.tree.get_children():
            self.tree.delete(item)

        i = 0
        while i < len(xs):
            row = []
            row.append(str(i))
            row.append(self.format_num(xs[i]))

            if euler_ys is None:
                row.append("—")
            else:
                row.append(self.format_num(euler_ys[i]))

            if improved_ys is None:
                row.append("—")
            else:
                row.append(self.format_num(improved_ys[i]))

            if adams_ys is None:
                row.append("—")
            else:
                row.append(self.format_num(adams_ys[i]))

            if exact is None:
                row.append("—")
            else:
                row.append(self.format_num(exact(xs[i])))

            self.tree.insert("", tk.END, values=row)
            i += 1

    def plot_results(self, xs, euler_ys, improved_ys, adams_ys, exact):
        self.axis.clear()
        self.axis.set_title("Решение ОДУ")
        self.axis.set_xlabel("x")
        self.axis.set_ylabel("y")

        if exact is not None and len(xs) > 1:
            dense_x = []
            dense_y = []
            step_count = 20
            i = 0
            while i < len(xs) - 1:
                left = xs[i]
                right = xs[i + 1]
                j = 0
                while j < step_count:
                    t = j / step_count
                    x_val = left + (right - left) * t
                    dense_x.append(x_val)
                    dense_y.append(exact(x_val))
                    j += 1
                i += 1
            dense_x.append(xs[-1])
            dense_y.append(exact(xs[-1]))
            self.axis.plot(dense_x, dense_y, linewidth=2, label="Exact")

        if euler_ys is not None:
            self.axis.plot(xs, euler_ys, marker="o", linewidth=1.5, label="Euler")
        if improved_ys is not None:
            self.axis.plot(xs, improved_ys, marker="o", linewidth=1.5, label="Improved Euler")
        if adams_ys is not None:
            self.axis.plot(xs, adams_ys, marker="o", linewidth=1.5, label="Adams")

        self.axis.grid(True, alpha=0.3)
        self.axis.legend()
        self.canvas.draw()

    def calculate(self):
        try:
            p = self.current_problem()
            x0, y0, xn, h, eps = self.validate_inputs()

            selected_methods = []
            if self.euler_var.get():
                selected_methods.append("Эйлер")
            if self.improved_var.get():
                selected_methods.append("Эйлер с пересчетом")
            if self.adams_var.get():
                selected_methods.append("Адамс")

            if len(selected_methods) == 0:
                raise ValueError("Выберите хотя бы один метод")

            self.clear_all()
            self.log("ОДУ: " + p.name)
            self.log(
                "x0 = " + str(x0) + ", y0 = " + str(y0) + ", xn = " + str(xn) + ", h = " + str(h) + ", eps = " + str(
                    eps))
            self.log("Выбраны методы: " + ", ".join(selected_methods))

            def exact(x):
                return p.exact(x, x0, y0)



            xs = build_grid(x0, xn, h)
            euler_ys = None
            improved_ys = None
            adams_ys = None

            i = 0
            while i < len(selected_methods):
                method_name = selected_methods[i]

                if method_name == "Эйлер":
                    xs, euler_ys = euler_method(p.f, x0, y0, xn, h)
                    euler_r = runge_estimate(euler_method, p.f, x0, y0, xn, h, 1)
                    self.log("Оценка погрешности по Рунге для метода Эйлера: " + self.format_num(euler_r))
                    if euler_r <= eps:
                        self.log("Метод Эйлера: точность удовлетворяет eps")
                    else:
                        self.log("Метод Эйлера: точность не удовлетворяет eps")

                elif method_name == "Эйлер с пересчетом":
                    xs, improved_ys = improved_euler_method(p.f, x0, y0, xn, h)
                    improved_r = runge_estimate(improved_euler_method, p.f, x0, y0, xn, h, 2)
                    self.log(
                        "Оценка погрешности по Рунге для метода Эйлера с пересчетом: " + self.format_num(improved_r))
                    if improved_r <= eps:
                        self.log("Метод Эйлера с пересчетом: точность удовлетворяет eps")
                    else:
                        self.log("Метод Эйлера с пересчетом: точность не удовлетворяет eps")

                elif method_name == "Адамс":
                    xs, adams_ys = adams_method(p.f, x0, y0, xn, h)
                    adams_err = max_abs_error(xs, adams_ys, exact)
                    self.log("Максимальная ошибка метода Адамса: " + self.format_num(adams_err))
                    if adams_err <= eps:
                        self.log("Метод Адамса: точность удовлетворяет eps")
                    else:
                        self.log("Метод Адамса: точность не удовлетворяет eps")

                i += 1

            self.fill_table(xs, euler_ys, improved_ys, adams_ys, exact)
            self.plot_results(xs, euler_ys, improved_ys, adams_ys, exact)

            self.log("")
            self.log("Расчёт выполнен на фиксированном шаге h = " + self.format_num(h))
            self.log("eps использован как критерий сравнения точности в логе.")

        except Exception as e:
            messagebox.showerror("Ошибка ввода", str(e))