from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from utils.checks import parse_float


def read_table_from_file(path: str | Path) -> Tuple[List[float], List[float]]:
    x: List[float] = []
    y: List[float] = []

    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace(",", ".").split()
            if len(parts) < 2:
                continue
            x.append(parse_float(parts[0]))
            y.append(parse_float(parts[1]))

    if len(x) < 2:
        raise ValueError("В файле должно быть минимум две строки с парами x y.")

    return x, y
