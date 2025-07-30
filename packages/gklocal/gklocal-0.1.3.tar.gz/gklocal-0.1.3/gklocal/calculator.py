def add(a,b):
    """this will return addition of two number """
    return a+b

def subtract(a,b):
    """this will return difference of two number """
    return a-b


def multiply(a,b):
    """this will return product of two number """
    return a*b


def divide(a,b):
    """this will return diision of two number """
    if b == 0 :
        raise ValueError("cant divide by zero")
    return a/b

def power(a,b):
    """this will return power of two number """
    return a**b
