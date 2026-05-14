from dataclasses import dataclass
from typing import Callable, List, Tuple

import numpy as np


@dataclass
class ScalarResult:
    root: float
    value: float
    iterations: int
    errors: List[float]
    x0: float
    method: str


@dataclass
class SystemResult:
    x: float
    y: float
    residuals: Tuple[float, float]
    iterations: int
    errors: List[Tuple[float, float]]
    method: str


def find_unique_root_interval(
    f: Callable[[float], float],
    a: float,
    b: float,
    grid: int = 2000,
    tol: float = 1e-10,
):
    if a >= b:
        raise ValueError("Левая граница интервала должна быть меньше правой.")

    xs = np.linspace(a, b, grid + 1)
    ys = np.array([float(f(x)) for x in xs], dtype=float)

    intervals = []

    for i in range(grid):
        y1 = ys[i]
        y2 = ys[i + 1]

        if abs(y1) <= tol:
            intervals.append((xs[i], xs[i]))
        elif y1 * y2 < 0:
            intervals.append((xs[i], xs[i + 1]))

    if abs(ys[-1]) <= tol:
        intervals.append((b, b))

    merged = []
    step = (b - a) / grid

    for interval in intervals:
        if not merged:
            merged.append(interval)
            continue

        prev = merged[-1]
        if interval[0] <= prev[1] + step:
            merged[-1] = (min(prev[0], interval[0]), max(prev[1], interval[1]))
        else:
            merged.append(interval)

    if len(merged) == 0:
        raise ValueError("На заданном интервале корень не найден.")
    if len(merged) > 1:
        raise ValueError("На заданном интервале найдено несколько корней. Уточните интервал.")

    return merged[0]


def choose_newton_start(f, d2f, a, b):
    if f(a) * d2f(a) > 0:
        return a
    if f(b) * d2f(b) > 0:
        return b
    return 0.5 * (a + b)


def choose_chord_data(f, d2f, a, b):
    if f(a) * d2f(a) > 0:
        return a, b
    if f(b) * d2f(b) > 0:
        return b, a
    return a, b


def newton_method(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    eps: float,
    max_iter: int = 1000,
):
    x = float(x0)
    errors = []

    for k in range(1, max_iter + 1):
        dfx = float(df(x))
        if abs(dfx) < 1e-14:
            raise ValueError("Производная близка к нулю, метод Ньютона неприменим.")

        x_new = x - float(f(x)) / dfx
        err = abs(x_new - x)
        errors.append(err)

        if err <= eps:
            return ScalarResult(
                root=x_new,
                value=float(f(x_new)),
                iterations=k,
                errors=errors,
                x0=x0,
                method="Newton",
            )

        x = x_new

    raise RuntimeError("Метод Ньютона не сошелся за максимальное число итераций.")


def fixed_chord_method(
    f: Callable[[float], float],
    fixed_point: float,
    x0: float,
    eps: float,
    max_iter: int = 1000,
):
    x = float(x0)
    c = float(fixed_point)
    fc = float(f(c))
    errors = []

    for k in range(1, max_iter + 1):
        fx = float(f(x))
        denom = fc - fx
        if abs(denom) < 1e-14:
            raise ValueError("Деление на ноль в методе хорд.")

        x_new = x - fx * (c - x) / denom
        err = abs(x_new - x)
        errors.append(err)

        if err <= eps:
            return ScalarResult(
                root=x_new,
                value=float(f(x_new)),
                iterations=k,
                errors=errors,
                x0=x0,
                method="Fixed chord",
            )

        x = x_new

    raise RuntimeError("Метод хорд не сошелся за максимальное число итераций.")


def check_scalar_iteration_convergence(phi_prime, a, b, grid: int = 400):
    xs = np.linspace(a, b, grid)
    values = np.array([abs(float(phi_prime(x))) for x in xs], dtype=float)
    max_value = float(np.max(values))
    return max_value < 1.0, max_value


def check_system_convergence(phi_jacobian, box, grid: int = 15):
    (xmin, xmax), (ymin, ymax) = box
    xs = np.linspace(xmin, xmax, grid)
    ys = np.linspace(ymin, ymax, grid)

    max_norm = 0.0
    for x in xs:
        for y in ys:
            j = np.array(phi_jacobian(float(x), float(y)), dtype=float)
            norm_inf = float(np.max(np.sum(np.abs(j), axis=1)))
            max_norm = max(max_norm, norm_inf)

    return max_norm < 1.0, max_norm


def simple_iteration_system(
    phi: Callable[[float, float], Tuple[float, float]],
    x0: float,
    y0: float,
    eps: float,
    max_iter: int = 200,
):
    x = float(x0)
    y = float(y0)
    errors = []

    for k in range(1, max_iter + 1):
        x_new, y_new = phi(x, y)
        x_new = float(x_new)
        y_new = float(y_new)

        err = (abs(x_new - x), abs(y_new - y))
        errors.append(err)

        if max(err) <= eps:
            return SystemResult(
                x=x_new,
                y=y_new,
                residuals=(np.nan, np.nan),
                iterations=k,
                errors=errors,
                method="Simple iteration",
            )

        x, y = x_new, y_new

    raise RuntimeError("Метод простой итерации для системы не сошелся за максимальное число итераций.")