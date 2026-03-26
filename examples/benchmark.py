import time

import numpy as np
from pint import UnitRegistry

from qunits import Quantity, si
from qunits.dimension import _dimension_cache
from qunits.unit import _unit_cache

u = UnitRegistry()
u.m
u.mm
u.s


def bench_init(name: str, u: UnitRegistry | type, n: int = 1_000_000) -> float:
    m = u.m
    mm = u.mm

    t0 = time.perf_counter()
    for _ in range(n):
        _ = (3 * m) + (4 * mm)  # type: ignore

    dt = time.perf_counter() - t0
    print(f"init({name}): {dt:.2f} s")
    return dt


def bench_units(name: str, u: UnitRegistry | type, n: int = 1_000_000) -> float:
    m = u.m
    s = u.s

    t0 = time.perf_counter()
    for _ in range(n):
        _ = m / s
        _ = m * s

    dt = time.perf_counter() - t0
    print(f"units({name}): {dt:.2f} s")
    return dt


def bench_array_ops(name: str, u: UnitRegistry | type, q: type, n: int = 1_000) -> float:
    arr = np.ones(1_000_000)
    a = q(arr, u.m)
    b = q(arr, u.mm)

    t0 = time.perf_counter()
    for _ in range(n):
        _ = a + b

    dt = time.perf_counter() - t0
    print(f"array_ops({name}): {dt:.2f} s")
    return dt


if __name__ == "__main__":
    n_samples = 100_000
    dt_pint = bench_init("pint", u, n=n_samples)
    dt_qunits = bench_init("qunits", si, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000_000
    dt_pint = bench_units("pint", u, n=n_samples)
    dt_qunits = bench_units("qunits", si, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000
    dt_pint = bench_array_ops("pint", u, u.Quantity, n=n_samples)
    dt_qunits = bench_array_ops("qunits", si, Quantity, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    print(f"dimension cache size: {len(_dimension_cache)}")
    print(f"unit cache size: {len(_unit_cache)}")
