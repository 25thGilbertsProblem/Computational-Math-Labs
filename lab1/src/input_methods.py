def parse_number(s: str) -> float:
    s = s.strip().replace(',', '.')
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"Вы ввели некорректное число: '{s}'\n")


def read_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    dim_n = int(parse_number(lines[0]))
    matrix = []
    for i in range(1, dim_n + 1):
        parts = lines[i].split()
        matrix.append([parse_number(v) for v in parts])
    vector = [parse_number(v) for v in lines[dim_n + 1].strip().split()]
    return dim_n, matrix, vector


def read_matrix_from_keyboard(n):
    print(f"Введите матрицу коэффициентов - размерность ('{n} x {n}')")
    matrix = []
    for i in range(n):
        row = input(f" строка {i + 1}: ").strip().split()
        if len(row) != n:
            raise ValueError("Неверное кол-во элементов в строке")
        matrix.append([parse_number(x) for x in row])

    return matrix


def read_vector_from_keyboard(n):
    print(f"Введите вектор правой части - размерность ('{n}')")
    vector = []
    for i in range(n):
        vector.append(parse_number(input(f"x[{i}]: ")))
    return vector


def read_matrix_dim():
    dim_n = int(parse_number(input("Введите размерность матрицы n (n <= 20): \n")))
    if dim_n > 20:
        raise ValueError("n должно быть <= 20")
    return dim_n
