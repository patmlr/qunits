import numpy as np

from qunits import si

a = si.m * np.array([1.0])
print(type(a), a.unit.d, a)
b = si.mm * 2.0
print(type(b), b.unit.d, b)
c = b + a
print(type(c), c.unit.d, c)
d = 3 * si.m / si.us
print(type(d), d.unit.d, d)
e = 4 / si.ms
print(type(e), e.unit.d, e)
f = d * e
print(type(f), f.unit.d, f)
