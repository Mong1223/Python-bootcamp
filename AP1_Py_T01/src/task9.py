def proizv(a, n, x):
    return a * n * x**(n - 1)

if __name__ == "__main__":
    n, x = input().split()
    n = int(n)
    x = float(x)

    result = 0
    degree = n

    for _ in range(n + 1):
        a = float(input())
        if degree > 0: 
            result += proizv(a, degree, x)
        degree -= 1

    print(f"{result:.3f}")
