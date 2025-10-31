import cmath

def equation2(inputs):
    #ddd
    inputs = inputs.replace(" ", '')
    sorty = []
    temp = 0
    for i in range(len(inputs)):
        if inputs[i] == "-" or inputs[i] == "+" or inputs[i] == "*" or inputs[i] == "/":
            sorty.append(inputs[temp:i])
            temp = i
        if i + 1 == len(inputs):
            sorty.append(inputs[temp:i + 1])
            temp = i
    a = 0
    b = 0
    c = 0
    print(sorty)
    for element in sorty:
        if 'x^2' in element:
            if element == 'x^2':
                a = 1
            elif element == '-x^2':
                a = -1
            elif element[0] == '-' or element[0] == '+' or element[0] in "1234567890":
                a = int(element.strip()[:-3])
            else:
                a = int(element.strip()[1:-3])
        elif 'x' in element:
            if element == 'x':
                b = 1
            elif element == '-x':
                b = -1
            elif element[0] == '-' or element[0] == '+' or element[0] in "1234567890":
                b = int(element.strip()[:-1])
            else:
                b = int(element.strip()[1:-1])
        elif element == '':
            pass
        else:
            if element[0] == '-' or element[0] == '+' or element[0] in "1234567890":
                c = int(element.strip())
            else:
                c = int(element.strip()[1:])
    D = b**2 - (4 * a * c)
    x1 = (-b - cmath.sqrt(D)) / (2 * a)
    x2 = (-b + cmath.sqrt(D)) / (2 * a)
    return (x1, x2)



def equation4(inputs):
    """Как найти корни биквадратного уровнения?
    Найдите Дискриминант и идите на#уй"""