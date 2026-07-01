def StrToFloat(s: str):
    if not s:
        raise ValueError("Empty string")

    k = 1
    value = 0.0
    frac = 0.0
    divisor = 1
    saw_dot = False
    
    idx = 0
    if s[0] == '-':
        k = -1
        idx = 1
    elif s[0] == '+':
        idx = 1

    for ch in s[idx:]:
        if ch == '.':
            if saw_dot:
                raise ValueError("Multiple dots")
            saw_dot = True
        elif '0' <= ch <= '9':
            digit = ord(ch) - ord('0')
            if not saw_dot:
                value = value * 10 + digit
            else:
                divisor *= 10
                frac += digit / divisor
        else:
            raise ValueError("Invalid character in float")

    return k * (value + frac)


if __name__ == "__main__":
    s = input()
    try:
        print(f"{StrToFloat(s) * 2:.3f}")
    except:
        print("Error")