from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from interpolation.gauss import gauss_value
from interpolation.lagrange import lagrange_value
from interpolation.newton import (
    divided_difference_coefficients,
    newton_divided_value,
    newton_finite_value,
)
from utils.checks import (
    check_uniform_grid,
    ensure_min_points,
    ensure_same_length,
    sort_and_validate_points,
)
from utils.plotting import build_figure, interpolation_residuals

from views.help_window import HelpWindow
from views.left import LeftPanel
from views.right import RightPanel


class RootWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Интерполяция функции")
        self.root.geometry("1400x850")

        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        self.right_panel = RightPanel(self.main_paned)
        self.left_panel = LeftPanel(
            self.main_paned,
            on_calculate=self.calculate,
            on_help=self.show_help,
        )

        self.main_paned.add(self.left_panel, weight=1)
        self.main_paned.add(self.right_panel, weight=5)

    def show_help(self) -> None:
        HelpWindow(self.root)

    def _format_results(self, x0, x, y, method_choice: str) -> str:
        ensure_same_length(x, y)
        ensure_min_points(x)

        uniform, step = check_uniform_grid(x)

        lines = []
        lines.append("Исходные данные:")
        lines.append("x = " + ", ".join(f"{value:.6f}" for value in x))
        lines.append("y = " + ", ".join(f"{value:.6f}" for value in y))
        lines.append("")
        if uniform:
            lines.append(f"Шаг сетки: {step:.6f}")
        else:
            lines.append("Сетка неравномерная.")
        lines.append("")

        values = []

        if method_choice == "Все" or method_choice == "Лагранж":
            values.append(("Лагранж", lagrange_value(x0, x, y)))

        if method_choice == "Все" or method_choice == "Ньютон (разделённые разности)":
            coeffs = divided_difference_coefficients(x, y)
            values.append(("Ньютон (разделённые разности)", newton_divided_value(x0, x, coeffs)))

        if uniform and (method_choice == "Все" or method_choice == "Ньютон (конечные разности)"):
            values.append(("Ньютон (конечные разности)", newton_finite_value(x0, x, y)))

        if uniform and (method_choice == "Все" or method_choice == "Гаусс"):
            values.append(("Гаусс", gauss_value(x0, x, y)))

        if len(values) == 0:
            lines.append("Для выбранного метода необходимы равноотстоящие узлы.")
            return "\n".join(lines)

        lines.append(f"Вычисление в точке x0 = {x0:.6f}:")
        index = 0
        while index < len(values):
            name, value = values[index]
            lines.append(f"  {name}: {value:.12f}")
            index += 1

        return "\n".join(lines)

    def calculate(self, x, y, x0, method_choice: str, error: str | None = None):
        if error is not None:
            self.right_panel.set_result_text(f"Ошибка: {error}")
            self.right_panel.clear_difference_table()
            self.right_panel.clear_plot()
            return

        try:
            x_sorted, y_sorted = sort_and_validate_points(x, y)
            uniform, _ = check_uniform_grid(x_sorted)

            text = self._format_results(x0, x_sorted, y_sorted, method_choice)
            self.right_panel.set_result_text(text)
            self.right_panel.set_difference_table(x_sorted, y_sorted)

            methods_to_plot = []

            if method_choice == "Все":
                methods_to_plot.append("Лагранж")
                methods_to_plot.append("Ньютон (разделённые разности)")

                if uniform:
                    methods_to_plot.append("Ньютон (конечные разности)")
                    methods_to_plot.append("Гаусс")
            else:
                methods_to_plot.append(method_choice)

            max_error = 0.0
            index = 0
            while index < len(methods_to_plot):
                current_method = methods_to_plot[index]
                current_error, _ = interpolation_residuals(x_sorted, y_sorted, current_method)
                if current_error > max_error:
                    max_error = current_error
                index += 1

            if max_error > 1e-7:
                text = text + f"\n\nПредупреждение: максимальная невязка в узлах для графика {max_error:.3e}."
                self.right_panel.set_result_text(text)

            fig = build_figure(x_sorted, y_sorted, x0=x0, methods=methods_to_plot)
            self.right_panel.set_plot(fig)

        except Exception as exc:
            self.right_panel.set_result_text(f"Ошибка вычислений: {exc}")
            self.right_panel.clear_difference_table()
            self.right_panel.clear_plot()

    def run(self) -> None:
        self.root.mainloop()