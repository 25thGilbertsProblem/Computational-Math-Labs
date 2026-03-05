import random


def check_matrix_diagonal_dominance(matrix):
    for i, row in enumerate(matrix):
        diagonal = abs(row[i])
        other = sum(abs(v) for j, v in enumerate(row) if i != j)
        if diagonal < other:
            return False
    return True


def try_make_matrix_diagonal_dominance(matrix, vector):
    dim_n = len(matrix)
    tested = [None] * dim_n
    matrix_new, vector_new = [None] * dim_n, [None] * dim_n
    for i in range(dim_n):
        exist = False
        for j in range(dim_n):
            if not tested[j]:
                if abs(matrix[j][i]) > sum(abs(matrix[j][k]) for k in range(dim_n) if k != i):
                    tested[j] = True
                    matrix_new[i] = matrix[j]
                    vector_new[i] = vector[j]
                    exist = True
                    break
        if not exist:
            return None, None
    return matrix_new, vector_new


def matrix_norma(matrix):
    return max(sum(abs(v) for v in row) for row in matrix)


def generate_random_matrix(n: int, diagonal_dom: bool = True):
    matrix = [[random.uniform(-10, 10) for i in range(n)] for j in range(n)]
    vector = [random.uniform(-10, 10) for i in range(n)]

    if diagonal_dom:
        for i in range(n):
            s = sum(abs(matrix[i][j]) for j in range(n) if j != i)
            matrix[i][i] = s + random.uniform(1, 5)

    return matrix, vector
