import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.lines import Line2D

from funcs import scalar_functions, system_functions, get_scalar_labels, get_system_labels
from method import (
    find_unique_root_interval,
    choose_newton_start,
    choose_chord_data,
    check_scalar_iteration_convergence,
    check_system_convergence,
    newton_method,
    fixed_chord_method,
    simple_iteration_system,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computational methods")
        self.geometry("1400x900")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.scalar_tab = ttk.Frame(self.notebook)
        self.system_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.scalar_tab, text="Нелинейное уравнение")
        self.notebook.add(self.system_tab, text="Система уравнений")

        self.scalar_result_text = ""
        self.system_result_text = ""

        self.build_scalar_tab()
        self.build_system_tab()

    def make_text_area(self, parent):
        frame = ttk.Frame(parent)
        text = tk.Text(frame, wrap="word", height=20)
        scroll = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return frame, text

    def get_scalar_spec(self):
        label = self.scalar_func_var.get()
        for item in scalar_functions:
            if item["label"] == label:
                return item
        return scalar_functions[0]

    def get_system_spec(self):
        label = self.system_var.get()
        for item in system_functions:
            if item["label"] == label:
                return item
        return system_functions[0]

    def build_scalar_tab(self):
        main = ttk.Frame(self.scalar_tab, padding=10)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        controls = ttk.LabelFrame(main, text="Параметры", padding=10)
        controls.grid(row=0, column=0, sticky="nw", padx=(0, 10), pady=(0, 10))

        ttk.Label(controls, text="Уравнение:").grid(row=0, column=0, sticky="w")
        self.scalar_func_var = tk.StringVar(value=scalar_functions[0]["label"])
        self.scalar_func_cb = ttk.Combobox(
            controls,
            textvariable=self.scalar_func_var,
            values=get_scalar_labels(),
            state="readonly",
            width=42,
        )
        self.scalar_func_cb.grid(row=0, column=1, sticky="we")
        self.scalar_func_cb.bind("<<ComboboxSelected>>", self.on_scalar_func_change)

        ttk.Label(controls, text="Метод:").grid(row=1, column=0, sticky="w")
        self.scalar_method_var = tk.StringVar(value="Newton")
        self.scalar_method_cb = ttk.Combobox(
            controls,
            textvariable=self.scalar_method_var,
            values=["Newton", "Fixed chord"],
            state="readonly",
            width=42,
        )
        self.scalar_method_cb.grid(row=1, column=1, sticky="we")

        ttk.Label(controls, text="a:").grid(row=2, column=0, sticky="w")
        self.scalar_a_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.scalar_a_var, width=20).grid(row=2, column=1, sticky="we")

        ttk.Label(controls, text="b:").grid(row=3, column=0, sticky="w")
        self.scalar_b_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.scalar_b_var, width=20).grid(row=3, column=1, sticky="we")

        ttk.Label(controls, text="eps:").grid(row=4, column=0, sticky="w")
        self.scalar_eps_var = tk.StringVar(value="1e-6")
        ttk.Entry(controls, textvariable=self.scalar_eps_var, width=20).grid(row=4, column=1, sticky="we")

        btns = ttk.Frame(controls)
        btns.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="we")

        ttk.Button(btns, text="Загрузить JSON", command=self.load_scalar_json).pack(side="left", padx=4)
        ttk.Button(btns, text="Решить", command=self.solve_scalar).pack(side="left", padx=4)
        ttk.Button(btns, text="Сохранить", command=self.save_scalar_result).pack(side="left", padx=4)

        out_frame, self.scalar_output = self.make_text_area(main)
        out_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        plot_box = ttk.LabelFrame(main, text="График", padding=5)
        plot_box.grid(row=0, column=1, rowspan=2, sticky="nsew")
        plot_box.rowconfigure(0, weight=1)
        plot_box.columnconfigure(0, weight=1)

        self.scalar_fig = Figure(figsize=(8, 6), dpi=100)
        self.scalar_ax = self.scalar_fig.add_subplot(111)
        self.scalar_canvas = FigureCanvasTkAgg(self.scalar_fig, master=plot_box)
        self.scalar_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        NavigationToolbar2Tk(self.scalar_canvas, plot_box).update()

        self.on_scalar_func_change()

    def build_system_tab(self):
        main = ttk.Frame(self.system_tab, padding=10)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        controls = ttk.LabelFrame(main, text="Параметры", padding=10)
        controls.grid(row=0, column=0, sticky="nw", padx=(0, 10), pady=(0, 10))

        ttk.Label(controls, text="Система:").grid(row=0, column=0, sticky="w")
        self.system_var = tk.StringVar(value=system_functions[0]["label"])
        self.system_cb = ttk.Combobox(
            controls,
            textvariable=self.system_var,
            values=get_system_labels(),
            state="readonly",
            width=52,
        )
        self.system_cb.grid(row=0, column=1, sticky="we")
        self.system_cb.bind("<<ComboboxSelected>>", self.on_system_change)

        ttk.Label(controls, text="Метод:").grid(row=1, column=0, sticky="w")
        self.system_method_var = tk.StringVar(value="Simple iteration")
        ttk.Entry(controls, textvariable=self.system_method_var, state="readonly", width=20).grid(row=1, column=1, sticky="we")

        ttk.Label(controls, text="x0:").grid(row=2, column=0, sticky="w")
        self.system_x0_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.system_x0_var, width=20).grid(row=2, column=1, sticky="we")

        ttk.Label(controls, text="y0:").grid(row=3, column=0, sticky="w")
        self.system_y0_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.system_y0_var, width=20).grid(row=3, column=1, sticky="we")

        ttk.Label(controls, text="eps:").grid(row=4, column=0, sticky="w")
        self.system_eps_var = tk.StringVar(value="1e-6")
        ttk.Entry(controls, textvariable=self.system_eps_var, width=20).grid(row=4, column=1, sticky="we")

        btns = ttk.Frame(controls)
        btns.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="we")

        ttk.Button(btns, text="Загрузить JSON", command=self.load_system_json).pack(side="left", padx=4)
        ttk.Button(btns, text="Решить", command=self.solve_system).pack(side="left", padx=4)
        ttk.Button(btns, text="Сохранить", command=self.save_system_result).pack(side="left", padx=4)

        out_frame, self.system_output = self.make_text_area(main)
        out_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        plot_box = ttk.LabelFrame(main, text="График", padding=5)
        plot_box.grid(row=0, column=1, rowspan=2, sticky="nsew")
        plot_box.rowconfigure(0, weight=1)
        plot_box.columnconfigure(0, weight=1)

        self.system_fig = Figure(figsize=(8, 6), dpi=100)
        self.system_ax = self.system_fig.add_subplot(111)
        self.system_canvas = FigureCanvasTkAgg(self.system_fig, master=plot_box)
        self.system_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        NavigationToolbar2Tk(self.system_canvas, plot_box).update()

        self.on_system_change()

    def on_scalar_func_change(self, event=None):
        spec = self.get_scalar_spec()
        a, b = spec["interval"]
        self.scalar_a_var.set(str(a))
        self.scalar_b_var.set(str(b))
        self.draw_scalar_plot(spec, a, b)

    def on_system_change(self, event=None):
        spec = self.get_system_spec()
        (xmin, xmax), (ymin, ymax) = spec["box"]
        self.system_x0_var.set(str(spec["initial"][0]))
        self.system_y0_var.set(str(spec["initial"][1]))
        self.draw_system_plot(spec, None, (xmin, xmax, ymin, ymax))

    def draw_scalar_plot(self, spec, a, b, root=None):
        f = spec["f"]
        self.scalar_ax.clear()

        xs = np.linspace(a, b, 800)
        ys = np.array([float(f(x)) for x in xs], dtype=float)

        self.scalar_ax.plot(xs, ys, label="f(x)")
        self.scalar_ax.axhline(0, color="black", linewidth=1)
        self.scalar_ax.grid(True, alpha=0.3)
        self.scalar_ax.set_xlim(a, b)
        self.scalar_ax.set_xlabel("x")
        self.scalar_ax.set_ylabel("f(x)")
        self.scalar_ax.set_title(spec["label"])

        if root is not None:
            self.scalar_ax.axvline(root, color="red", linestyle="--", linewidth=1)
            self.scalar_ax.scatter([root], [float(f(root))], color="red")

        self.scalar_ax.legend(loc="best")
        self.scalar_canvas.draw_idle()

    def draw_system_plot(self, spec, solution=None, box=None):
        self.system_ax.clear()

        if box is None:
            (xmin, xmax), (ymin, ymax) = spec["box"]
        else:
            xmin, xmax, ymin, ymax = box

        xs = np.linspace(xmin, xmax, 250)
        ys = np.linspace(ymin, ymax, 250)
        X, Y = np.meshgrid(xs, ys)

        Z1 = np.vectorize(spec["f1"])(X, Y)
        Z2 = np.vectorize(spec["f2"])(X, Y)

        self.system_ax.contour(X, Y, Z1, levels=[0], colors="blue", linewidths=2)
        self.system_ax.contour(X, Y, Z2, levels=[0], colors="red", linewidths=2)

        self.system_ax.grid(True, alpha=0.3)
        self.system_ax.set_aspect("equal", adjustable="box")
        self.system_ax.set_xlim(xmin, xmax)
        self.system_ax.set_ylim(ymin, ymax)
        self.system_ax.set_xlabel("x")
        self.system_ax.set_ylabel("y")
        self.system_ax.set_title(spec["label"])

        legend_items = [
            Line2D([], [], color="blue", label="f1 = 0"),
            Line2D([], [], color="red", label="f2 = 0"),
        ]
        if solution is not None:
            self.system_ax.scatter([solution[0]], [solution[1]], color="green", s=50, label="solution")
            legend_items.append(Line2D([], [], color="green", marker="o", linestyle="None", label="solution"))

        self.system_ax.legend(handles=legend_items, loc="best")
        self.system_canvas.draw_idle()

    def solve_scalar(self):
        spec = self.get_scalar_spec()
        f = spec["f"]
        df = spec["df"]
        d2f = spec["d2f"]
        method_name = self.scalar_method_var.get()

        try:
            a = float(self.scalar_a_var.get())
            b = float(self.scalar_b_var.get())
            eps = float(self.scalar_eps_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный ввод a, b или eps.")
            return

        try:
            find_unique_root_interval(f, a, b)
        except Exception as exc:
            messagebox.showerror("Проверка интервала", str(exc))
            self.scalar_output.delete("1.0", tk.END)
            self.scalar_output.insert(tk.END, str(exc))
            self.draw_scalar_plot(spec, a, b)
            return

        try:
            if method_name == "Newton":
                x0 = choose_newton_start(f, d2f, a, b)
                result = newton_method(f, df, x0, eps)
            elif method_name == "Fixed chord":
                fixed_point, x0 = choose_chord_data(f, d2f, a, b)
                result = fixed_chord_method(f, fixed_point, x0, eps)
            else:
                raise ValueError("Неизвестный метод.")
        except Exception as exc:
            messagebox.showerror("Ошибка решения", str(exc))
            self.scalar_output.delete("1.0", tk.END)
            self.scalar_output.insert(tk.END, str(exc))
            self.draw_scalar_plot(spec, a, b)
            return

        self.scalar_result_text = (
            f"Уравнение: {spec['label']}\n"
            f"Метод: {result.method}\n"
            f"Интервал: [{a}, {b}]\n"
            f"x0: {result.x0:.10f}\n"
            f"Корень: {result.root:.10f}\n"
            f"f(root): {result.value:.3e}\n"
            f"Итераций: {result.iterations}\n"
            f"Погрешности:\n{', '.join(f'{e:.3e}' for e in result.errors)}\n"
        )

        self.scalar_output.delete("1.0", tk.END)
        self.scalar_output.insert(tk.END, self.scalar_result_text)
        self.draw_scalar_plot(spec, a, b, result.root)

    def solve_system(self):
        spec = self.get_system_spec()
        phi = spec["phi"]
        phi_jacobian = spec["phi_jacobian"]
        method_name = self.system_method_var.get()

        try:
            x0 = float(self.system_x0_var.get())
            y0 = float(self.system_y0_var.get())
            eps = float(self.system_eps_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный ввод x0, y0 или eps.")
            return

        ok, max_norm = check_system_convergence(phi_jacobian, spec["box"])
        if not ok:
            messagebox.showerror(
                "Проверка сходимости",
                f"Достаточное условие сходимости не выполнено: max ||J(phi)||_∞ = {max_norm:.6f} >= 1."
            )
            return

        try:
            if method_name != "Simple iteration":
                raise ValueError("Для системы реализован только метод простой итерации.")

            result = simple_iteration_system(phi, x0, y0, eps)
            f1 = spec["f1"]
            f2 = spec["f2"]
            result.residuals = (float(f1(result.x, result.y)), float(f2(result.x, result.y)))
        except Exception as exc:
            messagebox.showerror("Ошибка решения", str(exc))
            self.system_output.delete("1.0", tk.END)
            self.system_output.insert(tk.END, str(exc))
            return

        self.system_result_text = (
            f"Система: {spec['label']}\n"
            f"Метод: {result.method}\n"
            f"x1 = {result.x:.10f}\n"
            f"x2 = {result.y:.10f}\n"
            f"F1(x1, x2) = {result.residuals[0]:.3e}\n"
            f"F2(x1, x2) = {result.residuals[1]:.3e}\n"
            f"Итераций: {result.iterations}\n"
            f"Погрешности:\n"
        )

        for i, (dx, dy) in enumerate(result.errors, start=1):
            self.system_result_text += f"{i}: |dx| = {dx:.3e}, |dy| = {dy:.3e}\n"

        self.system_output.delete("1.0", tk.END)
        self.system_output.insert(tk.END, self.system_result_text)
        self.draw_system_plot(spec, (result.x, result.y))

    def load_scalar_json(self):
        path = filedialog.askopenfilename(
            title="Open JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {exc}")
            return

        if "function" in data:
            self.scalar_func_var.set(data["function"])
        if "method" in data:
            self.scalar_method_var.set(data["method"])
        if "a" in data:
            self.scalar_a_var.set(str(data["a"]))
        if "b" in data:
            self.scalar_b_var.set(str(data["b"]))
        if "eps" in data:
            self.scalar_eps_var.set(str(data["eps"]))

    def load_system_json(self):
        path = filedialog.askopenfilename(
            title="Open JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {exc}")
            return

        if "system" in data:
            self.system_var.set(data["system"])
        if "x0" in data:
            self.system_x0_var.set(str(data["x0"]))
        if "y0" in data:
            self.system_y0_var.set(str(data["y0"]))
        if "eps" in data:
            self.system_eps_var.set(str(data["eps"]))

    def save_scalar_result(self):
        if not self.scalar_result_text:
            messagebox.showinfo("Сохранение", "Нет результата для сохранения.")
            return

        path = filedialog.asksaveasfilename(
            title="Save result",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.scalar_result_text)
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {exc}")

    def save_system_result(self):
        if not self.system_result_text:
            messagebox.showinfo("Сохранение", "Нет результата для сохранения.")
            return

        path = filedialog.asksaveasfilename(
            title="Save result",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.system_result_text)
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {exc}")


if __name__ == "__main__":
    app = App()
    app.mainloop()