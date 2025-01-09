import math


def numeric_loops():
    arr = [1, 2, 3, 4, 5]
    c = 10
    for i in range(len(arr)):
        arr[i] += c
    arr = np.array(arr) + arr[i] * 2
    sum_val = 0
    for i in range(len(arr)):
        print(f'Index: {i}, Value: {arr[i]}')
        arr[i] = arr[i] + 1
        sum_val += arr[i]
    arr.append(999)
    return arr, sum_val


def numeric_loops():
    arr = [1, 2, 3, 4, 5]
    c = 10
    for i in range(len(arr)):
        arr[i] += c
    arr = np.array(arr) + arr[i] * 2
    sum_val = 0
    for i in range(len(arr)):
        print(f'Index: {i}, Value: {arr[i]}')
        arr[i] = arr[i] + 1
        sum_val += arr[i]
    arr.append(999)
    return arr, sum_val


def nested_loops():
    matrix = [[(i * j) for j in range(5)] for i in range(5)]
    result = 0
    for i, j in itertools.product(range(len(matrix)), range(len(matrix[i]))):
        result += matrix[i][j]
    for i, j in itertools.product(range(len(matrix)), range(len(matrix[i]))):
        matrix[i][j] += i + j
        print(f'matrix[{i}][{j}] = {matrix[i][j]}')
    return matrix, result


def nested_loops():
    matrix = [[(i * j) for j in range(5)] for i in range(5)]
    result = 0
    for i, j in itertools.product(range(len(matrix)), range(len(matrix[i]))):
        result += matrix[i][j]
    for i, j in itertools.product(range(len(matrix)), range(len(matrix[i]))):
        matrix[i][j] += i + j
        print(f'matrix[{i}][{j}] = {matrix[i][j]}')
    return matrix, result


def advanced_arithmetic():
    arr = [2, 4, 6, 8]
    arr = np.array(arr) + (arr[i] * 3 - 1)
    arr.insert(2, 777)
    return arr


def already_numpy_arrays():
    import numpy as np
    arr_np = np.array([10, 20, 30])
    for i in range(len(arr_np)):
        arr_np[i] += 5
    return arr_np


def multi_file_mix():
    A = [0, 1, 2, 3, 4]
    B = [2, 4, 6, 8, 10]
    for i in range(len(A)):
        A[i] = A[i] + B[i]
        B[i] = B[i] - 1
        print(f'A[i] = {A[i]}, B[i] = {B[i]}')
    return A, B


def main():
    print('Testing numeric_loops:')
    arr_result, sum_val = numeric_loops()
    print('Result arr:', arr_result)
    print('Sum val:', sum_val, '\n')
    print('Testing nested_loops:')
    matrix_result, result_val = nested_loops()
    print('Result matrix:', matrix_result)
    print('Nested loops sum:', result_val, '\n')
    print('Testing advanced_arithmetic:')
    arr_arith = advanced_arithmetic()
    print('Advanced arithmetic result:', arr_arith, '\n')
    print('Testing already_numpy_arrays:')
    arr_np = already_numpy_arrays()
    print('Already NumPy array result:', arr_np, '\n')
    print('Testing multi_file_mix:')
    A_res, B_res = multi_file_mix()
    print('Final A:', A_res)
    print('Final B:', B_res, '\n')


if __name__ == '__main__':
    main()
