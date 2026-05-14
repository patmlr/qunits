import os
import time

import numpy as np
from pint import UnitRegistry

from qunits import Quantity, u
from qunits.dimension import _dimension_cache
from qunits.unit import _unit_cache

p = UnitRegistry(cache_folder=os.path.join(os.path.dirname(__file__), "__pintcache__"))


def bench_init(name: str, ureg: UnitRegistry | type, n: int = 100_000) -> float:
    m = ureg.m
    mm = ureg.mm

    t0 = time.perf_counter()
    for _ in range(n):
        _ = (3 * m) + (4 * mm)  # type: ignore

    dt = time.perf_counter() - t0
    print(f"init({name}): {dt:.2f} s")
    return dt


def bench_inplace(name: str, ureg: UnitRegistry | type, n: int = 100_000) -> float:
    m = ureg.m
    mm = ureg.mm

    a = 3 * m
    b = 4 * mm

    t0 = time.perf_counter()
    for _ in range(n):
        a += b  # type: ignore
        a -= b  # type: ignore
        a *= b  # type: ignore
        a /= b  # type: ignore

    dt = time.perf_counter() - t0
    print(f"inplace({name}): {dt:.2f} s")
    return dt


def bench_units(name: str, ureg: UnitRegistry | type, n: int = 1_000_000) -> float:
    m = ureg.m
    s = ureg.s

    t0 = time.perf_counter()
    for _ in range(n):
        _ = m / s
        _ = m * s

    dt = time.perf_counter() - t0
    print(f"units({name}): {dt:.2f} s")
    return dt


def bench_array_ops(name: str, ureg: UnitRegistry | type, q: type, n: int = 1_000) -> float:
    arr = np.ones(1_000_000)
    a = q(arr, ureg.m)
    b = q(arr, ureg.mm)

    t0 = time.perf_counter()
    for _ in range(n):
        _ = a + b

    dt = time.perf_counter() - t0
    print(f"array_ops({name}): {dt:.2f} s")
    return dt


def bench_conversion(name: str, ureg: UnitRegistry | type, q: type, n: int = 1_000) -> float:
    m = ureg.m
    mm = ureg.mm
    arr = np.ones(1_000_000)
    a = q(arr, mm)

    t0 = time.perf_counter()
    for _ in range(n):
        _ = a.to(m)
        _ = a.m_as(m)

    dt = time.perf_counter() - t0
    print(f"conversion({name}): {dt:.2f} s")
    return dt


if __name__ == "__main__":
    n_samples = 100_000
    dt_pint = bench_init("pint", p, n=n_samples)
    dt_qunits = bench_init("qunits", u, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 100_000
    dt_pint = bench_inplace("pint", p, n=n_samples)
    dt_qunits = bench_inplace("qunits", u, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000_000
    dt_pint = bench_units("pint", p, n=n_samples)
    dt_qunits = bench_units("qunits", u, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000
    dt_pint = bench_array_ops("pint", p, p.Quantity, n=n_samples)
    dt_qunits = bench_array_ops("qunits", u, Quantity, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 1_000
    dt_pint = bench_conversion("pint", p, p.Quantity, n=n_samples)
    dt_qunits = bench_conversion("qunits", u, Quantity, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    print(f"qunits dimension cache size: {len(_dimension_cache)}")
    print(f"qunits unit cache size: {len(_unit_cache)}")
