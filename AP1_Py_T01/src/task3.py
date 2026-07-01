def read_matrix():
    with open("input3.txt") as f:
        return [list(map(int, line.split())) for line in f]

def find_figures(matrix):

    n = len(matrix)
    visited = [[False]*n for _ in range(n)]

    squares = 0
    circles = 0

    for i in range(n):
        for j in range(n):
            if matrix[i][j] == 1 and not visited[i][j]:
                
                queue = [(i, j)]
                visited[i][j] = True
                cells = []

                while queue:
                    x, y = queue.pop(0)
                    cells.append((x, y))

                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < n and 0 <= ny < n:
                            if matrix[nx][ny] == 1 and not visited[nx][ny]:
                                visited[nx][ny] = True
                                queue.append((nx, ny))

                # 1 клетка — не фигура
                if len(cells) <= 1:
                    continue

                # --- Определяем квадрат / круг ---
                xs = [x for x, y in cells]
                ys = [y for x, y in cells]

                h = max(xs) - min(xs) + 1
                w = max(ys) - min(ys) + 1

                if h == w and len(cells) == h * w:
                    squares += 1
                else:
                    circles += 1
    return(squares, circles)

if __name__ == "__main__":
    matrix = read_matrix()
    print(*find_figures(matrix))
