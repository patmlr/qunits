import numpy as np

from qunits import u

a = u.m * np.array([1.0])
print(a.unit.d, a)

b = u.mm * 2.0
print(b.unit.d, b)

c = b + a
print(c.unit.d, c)

d = 3 * u.m / u.us
print(d.unit.d, d)

e = 4 / u.ms
print(e.unit.d, e)

f = d * e
print(f.unit.d, f)

g = 5 * u.e
print(g.unit.d, g)

h = g * 2 * u.mV
print(h.unit.d, h)

i = h.si()
print(i.unit.d, i)

j = 9 * u.kg * 2 * u.m / u.s**2
print(j.unit.d, j)

k = g.to(u.uC)
print(k.unit.d, k)
