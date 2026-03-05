class SimpleIterationsMethod:
    def __init__(self, matrix, vector, eps=1e-6, max_iter=10000):
        self.matrix = matrix
        self.vector = vector
        self.eps = eps
        self.max_iter = max_iter
        self.dim_n = len(matrix)

    def solver(self):
        dim_n = self.dim_n
        x_old = [0.0]*dim_n
        x_new = [0.0]*dim_n
        iters = 0
        errors = []

        while iters < self.max_iter:
            for i in range(dim_n):
                sum_ = sum(self.matrix[i][j] * x_old[j] for j in range(dim_n) if j != i)
                x_new[i] = (self.vector[i] - sum_) / self.matrix[i][i]
            err_vec = [abs(x_new[i] - x_old[i]) for i in range(dim_n)]
            errors.append(err_vec)
            if max(err_vec) < self.eps:
                break

            x_old = x_new.copy()
            iters += 1

        if iters >= self.max_iter:
            raise RuntimeError(f"Достигнут лимит итераций ({self.max_iter}). Метод не сошёлся.")

        return x_new, iters, errors
