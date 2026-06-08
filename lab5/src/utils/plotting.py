from __future__ import annotations

from typing import Callable, Sequence, Tuple, List

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure

from interpolation.gauss import gauss_value
from interpolation.lagrange import lagrange_value
from interpolation.newton import (
    divided_difference_coefficients,
    newton_divided_value,
    newton_finite_value,
)
from utils.checks import check_uniform_grid


def build_interpolator(method: str, x: Sequence[float], y: Sequence[float]) -> Callable[[float], float]:
    if method == "Лагранж":
        return lambda value: lagrange_value(value, x, y)

    if method == "Ньютон (разделённые разности)":
        coeffs = divided_difference_coefficients(x, y)
        return lambda value: newton_divided_value(value, x, coeffs)

    if method == "Ньютон (конечные разности)":
        return lambda value: newton_finite_value(value, x, y)

    if method == "Гаусс":
        return lambda value: gauss_value(value, x, y)

    return lambda value: lagrange_value(value, x, y)


def interpolation_residuals(x: Sequence[float], y: Sequence[float], method: str) -> Tuple[float, float]:
    interpolator = build_interpolator(method, x, y)
    max_error = 0.0
    sum_error = 0.0

    index = 0
    while index < len(x):
        current_error = abs(interpolator(x[index]) - y[index])
        sum_error += current_error
        if current_error > max_error:
            max_error = current_error
        index += 1

    return max_error, sum_error


def _allowed_methods(x: Sequence[float], requested: List[str]) -> List[str]:
    uniform, _ = check_uniform_grid(x)
    if uniform:
        return requested
    result = []
    index = 0
    while index < len(requested):
        name = requested[index]
        if name not in ("Ньютон (конечные разности)", "Гаусс"):
            result.append(name)
        index += 1
    return result


def build_figure(
    x: Sequence[float],
    y: Sequence[float],
    x0: float | None = None,
    methods: List[str] | None = None,
    grid_points: int = 2500,
) -> Figure:
    fig = Figure(figsize=(7.2, 4.8), dpi=100)
    ax = fig.add_subplot(111)

    if len(x) == 0:
        ax.set_title("Нет данных для графика")
        return fig

    if methods is None or len(methods) == 0:
        methods = ["Лагранж"]

    methods = _allowed_methods(x, methods)

    left = x[0]
    right = x[0]
    index = 1
    while index < len(x):
        if x[index] < left:
            left = x[index]
        if x[index] > right:
            right = x[index]
        index += 1

    dense_points = []
    step = (right - left) / (grid_points - 1)
    index = 0
    while index < grid_points:
        dense_points.append(left + index * step)
        index += 1

    merged = []
    index = 0
    while index < len(dense_points):
        merged.append(dense_points[index])
        index += 1

    index = 0
    while index < len(x):
        merged.append(x[index])
        index += 1

    merged.sort()

    xs = []
    index = 0
    while index < len(merged):
        if index == 0 or abs(merged[index] - merged[index - 1]) > 1e-14:
            xs.append(merged[index])
        index += 1

    ax.plot(x, y, linestyle="none", marker="o", markersize=5, label="Узлы")

    index = 0
    while index < len(x):
        ax.annotate(
            f"{index + 1}",
            (x[index], y[index]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
        )
        index += 1

    method_index = 0
    while method_index < len(methods):
        method = methods[method_index]
        interpolator = build_interpolator(method, x, y)

        ys = []
        point_index = 0
        while point_index < len(xs):
            ys.append(interpolator(xs[point_index]))
            point_index += 1

        ax.plot(xs, ys, linewidth=1.6, label=f"Интерполяция: {method}")
        method_index += 1

    if x0 is not None:
        ax.axvline(x0, linestyle="--", linewidth=1.0, label=f"x0 = {x0:.4f}")

    ax.grid(True)
    ax.legend()
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Интерполяция функции")
    fig.tight_layout()
    return fig


build_interpolated_figure = build_figure
get_interpolator = build_interpolator