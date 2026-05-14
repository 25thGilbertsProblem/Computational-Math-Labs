from math import isfinite


def rect(f, a, b, n, d):
    h = (b - a) / n
    x = []
    i = a + d * h
    j = 0
    while j < n:
        x.append(i)
        i += h
        j += 1

    ans = 0.0
    for i in range(len(x)):
        ans += f(x[i]) * h
    return ans


def trapez(f, a, b, n, d=0):
    h = (b - a) / n
    x = [a + i * h for i in range(n + 1)]

    ans = f(x[0]) + f(x[n])
    for i in range(1, n):
        ans += 2 * f(x[i])
    ans *= h / 2
    return ans


def simpson(f, a, b, n, d=0):
    if n % 2 != 0:
        n += 1

    h = (b - a) / n
    x = [a + i * h for i in range(n + 1)]

    ans = f(x[0]) + f(x[n])
    for i in range(1, n):
        if i % 2 == 0:
            ans += 2 * f(x[i])
        else:
            ans += 4 * f(x[i])
    ans *= h / 3
    return ans


METHODS = {
    1: ("Метод левых прямоугольников", rect, 1, 0),
    2: ("Метод правых прямоугольников", rect, 1, 1),
    3: ("Метод средних прямоугольников", rect, 2, 0.5),
    4: ("Метод трапеций", trapez, 2, 0),
    5: ("Метод Симпсона", simpson, 4, 0),
}


def integrate_runge(f, a, b, method_key, eps, n0=4, max_iter=30):
    method_name, method_func, p, k = METHODS[method_key]

    n = n0
    if method_key == 5 and n % 2 != 0:
        n += 1

    i_n = method_func(f, a, b, n, k)

    for _ in range(max_iter):
        n2 = 2 * n
        if method_key == 5 and n2 % 2 != 0:
            n2 += 1

        i_2n = method_func(f, a, b, n2, k)
        runge_error = abs(i_2n - i_n) / (2 ** p - 1)

        if runge_error <= eps:
            return i_2n, n2, runge_error

        n = n2
        i_n = i_2n

    raise RuntimeError("Не удалось достичь требуемой точности.")


def integrate_improper_once(spec, method_key, eps, delta):
    f = spec["func"]
    a = spec["a"]
    b = spec["b"]
    singularity = spec["singularity"]

    if singularity == "a":
        return integrate_runge(f, a + delta, b, method_key, eps)

    if singularity == "b":
        return integrate_runge(f, a, b - delta, method_key, eps)

    if singularity == "inside":
        c = spec["c"]
        left_value, left_n, left_err = integrate_runge(f, a, c - delta, method_key, eps / 2)
        right_value, right_n, right_err = integrate_runge(f, c + delta, b, method_key, eps / 2)
        return left_value + right_value, max(left_n, right_n), max(left_err, right_err)

    raise ValueError("Неизвестный тип особенности.")


def integrate_improper(spec, method_key, eps):
    deltas = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]

    prev_value = None
    prev_n = None
    prev_err = None

    for delta in deltas:
        try:
            value, n_used, err = integrate_improper_once(spec, method_key, eps, delta)
        except:
            continue

        if not isfinite(value):
            continue

        if prev_value is not None:
            if abs(value - prev_value) < max(eps * 10, 1e-6):
                return value, n_used, err

        prev_value = value
        prev_n = n_used
        prev_err = err

    return None, None, None