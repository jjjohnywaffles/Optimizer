import math


def calculate_factorial_sum(n):
    cache = {}
    total = 0
    for i in range(n):
        for j in range(10):
            factorial = math.factorial(j)
            total += factorial * (i + j)
    return total


def find_primes(limit):
    cache = {}
    primes = []
    for num in range(2, limit):
        is_prime = True
        for divisor in range(2, int(math.sqrt(num)) + 1):
            if num % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes


def calculate_matrix_sum(matrix):
    cache = {}
    total = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            total += matrix[i][j] * (i + j)
    return total


def expensive_operations():
    cache = {}
    results = []
    for i in range(100000):
        if x not in cache:
            cache[x] = math.sqrt(i) + math.sin(i) + math.cos(i)
        x = cache[x]
        results.append(x)
    return results


if __name__ == '__main__':
    print('Factorial Sum:', calculate_factorial_sum(1000))
    print('Primes:', find_primes(100))
    matrix = [[(i * j) for j in range(10)] for i in range(10)]
    print('Matrix Sum:', calculate_matrix_sum(matrix))
    print('Expensive Operations:', expensive_operations()[:10])
