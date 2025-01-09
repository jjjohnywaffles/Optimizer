import math

# Example script with complex loops and computations
def calculate_factorial_sum(n):
    # High-iteration loop with repeated computation
    total = 0
    for i in range(n):
        for j in range(10):  # Nested loop
            factorial = math.factorial(j)  # Repeated computation inside nested loop
            total += factorial * (i + j)
    return total

def find_primes(limit):
    # High-iteration loop with computation
    primes = []
    for num in range(2, limit):
        is_prime = True
        for divisor in range(2, int(math.sqrt(num)) + 1):  # Nested loop with math
            if num % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

def calculate_matrix_sum(matrix):
    # Complex nested loops to sum elements
    total = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            total += matrix[i][j] * (i + j)  # Repeated computation
    return total

def expensive_operations():
    # A loop with a high iteration count and repeated function calls
    results = []
    for i in range(100000):
        x = math.sqrt(i) + math.sin(i) + math.cos(i)  # Multiple repeated computations
        results.append(x)
    return results

if __name__ == "__main__":
    # Test calculate_factorial_sum
    print("Factorial Sum:", calculate_factorial_sum(1000))
    
    # Test find_primes
    print("Primes:", find_primes(100))
    
    # Test calculate_matrix_sum
    matrix = [[i * j for j in range(10)] for i in range(10)]
    print("Matrix Sum:", calculate_matrix_sum(matrix))
    
    # Test expensive_operations
    print("Expensive Operations:", expensive_operations()[:10])  # Only show the first 10 results
