# docs: custom-0
import numpy as np
import scipy.constants as sc

from qunits import Unit, u
from qunits.dimension import Dimensionless, Energy, Length
from qunits.prefix import Context

inch = Unit(0.0254, frozenset({("in", 1)}), Length, Context.I)
kcal = Unit(4184.0, frozenset({("kcal", 1)}), Energy, Context.I)

x = 10 * inch  # >>> 10.0 in
x = x.to(u.mm)  # >>> 254.0 mm
E = (2 * kcal).to(u.kJ)  # >>> 8.368 kJ
P = E / (1 * u.s)  # >>> 8.368 kJ/s
# docs: end

# docs: custom-1
luminance = (u.cd / u.m**2).d
name = luminance.name  # >>> LuminousIntensity__DIV__Area
nit = Unit(1.0, frozenset({("nit", 1)}), luminance, Context.I)

L = 300 * nit  # >>> 300.0 nit
L = L.to(u.cd / u.m**2)  # >>> 300.0 cd/m^2
# docs: end

# docs: custom-2
deg = Unit(sc.pi / 180, frozenset({("deg", 1)}), Dimensionless, Context.ANGLE)

phi = 90 * deg + 0.25 * u.pi  # >>> 135.0 deg
y = np.sin(phi)  # >>> 0.707106781186548 1

try:
    phi + 10 * u.percent
except ValueError as error:
    print(error)  # >>> Context mismatch in addition. Cannot add Dimensionless with context ANGLE and ...
# docs: end

# docs: custom-3
same = Unit(0.0254, frozenset({("in", 1)}), Length, Context.I)
print(same is inch)  # >>> True

try:
    Unit(0.025, frozenset({("in", 1)}), Length, Context.I)
except ValueError as error:
    print(error)  # >>> The unit in is already defined with scale 0.0254, dimension Length and context I.
# docs: end

print(x)
print(E)
print(P)
print(name)
print(L)
print(phi)
print(y)
