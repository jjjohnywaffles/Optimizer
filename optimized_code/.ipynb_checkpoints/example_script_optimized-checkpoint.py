import math


def calculate_factorial_sum(n):
    total = 0
    for i, j in itertools.product(range(n), range(10)):
        factorial = math.factorial(j)
        total += factorial * (i + j)
    return total


def calculate_factorial_sum(n):
    total = 0
    for i, j in itertools.product(range(n), range(10)):
        factorial = math.factorial(j)
        total += factorial * (i + j)
    return total


def find_primes(limit):
    primes = []
    for num, divisor in itertools.product(range(2, limit), range(2, int(
        math.sqrt(num)) + 1)):
        is_prime = True
        if num % divisor == 0:
            is_prime = False
            break
        if is_prime:
            primes.append(num)
    return primes


def calculate_matrix_sum(matrix):
    total = 0
    for i, j in itertools.product(range(len(matrix)), range(len(matrix[i]))):
        total += matrix[i][j] * (i + j)
    return total


def expensive_operations():
    results = []
    for i in range(100000):
        x = math.sqrt(i) + math.sin(i) + math.cos(i)
        results.append(x)
    return results


if __name__ == '__main__':
    print('Factorial Sum:', calculate_factorial_sum(1000))
    print('Primes:', find_primes(100))
    matrix = [[(i * j) for j in range(10)] for i in range(10)]
    print('Matrix Sum:', calculate_matrix_sum(matrix))
    print('Expensive Operations:', expensive_operations()[:10])
