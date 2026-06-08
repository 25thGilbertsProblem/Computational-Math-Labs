from __future__ import annotations

from typing import List, Sequence


def build_forward_difference_table(values: Sequence[float]) -> List[List[float]]:
    rows: List[List[float]] = []

    first_row: List[float] = []
    index = 0
    while index < len(values):
        first_row.append(float(values[index]))
        index += 1
    rows.append(first_row)

    order = 1
    while order < len(values):
        previous = rows[order - 1]
        current: List[float] = []
        index = 0
        while index < len(previous) - 1:
            current.append(previous[index + 1] - previous[index])
            index += 1
        rows.append(current)
        order += 1

    return rows


def difference_table_rows(x_values: Sequence[float], y_values: Sequence[float]) -> List[List[str]]:
    table = build_forward_difference_table(y_values)
    result: List[List[str]] = []

    row_index = 0
    while row_index < len(x_values):
        row: List[str] = []
        row.append(f"{x_values[row_index]:.6f}")
        row.append(f"{table[0][row_index]:.6f}")

        order = 1
        while order < len(x_values):
            if row_index < len(table[order]):
                row.append(f"{table[order][row_index]:.6f}")
            else:
                row.append("")
            order += 1

        result.append(row)
        row_index += 1

    return result


finite_differences = build_forward_difference_table
table_rows = difference_table_rows
