# docs: start-0
import numpy as np

from qunits import u

q = 2 * u.e  # >>> 2.0 e
v = 2e5 * u.m / u.s  # >>> 200000.0 m/s
B = 0.42 * u.mT  # >>> 0.42 mT

F = q * v * B  # >>> 168000.0 e⋅m⋅mT/s
F = F.to_base_units()  # >>> 2.69165674512e-17 N
F = F.to(u.e * u.V / u.m)  # >>> 168.0 V⋅e/m

omega = 2 * u.pi * u.kHz  # >>> 2.0 kHz⋅pi
T = np.linspace(0, 0.2, 5) * u.ms  # >>> [0.   0.05 0.1  0.15 0.2 ] ms

Ft = F * np.sin(omega * T)  # >>> [  0.  51.91485505  ...  159.77749474] V⋅e/m
# docs: end

print(q)
print(v)
print(B)
print(F)
print(omega)
print(T)
print(Ft)
