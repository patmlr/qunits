import numpy as np
from pint import UnitRegistry

from qunits import u
from qunits.dimension import Length, Time

p = UnitRegistry()

p.m
p.mT
p.A
p.rad


print(p.m / p.mT)
print(u.m / u.mT)
print(type(p.m / p.mT))
print(type(u.m / u.mT))
print()
print(p.m / p.mT / p.A)
print(u.m / u.mT / u.A)

omega = 2 * u.pi * u.Hz
print(omega, omega.unit.context)
rad = omega * u.s
print(rad, rad.unit.context)
print("sin", np.sin(rad))
print(2 * p.pi * p.Hz)
print(50 * u.percent * u.rad)
print(1 * u.rad + 3 * u.rad)
