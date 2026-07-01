def find_min_cost_for_year(devices, t):
    best = None
    n = len(devices)

    # Перебираем любые две разные записи
    for i in range(n):
        t1, p1 = devices[i]
        for j in range(i + 1, n):
            t2, p2 = devices[j]

            if t1 + t2 == t:
                total = p1 + p2
                if best is None or total < best:
                    best = total

    return best


if __name__ == "__main__":
    try:
        first = input().split()
        if len(first) != 2:
            raise ValueError

        n, t = map(int, first)
        if n <= 0 or t <= 0:
            raise ValueError

        data = {}  

        for _ in range(n):
            row = input().split()
            if len(row) != 3:
                raise ValueError

            year, price, battery = map(int, row)
            if year <= 0 or price <= 0 or battery <= 0:
                raise ValueError

            if year not in data:
                data[year] = []
            data[year].append((battery, price))

        best_global = None

        # Перебор по годам
        for year, devices in data.items():
            res = find_min_cost_for_year(devices, t)
            if res is not None:
                if best_global is None or res < best_global:
                    best_global = res

        if best_global is None:
            raise ValueError  # пара не найдена, но по условию она есть

        print(best_global)

    except Exception:
        print("Error")
