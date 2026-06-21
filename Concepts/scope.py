
def scopes(x):
    # local scope 
    print("local_scope ")
    print(id(x)) #...488
    print(x) # 10
    x =30
    print(id(x)) # changes add
    print(x) # 30

    #global scope
    print("Global Scope .... ")
    global y
    print(id(y)) #... 1368
    y = 300 #updated
    print(id(y))  # ...47784
    print(y) # 300


x = 10
y = 100
print(id(y)) #... 1368
print(y) # 100
print(id(x)) #...488
print(x) #10
scopes(x) 
print(id(x))  #...488
print(x) #10
print(id(y)) #...47784
print(y) # 300