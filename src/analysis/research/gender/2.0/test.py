import pandas as pd

a = [{'a':1}, {'a':2, 'b':0}]
b = map(lambda x:x['a'], a)
print(set(b))
print(pd.DataFrame(a))