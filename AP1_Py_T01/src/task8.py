if __name__ == "__main__":
    vals = set()
    n = int(input())
    for i in range(n):
        value = int(input())
        vals.add(value)
    print(len(vals))