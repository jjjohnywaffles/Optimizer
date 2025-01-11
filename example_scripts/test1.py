def basic_loop():
    arr = [1, 2, 3, 4, 5]
    c = 10
    for i in range(len(arr)):
        arr[i] += c
    print(arr)

def nested_loop():
    matrix = [[i * j for j in range(5)] for i in range(5)]
    result = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            result += matrix[i][j]
    print(result)

if __name__ == "__main__":
    basic_loop()
    nested_loop()
