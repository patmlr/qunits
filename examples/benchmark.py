import time

import numpy as np
from pint import UnitRegistry, Quantity

from qunits import si, Quantity as Q

u = UnitRegistry()
u.m
u.mm
u.s

n_samples = 1000

t0 = time.time()
for _ in range(n_samples):
    a = si.m * np.array([1.0, 2.0, 3.0])
    b = 2.0 * si.mm
    c = a + b
    d = [Q(1.0, si.m), Q(2.0, si.m), Q(3.0, si.mm)]
    e = [b + q for q in d]

t1 = time.time()
print(f"qunits: {(t1 - t0) / n_samples:.4f} seconds")


t0 = time.time()
for _ in range(n_samples):
    a = u.m * np.array([1.0, 2.0, 3.0])
    b = 2.0 * u.mm
    c = a + b
    d = [Quantity(1.0, u.m), Quantity(2.0, u.m), Quantity(3.0, u.mm)]
    e = [b + q for q in d]

t1 = time.time()
print(f"pint: {(t1 - t0) / n_samples:.4f} seconds")
