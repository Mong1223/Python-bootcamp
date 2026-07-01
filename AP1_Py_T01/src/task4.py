def PascalTriangle(n: int):
    triangle = []
    if n <= 0:
        print("Natural number was expected")
    else:
        for i in range(n):
            row = [1] * (i + 1)
            for j in range(1, i):
                row[j] = triangle[i - 1][j - 1] + triangle[i - 1][j]
            triangle.append(row)
            print(*row)

    return triangle


if __name__ == "__main__":
    try:
        n = int(input())
        PascalTriangle(n)
    except ValueError:
        print("Natural number was expected")
