from pint import UnitRegistry

from qunits import u

p = UnitRegistry()

p.m
p.mT
p.A


print(p.m / p.mT)
print(u.m / u.mT)
print(type(p.m / p.mT))
print(type(u.m / u.mT))
print()
print(p.m / p.mT / p.A)
print(u.m / u.mT / u.A)
