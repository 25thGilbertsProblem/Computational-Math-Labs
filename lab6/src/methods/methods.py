import math
def is_close(a, b, rel_tol=1e-9, abs_tol=1e-9):
    close_check = abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    return close_check


def is_finite_number(value):
    return not (math.isnan(value) or math.isinf(value))

def build_grid(x0, xn, h):
    if h <= 0:
        raise ValueError("Шаг h должен быть положительным")
    if xn <= x0:
        raise ValueError("Должно выполняться xn > x0")

    n_float = (xn - x0) / h
    n = int(round(n_float))
    if n < 1:
        raise ValueError("На интервале должен быть хотя бы один шаг")
    if not is_close(x0 + n * h, xn):
        raise ValueError("Шаг h должен делить отрезок [x0, xn] без остатка")

    xs = []
    i = 0
    while i <= n:
        xs.append(x0 + i * h)
        i += 1

    return xs



def euler_method(f, x0, y0, xn, h):
    xs = build_grid(x0, xn, h)
    ys = []
    ys.append(y0)

    i = 0
    while i < len(xs) - 1:
        x_i = xs[i]
        y_i = ys[i]
        y_next = y_i + h * f(x_i, y_i)
        ys.append(y_next)
        i += 1

    return xs, ys


def improved_euler_method(f, x0, y0, xn, h):
    xs = build_grid(x0, xn, h)
    ys = []
    ys.append(y0)

    i = 0
    while i < len(xs) - 1:
        x_i = xs[i]
        y_i = ys[i]

        f_i = f(x_i, y_i)
        y_predict = y_i + h * f_i
        f_predict = f(x_i + h, y_predict)
        y_next = y_i + (h / 2.0) * (f_i + f_predict)

        ys.append(y_next)
        i += 1

    return xs, ys


def rk4_step(f, x, y, h):
    k1 = h * f(x, y)
    k2 = h * f(x + h / 2.0, y + k1 / 2.0)
    k3 = h * f(x + h / 2.0, y + k2 / 2.0)
    k4 = h * f(x + h, y + k3)
    res = y + (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
    return res


def adams_method(f, x0, y0, xn, h):
    xs = build_grid(x0, xn, h)
    n = len(xs) - 1
    if n < 3:
        raise ValueError("Для метода Адамса нужно минимум 4 узла на сетке")

    ys = []
    ys.append(y0)

    i = 0
    while i < 3:
        y_next = rk4_step(f, xs[i], ys[i], h)
        ys.append(y_next)
        i += 1

    fvals = []
    i = 0
    while i < 4:
        fvals.append(f(xs[i], ys[i]))
        i += 1

    i = 3
    while i < n:
        x_next = xs[i + 1]

        y_pred = ys[i] + (h / 24.0) * (
            55.0 * fvals[3] - 59.0 * fvals[2] + 37.0 * fvals[1] - 9.0 * fvals[0]
        )


        f_pred = f(x_next, y_pred)
        y_corr = ys[i] + (h / 24.0) * (
            9.0 * f_pred + 19.0 * fvals[3] - 5.0 * fvals[2] + fvals[1]
        )

        ys.append(y_corr)

        fvals_new = []
        fvals_new.append(fvals[1])
        fvals_new.append(fvals[2])
        fvals_new.append(fvals[3])
        fvals_new.append(f(x_next, y_corr))
        fvals = fvals_new

        i += 1

    return xs, ys

def runge_estimate(method, f, x0, y0, xn, h, p):
    xs_h, ys_h = method(f, x0, y0, xn, h)
    xs_h2, ys_h2 = method(f, x0, y0, xn, h / 2.0)

    ys_h2_even = []
    i = 0
    while i < len(ys_h2):
        if i % 2 == 0:
            ys_h2_even.append(ys_h2[i])
        i += 1

    if len(ys_h) != len(ys_h2_even):
        raise RuntimeError("Несовместимые размеры сеток для правила Рунге")

    r = abs(ys_h[-1] - ys_h2_even[-1]) / (2 ** p - 1)
    return r


def max_abs_error(xs, ys, exact):
    if exact is None:
        return None

    max_err = 0.0
    i = 0
    while i < len(xs):
        err = abs(exact(xs[i]) - ys[i])
        if err > max_err:
            max_err = err
        i += 1

    return max_err