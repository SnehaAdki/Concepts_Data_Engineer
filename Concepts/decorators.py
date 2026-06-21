from functools import * 


def greet(func):
    def wrapper(name):
        print("Welcome.... ")
        func(name)
    return wrapper

@greet
def welcome(name):
    print(name)


print("Where welcoome is not returing anythinhg")
welcome("Sneha")


def greet_1(func):
    def wrapper(name):
        print(f"GM .... {func(name)}")
    return wrapper


@greet_1
def greeting(name):
    return name

print("Where greeting is  returing anythinhg")
greeting("Vijay")

def param(num):
    def inner(fun):
        @wraps(fun)
        def wrapper(param):
            if num%2 !=0:
                return f" From odd param {num} as {fun(param)}"
            else:
                return f" From even param {num} as {fun(param)}"

        return wrapper
    return inner


@param(1)
def odd(num):
    print(odd.__name__)
    return f"Odd {num}"

@param(2)
def even(num):
    return f"Even {num}"

print("--------- decorator param ---- ")
print(odd(13))
print(even(20))



