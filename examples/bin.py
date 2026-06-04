import numpy as np
from pint import UnitRegistry

from qunits import u

p = UnitRegistry()


print(p.m / p.mT)
print(u.m / u.mT)
print(type(p.m / p.mT))
print(type(u.m / u.mT))
print()
print(p.m / p.mT / p.A)
print(u.m / u.mT / u.A)

omega = 2 * p.pi * p.MHz
print(omega)
rad = omega * p.s
print(rad)
print(rad.to_base_units())  # type: ignore

omega = 2 * u.pi * u.MHz
print(omega, omega.unit.context)
rad = omega * u.s
print(rad, rad.unit.context)
print(rad.to_base_units())

print("sin", np.sin(rad))
print(2 * p.pi * p.Hz)
print(50 * u.percent * u.rad)
print(1 * u.rad + 3 * u.rad)
print((5 * u.mm).to(u.um))
a = 3 * u.mm
a += 3 * u.m
print(a)
