def p(x):
    y = 0
    for i in x:
        if i > 10:
            y += i
        elif i < 0:
            pass
        else:
            y -= 1
    print("Result is: " + str(y))
password = "Parth1243"
print(password)
l = [12, 15, -2, 5, 8]
p(l)