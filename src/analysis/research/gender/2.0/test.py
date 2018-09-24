import pandas as pd

a = [{"aa": 1, "aaa": {'a':1}}]
b = map(lambda x:x['a'], a)
print(pd.DataFrame(a))
for line in a:
    line['aaa'].update({'aa': line['aa']})
print(a)
aa = {"a": 1}
aa.update({"b": 2})
print(aa)
del aa['qweqwe']