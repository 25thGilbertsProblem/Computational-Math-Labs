import sys

import input_methods
import matrix_methods
import iteration_method


def main():
    print("Решение СЛАУ методом простых итераций:")
    print("Формат ввода:")
    print("f - из файла")
    print("k - ввод с клавиатуры")
    print("r - сгенерировать случайную произвольную матрицу")
    print("g - сгенерировать случайную диагонально доминирующую матрицу")
    in_value_input_type = input("Введите формат ввода: \n").lower()
    if in_value_input_type == 'f':
        path_to_file = input("Путь до файла: \n")
        dim_n, A, B = input_methods.read_from_file(path_to_file)
    elif in_value_input_type == 'k':
        dim_n = input_methods.read_matrix_dim()
        A = input_methods.read_matrix_from_keyboard(dim_n)
        B = input_methods.read_vector_from_keyboard(dim_n)
    elif in_value_input_type == 'r':
        dim_n = input_methods.read_matrix_dim()
        A, B = matrix_methods.generate_random_matrix(dim_n, False)
        print("Сгенерирована случайная произвольная матрица")
    elif in_value_input_type == 'g':
        dim_n = input_methods.read_matrix_dim()
        A, B = matrix_methods.generate_random_matrix(dim_n, True)
        print("Сгенерирована случайная диагонально доминирующая матрица")
    else:
        raise ValueError("Некорректный выбор ввода")

    print("Вы ввели матрицу: ")
    for row in A:
        print(*row)
    print(f"Вы ввели вектор: {B} ")
    if not matrix_methods.check_matrix_diagonal_dominance(A):
        print("Матрица не имеет диагонального преобладания. Попытаемся переставить строки: \n")
        A_new, B_new = matrix_methods.try_make_matrix_diagonal_dominance(A, B)
        if A_new is None:
            print("Невозможно получить диагональное преобладание для данной матрицы")
            sys.exit(1)
        A, B = A_new, B_new
        print("Преобразованная матрица:")
        for row in A:
            print(*row)
        print(f"Вектор B: {B} ")

    print(f"Норма исходной матрицы (max из сумм модулей элементов строк): '{matrix_methods.matrix_norma(A)}'")

    eps = input_methods.parse_number(input("Введите точность eps: \n"))
    try:
        iteration_solution = iteration_method.SimpleIterationsMethod(A, B, eps=eps)
        x, iters, errors = iteration_solution.solver()
    except ZeroDivisionError:
        print("\nОшибка: Произошло деление на ноль внутри алгоритма итераций")
        print("\nВ процессе вычислений возник недопустимый знаменатель.")
        sys.exit(1)
    except Exception as e:
        print(f"\nНепредвиденная ошибка при решении: {e}")
        sys.exit(1)
    print("\nРешение:")
    for i, xi in enumerate(x, start=1):
        print(f"x_{i} = {xi}")

    print(f"Кол-во итераций: {iters}\n")
    print("Вектор погрешностей (последних итераций): ")
    for err in errors[-2:]:
        print(err)
    main()


if __name__ == "__main__":
    main()
