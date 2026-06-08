from __future__ import annotations

import math
from typing import List, Sequence, Tuple


def parse_float(text: str) -> float:
    cleaned = text.strip().replace(" ", "").replace(",", ".")
    if cleaned == "":
        raise ValueError("Пустое значение нельзя преобразовать в число.")

    try:
        value = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"Некорректное число: {text!r}") from exc

    if not math.isfinite(value):
        raise ValueError(f"Некорректное число: {text!r}")

    return value


def ensure_same_length(x: Sequence[float], y: Sequence[float]) -> None:
    if len(x) != len(y):
        raise ValueError("Списки x и y должны иметь одинаковую длину.")


def ensure_min_points(x: Sequence[float]) -> None:
    if len(x) < 2:
        raise ValueError("Нужно минимум две точки.")


def sort_and_validate_points(
    x: Sequence[float],
    y: Sequence[float],
    eps: float = 1e-12,
) -> Tuple[List[float], List[float]]:
    ensure_same_length(x, y)
    ensure_min_points(x)

    pairs: List[Tuple[float, float]] = []
    index = 0
    while index < len(x):
        xi = float(x[index])
        yi = float(y[index])
        if not math.isfinite(xi) or not math.isfinite(yi):
            raise ValueError("Все значения x и y должны быть конечными числами.")
        pairs.append((xi, yi))
        index += 1

    pairs.sort(key=lambda item: item[0])

    sorted_x: List[float] = []
    sorted_y: List[float] = []

    index = 0
    while index < len(pairs):
        xi, yi = pairs[index]

        if index > 0:
            prev_x, prev_y = pairs[index - 1]
            if abs(xi - prev_x) <= eps:
                if abs(yi - prev_y) > eps:
                    raise ValueError(
                        "Обнаружены одинаковые значения x с разными y. Такой набор точек недопустим."
                    )
                raise ValueError("Обнаружены повторяющиеся значения x. Такие точки недопустимы.")

        sorted_x.append(xi)
        sorted_y.append(yi)
        index += 1

    return sorted_x, sorted_y


def check_uniform_grid(x: Sequence[float], eps: float = 1e-10) -> Tuple[bool, float]:
    if len(x) < 2:
        return False, 0.0

    step = x[1] - x[0]
    index = 1
    while index < len(x) - 1:
        current_step = x[index + 1] - x[index]
        if abs(current_step - step) > eps:
            return False, step
        index += 1

    return True, step
