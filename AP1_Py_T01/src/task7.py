def best_way(n, m, matrix):
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = matrix[0][0]

    for i in range(n):
        for j in range(m):
            if i > 0:
                dp[i][j] = max(dp[i][j], dp[i-1][j] + matrix[i][j])
            if j > 0:
                dp[i][j] = max(dp[i][j], dp[i][j-1] + matrix[i][j])

    return(dp[n-1][m-1])


if __name__ == "__main__":
    n, m = map(int, input().split())
    matrix = [list(map(int, input().split())) for _ in range(n)]
    print(best_way(n, m, matrix))
