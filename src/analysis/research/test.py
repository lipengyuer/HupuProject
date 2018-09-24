
def getC(n):
    if n>1:
        print(n)
        return n*getC(n-1)
    else:
        return 1

if __name__ == '__main__':
    s = [1, 2, 3, 4, 5, 6]
    res = []
    res = getC(s, res, l)
    print(res)