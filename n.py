import inspect

def ex_func(query, min_price=0, max_price=100000000):
    """funcao ex"""
    return "Resultado"

g = inspect.signature(ex_func)
d = inspect.getdoc(ex_func)

print(g, "\n", d)