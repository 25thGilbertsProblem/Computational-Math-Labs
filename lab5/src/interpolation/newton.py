from __future__ import annotations

from typing import List, Sequence

from interpolation.differences import build_forward_difference_table
from utils.checks import check_uniform_grid


def divided_difference_coefficients(grid_x: Sequence[float], grid_y: Sequence[float]) -> List[float]:
    count = len(grid_x)
    coefficients: List[float] = []

    index = 0
    while index < count:
        coefficients.append(float(grid_y[index]))
        index += 1

    order = 1
    while order < count:
        index = count - 1
        while index >= order:
            left = coefficients[index - 1]
            right = coefficients[index]
            coefficients[index] = (right - left) / (grid_x[index] - grid_x[index - order])
            index -= 1
        order += 1

    return coefficients


def newton_divided_value(point: float, grid_x: Sequence[float], coefficients: Sequence[float]) -> float:
    result = coefficients[0]
    factor = 1.0

    index = 1
    while index < len(grid_x):
        factor = factor * (point - grid_x[index - 1])
        result = result + coefficients[index] * factor
        index += 1

    return result


def newton_forward_value(point: float, grid_x: Sequence[float], grid_y: Sequence[float]) -> float:
    is_uniform, step = check_uniform_grid(grid_x)
    if not is_uniform:
        raise ValueError("Для формулы Ньютона по конечным разностям требуется равномерная сетка.")

    table = build_forward_difference_table(grid_y)
    argument = (point - grid_x[0]) / step

    result = table[0][0]
    factor = 1.0
    order = 1
    while order < len(grid_x):
        factor = factor * (argument - (order - 1)) / order
        result = result + factor * table[order][0]
        order += 1

    return result


def newton_backward_value(point: float, grid_x: Sequence[float], grid_y: Sequence[float]) -> float:
    is_uniform, step = check_uniform_grid(grid_x)
    if not is_uniform:
        raise ValueError("Для формулы Ньютона по конечным разностям требуется равномерная сетка.")

    table = build_forward_difference_table(grid_y)
    argument = (point - grid_x[-1]) / step

    result = table[0][-1]
    factor = 1.0
    order = 1
    while order < len(grid_x):
        factor = factor * (argument + (order - 1)) / order
        if order < len(table):
            result = result + factor * table[order][-1]
        order += 1

    return result


def newton_finite_value(point: float, grid_x: Sequence[float], grid_y: Sequence[float]) -> float:
    middle = (grid_x[0] + grid_x[-1]) / 2
    if point <= middle:
        return newton_forward_value(point, grid_x, grid_y)
    return newton_backward_value(point, grid_x, grid_y)


build_coefficients = divided_difference_coefficients
newton_divided_interpolate = newton_divided_value
newton_forward = newton_forward_value
newton_backward = newton_backward_value
interpolate_newton_finite = newton_finite_value
