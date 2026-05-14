import numpy as np


scalar_functions = [
    {
        "label": "x^3 - x - 2",
        "f": lambda x: x**3 - x - 2,
        "df": lambda x: 3 * x**2 - 1,
        "d2f": lambda x: 6 * x,
        "interval": (1.0, 2.0),
    },
    {
        "label": "cos(x) - x",
        "f": lambda x: np.cos(x) - x,
        "df": lambda x: -np.sin(x) - 1,
        "d2f": lambda x: -np.cos(x),
        "interval": (0.0, 1.0),
    },
    {
        "label": "exp(-x) - x",
        "f": lambda x: np.exp(-x) - x,
        "df": lambda x: -np.exp(-x) - 1,
        "d2f": lambda x: np.exp(-x),
        "interval": (0.0, 1.0),
    },
    {
        "label": "x^2 - 2",
        "f": lambda x: x**2 - 2,
        "df": lambda x: 2 * x,
        "d2f": lambda x: 2.0,
        "interval": (1.0, 2.0),
    },
    {
        "label": "sin(x) - 0.5",
        "f": lambda x: np.sin(x) - 0.5,
        "df": lambda x: np.cos(x),
        "d2f": lambda x: -np.sin(x),
        "interval": (0.0, 2.0),
    },
]


system_functions = [
    {
        "label": "x = 0.5 cos(y), y = 0.5 sin(x)",
        "f1": lambda x, y: x - 0.5 * np.cos(y),
        "f2": lambda x, y: y - 0.5 * np.sin(x),
        "phi": lambda x, y: (0.5 * np.cos(y), 0.5 * np.sin(x)),
        "phi_jacobian": lambda x, y: np.array(
            [
                [0.0, -0.5 * np.sin(y)],
                [0.5 * np.cos(x), 0.0],
            ],
            dtype=float,
        ),
        "box": ((-1.0, 1.0), (-1.0, 1.0)),
        "initial": (0.4, 0.2),
    },
    {
        "label": "x = 0.3 + 0.1 cos(y), y = 0.2 + 0.1 sin(x)",
        "f1": lambda x, y: x - 0.3 - 0.1 * np.cos(y),
        "f2": lambda x, y: y - 0.2 - 0.1 * np.sin(x),
        "phi": lambda x, y: (0.3 + 0.1 * np.cos(y), 0.2 + 0.1 * np.sin(x)),
        "phi_jacobian": lambda x, y: np.array(
            [
                [0.0, -0.1 * np.sin(y)],
                [0.1 * np.cos(x), 0.0],
            ],
            dtype=float,
        ),
        "box": ((0.0, 1.0), (0.0, 1.0)),
        "initial": (0.35, 0.25),
    },
]


def get_scalar_labels():
    return [item["label"] for item in scalar_functions]


def get_system_labels():
    return [item["label"] for item in system_functions]