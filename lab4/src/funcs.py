import math
from typing import List, Tuple


_EPS = 1e-12


def sx(points: List[float]) -> float:
    _sum: float = 0.0
    for i in range(len(points)):
        _sum += points[i]
    return _sum


def sxx(points: List[float]) -> float:
    _sum: float = 0.0
    for i in range(len(points)):
        v = points[i]
        _sum += v * v
    return _sum


def sxy(x: List[float], y: List[float]) -> float:
    if len(x) != len(y):
        raise ValueError("Массивы x и y должны быть одинаковой длины.")
    _sum: float = 0.0
    for i in range(len(x)):
        _sum += x[i] * y[i]
    return _sum


def sxn(points: List[float], power: int) -> float:
    _sum: float = 0.0
    for i in range(len(points)):
        _sum += points[i] ** power
    return _sum


def det(m: List[List[float]]) -> float:
    n = len(m)
    if n == 0:
        return 1.0
    if any(len(row) != n for row in m):
        raise ValueError("Матрица должна быть квадратной.")
    a = [row[:] for row in m]
    sign = 1.0
    eps = 1e-12

    for i in range(n):
        pivot = i
        for r in range(i, n):
            if abs(a[r][i]) > abs(a[pivot][i]):
                pivot = r
        if abs(a[pivot][i]) < eps:
            return 0.0
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            sign *= -1.0

        pivot_val = a[i][i]
        for r in range(i + 1, n):
            factor = a[r][i] / pivot_val
            for c in range(i, n):
                a[r][c] -= factor * a[i][c]

    d = sign
    for i in range(n):
        d *= a[i][i]
    return d


def linear_approx(x: List[float], y: List[float], n: int) -> Tuple[float, float]:
    if n != len(x) or n != len(y):
        raise ValueError("n должен совпадать с длиной списков x и y.")
    d = sxx(x) * n - sx(x) * sx(x)
    if abs(d) < _EPS:
        raise ValueError("Невозможно построить линейную аппроксимацию: вырожденная система.")
    d1 = sxy(x, y) * n - sx(x) * sx(y)
    d2 = sxx(x) * sx(y) - sx(x) * sxy(x, y)
    app1 = d1 / d
    app2 = d2 / d
    return app2, app1


def polinom_approx(x: List[float], y: List[float], n: int, nn: int) -> Tuple[float, ...]:
    if n != len(x) or n != len(y):
        raise ValueError("n должен совпадать с длиной списков x и y.")
    if nn <= 0:
        raise ValueError("nn должно быть положительным.")

    matrix = []
    i = 0
    while i < nn:
        row = []
        j = 0
        while j < nn:
            row.append(0.0)
            j += 1
        matrix.append(row)
        i += 1

    i = 0
    while i < nn:
        j = 0
        while j < nn:
            if i == 0 and j == 0:
                matrix[i][j] = n
            else:
                matrix[i][j] = sxn(x, i + j)
            j += 1
        i += 1

    rhs = []
    i = 0
    while i < nn:
        row_vals = []
        j = 0
        while j < n:
            row_vals.append(y[j] * (x[j] ** i))
            j += 1
        rhs.append(sx(row_vals))
        i += 1

    det_main = det(matrix)
    if abs(det_main) < _EPS:
        raise ValueError("Невозможно построить полиномиальную аппроксимацию: вырожденная система.")

    matrices_replaced = []
    j = 0
    while j < nn:
        matrix_copy = []
        i = 0
        while i < nn:
            matrix_copy.append(matrix[i][:])
            i += 1

        i = 0
        while i < nn:
            matrix_copy[i][j] = rhs[i]
            i += 1

        matrices_replaced.append(matrix_copy)
        j += 1

    coeffs = []
    i = 0
    while i < nn:
        coeffs.append(det(matrices_replaced[i]) / det_main)
        i += 1

    return tuple(coeffs)


def exponential_approx(x, y, n):
    if n != len(x) or n != len(y):
        raise ValueError("n должен совпадать с длиной списков x и y.")
    if any(v <= 0 for v in y):
        raise ValueError("Для экспоненциальной аппроксимации все y должны быть > 0.")
    yn = [math.log(y[i]) for i in range(n)]
    a, b = linear_approx(x, yn, n)
    return (math.exp(a), b)


