

class IterativeMethod:
    @staticmethod
    def solve_by_newton_raphson(func, func_deriv, x_0, tol):

        find_next = lambda x: x - func(x) / func_deriv(x)

        x_next = x_0
        while math.fabs(func(x_next)) > tol:
            x_next = find_next(x_next)

        return x_next

if __name__ == '__main__':
    import math
    func = lambda x: math.pow(x, 2) - 2
    func_deriv = lambda x: 2 * x
    test = IterativeMethod.solve_by_newton_raphson(func, func_deriv, x_0=0.01, tol=0.0000001)
    truth = math.sqrt(2)
    print()