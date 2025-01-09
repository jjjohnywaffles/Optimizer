import math

# Example script with various loops and list operations for testing optimization.

def numeric_loops():
    # Loop 1: Simple, single statement (vectorizable).
    arr = [1, 2, 3, 4, 5]
    c = 10
    for i in range(len(arr)):
        arr[i] += c  # This should be recognized for vectorization

    # Loop 2: Single statement, but uses multiplication (another vectorizable pattern).
    for i in range(len(arr)):
        arr[i] = arr[i] * 2  # Might be vectorizable if you handle multiplication

    # Loop 3: Multiple statements: partially vectorizable?
    # Contains a print statement, a step-by-step sum, and an assignment.
    sum_val = 0
    for i in range(len(arr)):
        print(f"Index: {i}, Value: {arr[i]}")
        arr[i] = arr[i] + 1
        sum_val += arr[i]  # Another statement referencing arr[i]

    # Attempt list operations after
    arr.append(999)  # If arr is converted to np.array, this might break
    return arr, sum_val


def nested_loops():
    # Loop 4: Nested loops that can be flattened using itertools.product.
    matrix = [[i * j for j in range(5)] for i in range(5)]
    result = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            result += matrix[i][j]

    # Loop 5: Another nested loop with multiple statements, partially flattenable?
    # Each inner iteration modifies 'matrix[i][j]' and logs it.
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] += i + j
            print(f"matrix[{i}][{j}] = {matrix[i][j]}")

    return matrix, result


def advanced_arithmetic():
    # Loop 6: More complex arithmetic in a single statement.
    # arr[i] = (arr[i] * 3) - 1
    arr = [2, 4, 6, 8]
    for i in range(len(arr)):
        arr[i] = (arr[i] * 3) - 1

    # Loop 7: Additional list ops after the loop
    arr.insert(2, 777)  # Could break if arr is turned into np.array
    return arr


def already_numpy_arrays():
    import numpy as np
    # Loop 8: If the array is already np.array, we might skip vectorizing or skip re-converting.
    arr_np = np.array([10, 20, 30])
    for i in range(len(arr_np)):
        arr_np[i] += 5  # Already a NumPy array, might want to skip 'arr_np = np.array(arr_np)'

    return arr_np


def multi_file_mix():
    # Loop 9: A multi-step numeric loop referencing different lists.
    # Potentially partial vectorization if we can isolate one assignment to A[i].
    A = [0, 1, 2, 3, 4]
    B = [2, 4, 6, 8, 10]
    for i in range(len(A)):
        A[i] = A[i] + B[i]
        B[i] = B[i] - 1
        print(f"A[i] = {A[i]}, B[i] = {B[i]}")

    return A, B


def main():
    print("Testing numeric_loops:")
    arr_result, sum_val = numeric_loops()
    print("Result arr:", arr_result)
    print("Sum val:", sum_val, "\n")

    print("Testing nested_loops:")
    matrix_result, result_val = nested_loops()
    print("Result matrix:", matrix_result)
    print("Nested loops sum:", result_val, "\n")

    print("Testing advanced_arithmetic:")
    arr_arith = advanced_arithmetic()
    print("Advanced arithmetic result:", arr_arith, "\n")

    print("Testing already_numpy_arrays:")
    arr_np = already_numpy_arrays()
    print("Already NumPy array result:", arr_np, "\n")

    print("Testing multi_file_mix:")
    A_res, B_res = multi_file_mix()
    print("Final A:", A_res)
    print("Final B:", B_res, "\n")


if __name__ == "__main__":
    main()
