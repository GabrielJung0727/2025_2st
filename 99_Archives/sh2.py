if __name__ == "__main__":
    x = int(input())
    y = float(input())

    print("%d 와 %f의 합은 %f" % (x, y, x + y))
    print("%d 와 %f의 합은 %f" % (x, y, x + y))
    print("x의 자료형은 %s, y의 자료형은 %s" % (type(x), type(y)))

    xf = float(x)
    yi = int(y)
    print("x의 자료형은 %s, y의 자료형은 %s" % (type(xf), type(yi)))

    print("%f 와 %d의 곱은 %f" % (y, x, x * y))