def logarithmic_approx(x, y, n):
    if n != len(x) or n != len(y):
        raise ValueError("n должен совпадать с длиной списков x и y.")
    if any(v <= 0 for v in x):
        raise ValueError("Для логарифмической аппроксимации все x должны быть > 0.")
    xn = [math.log(x[i]) for i in range(n)]
    a, b = linear_approx(xn, y, n)
    return (b, a)


def power_approx(x, y, n):
    if n != len(x) or n != len(y):
        raise ValueError("n должен совпадать с длиной списков x и y.")
    if any(v <= 0 for v in x):
        raise ValueError("Для степенной аппроксимации все x должны быть > 0.")
    if any(v <= 0 for v in y):
        raise ValueError("Для степенной аппроксимации все y должны быть > 0.")
    yn = [math.log(y[i]) for i in range(n)]
    xn = [math.log(x[i]) for i in range(n)]
    a, b = linear_approx(xn, yn, n)
    return (math.exp(a), b)


def residuals(y: List[float], y_hat: List[float]) -> List[float]:
    if len(y) != len(y_hat):
        raise ValueError("Списки y и y_hat должны быть одинаковой длины.")
    return [y_hat[i] - y[i] for i in range(len(y))]


def sse(y: List[float], y_hat: List[float]) -> float:
    if len(y) != len(y_hat):
        raise ValueError("Списки y и y_hat должны быть одинаковой длины.")
    return sum((y_hat[i] - y[i]) ** 2 for i in range(len(y)))


def rmse(y: List[float], y_hat: List[float]) -> float:
    if not y:
        return float("nan")
    value = sse(y, y_hat) / len(y)
    return math.sqrt(max(value, 0.0))


def pearson_r(x: List[float], y: List[float]) -> float:
    if len(x) != len(y):
        raise ValueError("Списки x и y должны быть одинаковой длины.")
    n = len(x)
    if n < 2:
        raise ValueError("Для коэффициента Пирсона нужно минимум 2 точки.")
    sxv = sx(x)
    syv = sx(y)
    sxxv = sxx(x)
    syyv = sxx(y)
    sxyv = sxy(x, y)

    term_x = n * sxxv - sxv * sxv
    term_y = n * syyv - syv * syv

    if term_x < -_EPS or term_y < -_EPS:
        raise ValueError("Невозможно вычислить коэффициент Пирсона: подкоренное выражение отрицательно.")

    term_x = max(term_x, 0.0)
    term_y = max(term_y, 0.0)
    denom_sq = term_x * term_y

    if denom_sq <= _EPS:
        raise ValueError("Невозможно вычислить коэффициент Пирсона: нулевая дисперсия.")

    return (n * sxyv - sxv * syv) / math.sqrt(denom_sq)


def r2_score(y: List[float], y_hat: List[float]) -> float:
    if len(y) != len(y_hat):
        raise ValueError("Списки y и y_hat должны быть одинаковой длины.")
    y_mean = sum(y) / len(y)
    ss_res = sse(y, y_hat)
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    if abs(ss_tot) < _EPS:
        raise ValueError("Невозможно вычислить R^2: нулевая общая дисперсия.")
    return 1.0 - ss_res / ss_tot


def r2_message(r2: float) -> str:
    if r2 < 0:
        return "R^2 < 0: модель хуже среднего значения данных."
    if r2 < 0.5:
        return "0 <= R^2 < 0.5: слабое качество приближения."
    if r2 < 0.75:
        return "0.5 <= R^2 < 0.75: удовлетворительное качество приближения."
    if r2 < 0.9:
        return "0.75 <= R^2 < 0.9: хорошее качество приближения."
    return "R^2 >= 0.9: очень хорошее качество приближения."


def f_linear(x: float, c: Tuple[float, float]) -> float:
    a0, a1 = c
    return a0 + a1 * x


def f_poly2(x: float, c: Tuple[float, float, float]) -> float:
    a0, a1, a2 = c
    return a0 + a1 * x + a2 * x * x


def f_poly3(x: float, c: Tuple[float, float, float, float]) -> float:
    a0, a1, a2, a3 = c
    return a0 + a1 * x + a2 * x * x + a3 * x * x * x


def f_exp(x: float, c: Tuple[float, float]) -> float:
    a, b = c
    return a * math.exp(b * x)


def f_log(x: float, c: Tuple[float, float]) -> float:
    a, b = c
    return a + b * math.log(x)


def f_power(x: float, c: Tuple[float, float]) -> float:
    a, b = c
    return a * (x ** b)
