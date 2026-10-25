# docs: overview-0
from qunits import u

v = 42 * u.m / u.s  # >>> 42.0 m/s
v += 0.69 * u.mm / u.us  # >>> 732.0 m/s

s = 101 * u.m + 7 * u.s * v  # >>> 5225.0 m
s = s.to(u.km)  # >>> 5.225 km
# docs: end

print(v)
print(s)
