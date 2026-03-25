import numpy as np

from qunits import si

a = si.m * np.array([1.0])
print(type(a), a.unit.d, a)
b = si.mm * 2.0
print(type(b), b.unit.d, b)
c = a + b
print(type(c), c.unit.d, c)
