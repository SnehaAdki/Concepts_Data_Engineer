def accept_args(*a):
    print(*a)
    for i in a:
        print(i)

def key_args(**kargs):
    print(kargs)
    # for i in kargs:
    #     print(i)


accept_args(10,20,30,40)
accept_args(2,3,4)
accept_args(2,'abc',4)
# accept_args(a=1 , b=20) # accept_args() got an unexpected keyword argument 'a'
key_args(a=1 , b=20)


