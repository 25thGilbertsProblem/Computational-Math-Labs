from __future__ import annotations

from typing import Sequence

def lagrange_value(point: float, grid_x: Sequence[float], grid_y: Sequence[float]) -> float:
    count = len(grid_x)
    total = 0.0

    i = 0
    while i < count:
        basis = grid_y[i]
        j = 0
        while j < count:
            if j != i:
                numerator = point - grid_x[j]
                denominator = grid_x[i] - grid_x[j]
                basis = basis * numerator / denominator
            j += 1
        total += basis
        i += 1

    return total


lagrange_interpolate = lagrange_value
