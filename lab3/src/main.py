import func
import methods


def read_int(prompt, allowed=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ошибка: нужно ввести целое число.")
            continue

        if allowed is not None and value not in allowed:
            print(f"Ошибка: допустимые значения: {sorted(allowed)}")
            continue

        return value


def read_float(prompt, positive=False):
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("Ошибка: нужно ввести число.")
            continue

        if positive and value <= 0:
            print("Ошибка: число должно быть больше 0.")
            continue

        return value


def choose_regular_function():
    while True:
        print("\nВыберите функцию:")
        for num, (name, _, _) in func.REGULAR_FUNCTIONS.items():
            print(f"{num}. {name}")
        choice = read_int("Ваш выбор: ", allowed=func.REGULAR_FUNCTIONS.keys())
        if choice in func.REGULAR_FUNCTIONS:
            return choice, func.REGULAR_FUNCTIONS[choice]
        print("Ошибка: такой функции нет.")



def choose_improper_function():
    while True:
        print("\nВыберите несобственный интеграл:")
        for num, data in func.IMPROPER_FUNCTIONS.items():
            print(f"{num}. {data['name']}")
        choice = read_int("Ваш выбор: ", allowed=func.IMPROPER_FUNCTIONS.keys())
        if choice in func.IMPROPER_FUNCTIONS:
            return func.IMPROPER_FUNCTIONS[choice]
        print("Ошибка: такого варианта нет.")


def choose_method_or_all():
    while True:
        print("\nВыберите численный метод:")
        print("0. Все методы")
        for num, (name, _, _, _) in methods.METHODS.items():
            print(f"{num}. {name}")

        choice = read_int("Ваш выбор: ", allowed={0, 1, 2, 3, 4, 5})
        return choice


def print_regular_result(method_name, value, n_used, err, exact):
    abs_err = abs(value - exact)
    rel_err = abs_err / abs(exact) if exact != 0 else abs_err

    print(f"{method_name}:")
    print(f"  Приближённое значение: {value}")
    print(f"  Число разбиений n: {n_used}")
    print(f"  Оценка погрешности по Рунге: {err}")
    print(f"  Абсолютная ошибка: {abs_err}")
    print(f"  Относительная ошибка: {rel_err}")
    print()


def main():
    print("<Вычисление определённых интегралов численными методами>")
    print("1. Обычный интеграл")
    print("2. Несобственный интеграл 2 рода")
    mode = read_int("Выберите режим: ", allowed={1, 2})

    eps = read_float("\nВведите требуемую точность eps: ", positive=True)

    if mode == 1:
        print("\n<Режим 1 выбран: Подсчёт определенных интегралов>")
        func_key, data = choose_regular_function()
        func_name, f, _ = data

        method_key = choose_method_or_all()

        while True:
            a = read_float("Введите нижний предел a: ")
            b = read_float("Введите верхний предел b: ")
            if b < a:
                a, b = b, a
                print(f"Вы ввели верхний предел меньше нижнего, поменяли их местами: a = {a}, b = {b}")
            break

        try:
            exact = func.exact_integral_regular(func_key, a, b)

            print("\n--- Результат ---")
            print(f"Функция: {func_name}")
            print(f"Точное значение интеграла: {exact}\n")

            if method_key == 0:
                vals = []
                for mk, (method_name, _, _, _) in methods.METHODS.items():
                    try:
                        value, n_used, err = methods.integrate_runge(f, a, b, mk, eps, n0=4)
                        # print_regular_result(method_name, value, n_used, err, exact)

                        vals.append([n_used, method_name, value, err, exact])

                    except Exception as ex:
                        print(f"{method_name}: ошибка вычисления: {ex}\n")
                vals.sort()
                for el in vals:
                    print_regular_result(el[1], el[2], el[0], el[3], el[4])


            else:
                method_name, _, _, _ = methods.METHODS[method_key]
                value, n_used, err = methods.integrate_runge(f, a, b, method_key, eps, n0=4)
                print_regular_result(method_name, value, n_used, err, exact)

        except Exception as ex:
            print(f"Ошибка: {ex}")

    elif mode == 2:
        print("\n<Режим 2 выбран: Подсчёт несобственных интегралов>")
        spec = choose_improper_function()

        method_key = choose_method_or_all()
        if method_key == 0:
            print("Для несобственных интегралов нужно выбрать один метод, а не все сразу.")
            return

        try:
            value, n_used, err = methods.integrate_improper(spec, method_key, eps)

            if value is None:
                print("\nИнтеграл не существует")
                return

            print("\n--- Результат ---")
            print(f"Интеграл: {spec['name']}")
            print(f"Значение интеграла: {value}")
            print(f"Число разбиений n: {n_used}")
            print(f"Оценка погрешности по Рунге: {err}")
        except Exception as ex:
            print(f"Ошибка вычисления: {ex}")


if __name__ == '__main__':
    main()