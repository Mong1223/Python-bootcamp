def IsPalindrome(value):
    result = False
    if value>0:
        original = value
        reversed_value = 0
        while value>0:
            digit = value%10
            reversed_value = reversed_value*10+digit
            value //=10
        if original ==reversed_value:
            result = True
        else:
            result = False
    return result
        

if __name__ == "__main__":
    s = int(input())
    print(IsPalindrome(s))