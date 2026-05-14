from math import sin, cos, sqrt, atan

def f1(x):
    return x ** 3 - 2 * x + 1


def F1(x):
    return x ** 4 / 4 - x ** 2 + x


def f2(x):
    return x ** 2 + 2 * x + 1


def F2(x):
    return x ** 3 / 3 + x ** 2 + x


def f3(x):
    return sin(x)


def F3(x):
    return -cos(x)


def f4(x):
    return cos(x)


def F4(x):
    return sin(x)


def f5(x):
    return 1 / (1 + x * x)


def F5(x):
    return atan(x)


REGULAR_FUNCTIONS = {
    1: ("f(x) = x^3 - 2x + 1", f1, F1),
    2: ("f(x) = x^2 + 2x + 1", f2, F2),
    3: ("f(x) = sin(x)", f3, F3),
    4: ("f(x) = cos(x)", f4, F4),
    5: ("f(x) = 1 / (1 + x^2)", f5, F5),
}


def exact_integral_regular(func_key, a, b):
    _, _, F = REGULAR_FUNCTIONS[func_key]
    return F(b) - F(a)


def imp1(x):
    return 1 / sqrt(x) + x


def imp2(x):
    return 1 / sqrt(1 - x) + x


def imp3(x):
    return 1 / sqrt(abs(x - 0.5)) + x


def imp4(x):
    return 1 / ((x - 0.5) ** 2) + x


IMPROPER_FUNCTIONS = {
    1: {
        "name": "∫_0^1 (1/sqrt(x) + x) dx",
        "func": imp1,
        "a": 0.0,
        "b": 1.0,
        "singularity": "a",
    },
    2: {
        "name": "∫_0^1 (1/sqrt(1-x) + x) dx",
        "func": imp2,
        "a": 0.0,
        "b": 1.0,
        "singularity": "b",
    },
    3: {
        "name": "∫_0^1 (1/sqrt(|x-0.5|) + x) dx",
        "func": imp3,
        "a": 0.0,
        "b": 1.0,
        "singularity": "inside",
        "c": 0.5,
    },
    4: {
        "name": "∫_0^1 (1/(x-0.5)^2 + x) dx",
        "func": imp4,
        "a": 0.0,
        "b": 1.0,
        "singularity": "inside",
        "c": 0.5,
    },
}