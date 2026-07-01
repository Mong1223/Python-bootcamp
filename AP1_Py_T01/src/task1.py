def scal_multyply(vector1,vector2):
    result = sum(a*b for a,b in zip(vector1,vector2))
    return result


if __name__ == "__main__":
    v1 = list(map(float,input().split()))
    v2 = list(map(float,input().split()))
    print(scal_multyply(v1,v2))