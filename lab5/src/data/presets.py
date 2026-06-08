from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

PRESET_TABLES: Dict[str, Tuple[List[float], List[float]]] = {
    "Вариант 4": (
        [1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65],
        [0.1213, 1.1316, 2.1459, 3.1565, 4.1571, 5.1819, 6.1969],
    ),
    "Тест 1": (
        [0.0, 0.5, 1.0, 1.5, 2.0],
        [1.0, 1.6487, 2.7183, 4.4817, 7.3891],
    ),
    "Тест 2": (
        [1.0, 1.2, 1.4, 1.6, 1.8],
        [0.0, 0.1823, 0.3365, 0.4700, 0.5878],
    ),
    "Тест 3": (
        [2.0, 2.2, 2.4, 2.6, 2.8],
        [math.log(2.0), math.log(2.2), math.log(2.4), math.log(2.6), math.log(2.8)],
    ),
}

FUNCTIONS: Dict[str, Callable[[float], float]] = {
    "sin(x)": math.sin,
    "cos(x)": math.cos,
    "exp(x)": math.exp,
    "x^2": lambda value: value * value,
    "x^3": lambda value: value ** 3,
}


def preset_names() -> List[str]:
    names: List[str] = []
    for key in PRESET_TABLES:
        names.append(key)
    return names


def function_names() -> List[str]:
    names: List[str] = []
    for key in FUNCTIONS:
        names.append(key)
    return names
