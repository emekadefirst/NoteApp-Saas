from typing import Callable, Iterable

def add(*args):
    return sum(args)



def logic(func: Callable, data=None, *args):
    if data is not None and isinstance(data, (list, tuple, set)):
        return func(*data)
    return func(*args)

print(logic(add, [5, 3]))  
print(logic(add, None, 5, 3))  # Output: 8
