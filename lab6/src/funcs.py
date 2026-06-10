import math
class ODEProblem:
    def __init__(self, name, f, exact, x0_default, y0_default, xn_default, h_default):
        self.name = name
        self.f = f
        self.exact = exact
        self.x0_default = x0_default
        self.y0_default = y0_default
        self.xn_default = xn_default
        self.h_default = h_default

def f1(x, y):
    return y - x * x + 1


def exact1(x, x0, y0):
    c = (y0 - (x0 + 1)**2) * math.exp(-x0)
    return (x + 1)**2 + c * math.exp(x)


def f2(x, y):
    return x + y


def exact2(x, x0, y0):
    c = (y0 + x0 + 1.0) * math.exp(-x0)
    return c * math.exp(x) - x - 1.0


def f3(x, y):
    return y * (1.0 - y)

def exact3(x, x0, y0):
    return 1.0 / (1.0 + c3(x0, y0) * math.exp(-x))

def c3(x0, y0):
    return math.exp(x0) * (1/y0 - 1)

PROBLEMS = []
PROBLEMS.append(
    ODEProblem(
        "y' = y - x^2 + 1",
        f1,
        exact1,
        0.0,
        0.5,
        2.0,
        0.25,
    )
)
PROBLEMS.append(
    ODEProblem(
        "y' = x + y",
        f2,
        exact2,
        0.0,
        1.0,
        1.0,
        0.2,
    )
)
PROBLEMS.append(
    ODEProblem(
        "y' = y(1-y)",
        f3,
        exact3,
        0.0,
        0.1,
        5.0,
        0.5,
    )
)