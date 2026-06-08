from __future__ import annotations

from math import factorial
from typing import Sequence

from interpolation.differences import build_forward_difference_table
from utils.checks import check_uniform_grid


def _gauss_factor(argument: float, order: int) -> float:
    if order == 0:
        return 1.0

    product = argument
    if order == 1:
        return product

    offset = 1
    sign_positive = True
    current = 1

    while current < order:
        if sign_positive:
            product = product * (argument + offset)
        else:
            product = product * (argument - offset)
            offset += 1
        sign_positive = not sign_positive
        current += 1

    return product / factorial(order)


def gauss_value(point: float, grid_x: Sequence[float], grid_y: Sequence[float]) -> float:
    is_uniform, step = check_uniform_grid(grid_x)
    if not is_uniform:
        raise ValueError("Формула Гаусса требует равномерную сетку.")

    table = build_forward_difference_table(grid_y)

    center = 0
    best_distance = abs(point - grid_x[0])
    index = 1
    while index < len(grid_x):
        distance = abs(point - grid_x[index])
        if distance < best_distance:
            best_distance = distance
            center = index
        index += 1

    argument = (point - grid_x[center]) / step
    result = grid_y[center]

    order = 1
    while order < len(grid_x):
        table_index = center - ((order + 1) // 2)
        if table_index < 0 or table_index >= len(table[order]):
            break
        result = result + _gauss_factor(argument, order) * table[order][table_index]
        order += 1

    return result


gauss_interpolate = gauss_value
