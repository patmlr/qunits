import time

import numpy as np
from pint import UnitRegistry

from qunits import Quantity, u
from qunits.dimension import _dimension_cache
from qunits.unit import _unit_cache

up = UnitRegistry()
up.m
up.mm
up.s


def bench_init(name: str, _u: UnitRegistry | type, n: int = 1_000_000) -> float:
    m = _u.m
    mm = _u.mm

    t0 = time.perf_counter()
    for _ in range(n):
        _ = (3 * m) + (4 * mm)  # type: ignore

    dt = time.perf_counter() - t0
    print(f"init({name}): {dt:.2f} s")
    return dt


def bench_units(name: str, _u: UnitRegistry | type, n: int = 1_000_000) -> float:
    m = _u.m
    s = _u.s

    t0 = time.perf_counter()
    for _ in range(n):
        _ = m / s
        _ = m * s

    dt = time.perf_counter() - t0
    print(f"units({name}): {dt:.2f} s")
    return dt


def bench_array_ops(name: str, _u: UnitRegistry | type, q: type, n: int = 1_000) -> float:
    arr = np.ones(1_000_000)
    a = q(arr, _u.m)
    b = q(arr, _u.mm)

    t0 = time.perf_counter()
    for _ in range(n):
        _ = a + b

    dt = time.perf_counter() - t0
    print(f"array_ops({name}): {dt:.2f} s")
    return dt


def bench_conversion(name: str, _u: UnitRegistry | type, q: type, n: int = 1_000) -> float:
    arr = np.ones(1_000_000)
    a = q(arr, _u.mm)

    t0 = time.perf_counter()
    for _ in range(n):
        _ = a.to(_u.m)

    dt = time.perf_counter() - t0
    print(f"conversion({name}): {dt:.2f} s")
    return dt


if __name__ == "__main__":
    n_samples = 100_000
    dt_pint = bench_init("pint", up, n=n_samples)
    dt_qunits = bench_init("qunits", u, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000_000
    dt_pint = bench_units("pint", up, n=n_samples)
    dt_qunits = bench_units("qunits", u, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000
    dt_pint = bench_array_ops("pint", up, up.Quantity, n=n_samples)
    dt_qunits = bench_array_ops("qunits", u, Quantity, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000
    dt_pint = bench_conversion("pint", up, up.Quantity, n=n_samples)
    dt_qunits = bench_conversion("qunits", u, Quantity, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    print(f"dimension cache size: {len(_dimension_cache)}")
    print(f"unit cache size: {len(_unit_cache)}")
