import math
import numpy as np
import sympy as sp
from scipy import integrate
from scipy.special import eval_jacobi, eval_legendre, eval_genlaguerre, eval_hermite
import matplotlib.pyplot as plt
import scipy.integrate as integrate

x = sp.symbols('x')  # общий символ x для sympy

class ChebyshevFirstKind:
    def evaluate(self, n, x_val):
        """Аналитическая формула"""
        return np.cos(n * np.arccos(x_val))

    def recurrent(self, n, x_val):
        """Рекуррентная формула"""
        if n == 0:
            return x_val
        else:
            T_n = self.evaluate(n, x_val) * 2 * x_val
            Т_n_minus_1 = self.evaluate(n - 1, x_val)
            return round(T_n - Т_n_minus_1, 2)

    def diff_eq(self, n):
        '''Подставляет многочлен Чебышева 1-го рода порядка n
        в уравнение (1-x²)y\'\' - xy\' + n²y = 0 '''
        y = sp.chebyshevt(n, x)

        # Вычисляем первую и вторую производные
        first_derivative = sp.diff(y, x)
        second_derivative = sp.diff(first_derivative, x)
        # Составляем уравнение
        result = (1 - x ** 2) * second_derivative - x * first_derivative + n ** 2 * y
        return result

    def generating_function(self, x_val, r, n):
        ''' Вычисляет выражение Σ r²Tₙ(x), 0 < r < 1 '''
        T_n = [self.evaluate(i, x_val) for i in range(n)]

        # Формируем выражение для r^n * T_n(x)
        Tn_expression = sum(r ** i * T_n[i] for i in range(n))

        return Tn_expression

    def roots(self, n):
        """Корни T_n"""
        return ', '.join([f'x{k}={float(round(np.cos((2 * k - 1) * np.pi / (2 * n)), 4))}' for k in range(1, n + 1)])

    def orthogonality_integral(self, m, n):
        """Интеграл ортогональности"""
        T_m = sp.chebyshevt(m, x)
        T_n = sp.chebyshevt(n, x)
        integrand = T_m * T_n / sp.sqrt(1 - x**2)
        return sp.integrate(integrand, (x, -1, 1))

    def plot(self, n, num_points=500):
        """Построение графика T_n"""
        x = np.linspace(-1, 1, num_points)
        y = np.cos(n * np.arccos(x))
        plt.plot(x, y, label=f"T_{n}(x)")
        plt.title(f"Полином Чебышёва первого рода T_{n}(x)")
        plt.xlabel("x")
        plt.ylabel(f"T_{n}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()

class ChebyshevSecondKind:
    """Свойства полиномов Чебышёва второго рода"""

    def evaluate(self, n, x_val):
        """Аналитическая формула"""
        return np.sin((n + 1) * np.arccos(x_val)) / np.sqrt(1 - x_val**2)


    def recurrent(self, n, x_val):
        """Рекуррентная формула"""
        if n == 0:
            return 1
        elif n == 1:
            return 2 * x_val
        else:
            U0, U1 = 1, 2 * x_val
            for _ in range(2, n + 1):
                U0, U1 = U1, 2 * x_val * U1 - U0
            return U1

    def estimate_bounds(self, x_val, n_max):
        """Оценка модулей"""
        bound1 = round(1 / math.sqrt(1 - x_val**2), 3)
        result = []
        for n in range(n_max):
            val = abs(self.evaluate(n, x_val))
            result.append((n, round(val, 4), bound1, n + 1))
        return result

    def roots(self, n):
        """Корни"""
        return np.cos(np.arange(1, n + 1) * np.pi / (n + 1))

    def orthogonality_integral(self, m, n):
        """Ортогональность"""
        U_m = sp.chebyshevu(m, x)
        U_n = sp.chebyshevu(n, x)
        integrand = U_m * U_n * sp.sqrt(1 - x**2)
        integral = sp.integrate(integrand, (x, -1, 1))
        return integral


class LegendrePolynomial:
    """Свойства многочленов Лежандра"""

    def rodrigues(self, n):
        """Формула Родрига (символьный вывод)"""
        return (1 / (2**n * sp.factorial(n))) * sp.diff((x**2 - 1)**n, x, n)

    def rodrigues_numeric(self, n, x_val):
        """Значение многочлена по формуле Родрига"""
        expr = self.rodrigues(n)
        return float(expr.subs(x, x_val))

    def recurrent(self, n, x_val):
        """Рекуррентная формула"""
        if n == 0:
            return 1
        elif n == 1:
            return x_val
        else:
            P0, P1 = 1, x_val
            for i in range(2, n + 1):
                P0, P1 = P1, ((2 * i - 1) * x_val * P1 - (i - 1) * P0) / i
            return P1

    def orthogonality_integral(self, m, n):
        """Интеграл ортогональности"""
        x = self.symbol
        P_m = sp.legendre(m, x)
        P_n = sp.legendre(n, x)
        return sp.integrate(P_m * P_n, (x, -1, 1))

    def generating_function(self, x_val, w, n_terms):
        """
        Сумма первых n_terms членов производящей функции:
        ∑ wⁿ Pₙ(x)
        """
        return sum(w**i * eval_legendre(i, x_val) for i in range(n_terms))

    def right_part_of_generating_function(self, x_val, w):
        return 1 / sp.sqrt(1 - 2 * x_val * w + w ** 2)

    def diff_eq(self, n):
        """Дифференциальное уравнение"""
        y = sp.legendre(n, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return (1 - x**2) * d2y - 2 * x * dy + n * (n + 1) * y

    def plot(self, n, num_points=500):
        """График P_n(x)"""
        x = np.linspace(-1, 1, num_points)
        y = eval_legendre(n, x)
        plt.plot(x, y, label=f"P_{n}(x)")
        plt.title(f"Многочлен Лежандра P_{n}(x)")
        plt.xlabel("x")
        plt.ylabel(f"P_{n}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()


class LaguerrePolynomial:
    """Свойства обобщённых полиномов Лагерра (Чебышёва-Лаггера)"""

    def evaluate(self, n, alpha, x_val):
        return eval_genlaguerre(n, alpha, x_val)

    def orthogonality_integral(self, m, n, alpha):
        """Ортогональность: ∫₀^∞ x^α e^{-x} Lₘ^α(x)·Lₙ^α(x) dx"""
        integrand = lambda x1: x1 ** alpha * np.exp(-x1) * eval_genlaguerre(m, alpha, x1) * eval_genlaguerre(n, alpha, x1)
        result, error = integrate.quad(integrand, 0, np.inf)
        return 0 if abs(result) < 0.001 else result

    def generating_function(self, x_val, t, alpha, n_terms=10):
        """
        Производящая функция как ряд:
        ∑ Lₙ^α(x) tⁿ
        """
        return sum([self.evaluate(n, alpha, x_val) * t**n for n in range(n_terms)])

    def recurrent(self, n, alpha, x_val):
        """
        Рекуррентное соотношение:
        Lₙ^α(x) = ((2n + 1 + α - x)Lₙ^α(x) - (n + α)Lₙ₋₁^α(x)) / (n + 1)
        """
        Ln = (2 * n + 1 + alpha - x_val) * eval_genlaguerre(n, alpha, x_val)
        Ln_minus_1 = eval_genlaguerre(n - 1, alpha, x_val) * (n + alpha)

        return (Ln - Ln_minus_1) / (n + 1)

    def dif_eq(self, alpha, n):
        """
        Дифференциальное уравнение:
        x·y\'\' + (1 + α - x)·y' + n·y = 0
        """
        y = sp.assoc_laguerre(n, alpha, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return x * d2y + (1 + alpha - x) * dy + n * y

    def plot(self, n, alpha=0, num_points=500):
        """График Lₙ^α(x)"""
        x_range = np.linspace(0, 20, num_points)
        y = self.evaluate(n, alpha, x_range)
        plt.plot(x_range, y, label=f"L_{n}^{alpha}(x)")
        plt.title(f"Многочлен Лагерра L_{n}^{alpha}(x)")
        plt.xlabel("x")
        plt.ylabel(f"L_{n}^{alpha}(x)")
        plt.grid(True)
        plt.legend()
        plt.show()

class JacobiPolynomial:
    """Свойства многочленов Якоби"""

    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    def evaluate(self, n, x_val):
        """Численное значение многочлена Якоби через scipy"""
        return eval_jacobi(n, self.alpha, self.beta, x_val)

    def rodriguez(self, n):
        alpha = self.alpha
        beta = self.beta
        coeff = (-1) ** n / (2 ** n * math.factorial(n))
        term1 = (1 - x) ** (-alpha) * (1 + x) ** (-beta)
        term2 = sp.diff((1 - x) ** (n + alpha) * (1 + x) ** (n + beta), x, n)
        return coeff * term1 * term2

    def orthogonality_integral(self, m, n):
        J_m = sp.jacobi(m, self.alpha, self.beta, x)
        J_n = sp.jacobi(n, self.alpha, self.beta, x)
        integrand = J_m * J_n * (1 - x)**self.alpha * (1 + x)**self.beta
        return sp.integrate(integrand, (x, -1, 1))

    def inn(self, n):
        a, b = self.alpha, self.beta
        numerator = 2 ** (a + b + 1)
        denominator = math.factorial(n) * (2 * n + a + b + 1)
        gamma1 = math.gamma(n + a + 1)
        gamma2 = math.gamma(n + b + 1)
        gamma3 = math.gamma(n + a + b + 1)
        return numerator / denominator * (gamma1 * gamma2) / gamma3

    def lambda_n(self, n):
        a, b = self.alpha, self.beta
        numerator = (n + 1) * (n + a + 1) * (n + b + 1) * (n + a + b + 1)
        denominator = (2*n + a + b + 1) * (2*n + a + b + 2)**2 * (2*n + a + b + 3)
        return 2 * math.sqrt(numerator / denominator)


    def alpha_n(self, n):
        a, b = self.alpha, self.beta
        numerator = b**2 - a**2
        denominator = (2 * n + a + b + 2) * (2 * n + a + b)
        return numerator / denominator

    def J_hat(self, n):
        a, b = self.alpha, self.beta
        numerator = math.factorial(n) * (2*n + a + b + 1) * math.gamma(n + a + b + 1)
        denominator = 2 ** (a + b + 1) * math.gamma(n + a + 1) * math.gamma(n + b + 1)
        return math.sqrt(numerator / denominator) * sp.jacobi(n, a, b, x)

    def J_hat_recursive(self, n):
        if n == 0:
            return self.J_hat(n) * (x - self.alpha_n(n)) / self.lambda_n(n)
        else:
            return ((x - self.alpha_n(n)) * self.J_hat(n) -
                    self.lambda_n(n - 1) * self.J_hat(n - 1)) / self.lambda_n(n)

    def generating_function(self, w, terms):
        return sum([w ** i * sp.jacobi(i, self.alpha, self.beta, x) for i in range(terms)])

    def differential_equation(self, n):
        y = sp.jacobi(n, self.alpha, self.beta, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        a, b = self.alpha, self.beta
        return (1 - x**2) * d2y + (b - a - (2 + a + b) * x) * dy + n * (n + a + b + 1) * y

    def plot(self, n_max=4):
        x_vals = np.linspace(-1, 1, 400)
        for n in range(n_max + 1):
            y_vals = [self.evaluate(n, x1) for x1 in x_vals]
            plt.plot(x_vals, y_vals, label=f"$P_{n}^{{({self.alpha},{self.beta})}}(x)$")
        plt.title("Многочлены Якоби")
        plt.xlabel("x")
        plt.ylabel("P_n(x)")
        plt.grid(True)
        plt.legend()
        plt.show()


class HermitePolynomial:
    """Свойства многочленов Эрмита"""

    def evaluate(self,n, x_val):
        if isinstance(x_val, (int, float, np.ndarray)):
            return eval_hermite(n, x_val)
        else:
            return sp.hermite(n, x_val)

    def recurrent(self, n):
        """Рекуррентная формула:
        H₀(x) = 1,
        H₁(x) = 2x,
        Hₙ(x) = 2x·Hₙ₋₁(x) - 2(n-1)·Hₙ₋₂(x)
        """
        if n == 0:
            return lambda x1: np.ones_like(x1)  # H_0(x) = 1
        elif n == 1:
            return lambda x1: 2 * x1  # H_1(x) = 2x

            # Рекуррентное соотношение:
            # H_n(x) = 2x * H_{n-1}(x) - 2(n-1) * H_{n-2}(x)

        def hermite_recursive(x_val):
            H0 = np.ones_like(x)
            H1 = 2 * x_val
            for i in range(2, n + 1):
                Hn = 2 * x_val * H1 - 2 * (i - 1) * H0
                H0, H1 = H1, Hn
            return H1

        return hermite_recursive

        return hermite_recursive

    def generating_function(self, x_val, t_val, n_terms=6):
        """Численное значение суммы производящей функции:
        G(x, t) = Σ Hₙ(x)tⁿ/n!
        """
        if np.abs(t_val) >= 1:
            raise ValueError("Параметр t должен удовлетворять условию |t| < 1.")

            # Вычисляем сумму ряда
        result = np.zeros_like(x_val, dtype=float)
        for n in range(n_terms + 1):
            Hn_x = eval_hermite(n, x_val)  # Вычисляем H_n(x)
            term = (Hn_x / math.factorial(n)) * (t_val ** n)
            result += term

        return result


    def orthogonality_integral(self, m, n):
        """Интеграл ортогональности:
        ∫ Hₘ(x)·Hₙ(x)·e^{-x²} dx = sqrt(pi)·2ⁿ·n!·δₘₙ
        """
        Hm = sp.hermite(m, x)
        Hn = sp.hermite(n, x)
        integrand = Hm * Hn * sp.exp(-x ** 2)
        integral = sp.integrate(integrand, (x, -sp.oo, sp.oo))
        return sp.simplify(integral)

    def differential_equation(self, n):
        """Дифференциальное уравнение Эрмита:
        y'' - 2x·y' + 2n·y = 0
        """
        y = self.evaluate(n, x)
        dy = sp.diff(y, x)
        d2y = sp.diff(dy, x)
        return d2y - 2 * x * dy + 2 * n * y

    def plot(self, n, x_range=(-3, 3), points=400):
        """Строит график многочлена Эрмита Hₙ(x)"""
        x_vals = np.linspace(x_range[0], x_range[1], points)
        Hn_expr = sp.hermite(n, x)
        Hn_func = sp.lambdify(x, Hn_expr, modules='numpy')

        y_vals = Hn_func(x_vals)

        plt.plot(x_vals, y_vals, label=f"H_{n}(x)")
        plt.title(f"Многочлен Эрмита H_{n}(x)")
        plt.xlabel("x")
        plt.ylabel("Hₙ(x)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
