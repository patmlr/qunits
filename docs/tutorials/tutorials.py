
import os
import inspect
from turtle import up
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


STYLE = "catppuccin-latte"  # "tango"


def example_0():
    from qunits import u

    q = 2 * u.e  # >>> 2.0 e
    v = 2e5 * u.m / u.s  # >>> 200000.0 m/s
    B = 0.42 * u.mT  # >>> 0.42 mT

    F = q * v * B  # >>> 2.69165674512e-17 N


def example_1():
    from qunits import u
    # This imports all default units with prefixes.

    s = 8 * u.m
    dt = 2 * u.ms
    v = s / dt  # >>> 4000.0 m/s

    a = v / (2 * u.s)  # >>> 2000.0 m/s^2

    f = 200 * u.kg * a  # >>> 400.0 kN

def example_2():
    import os
    import time

    import numpy as np
    from pint import UnitRegistry

    from qunits import Quantity, u
    from qunits.dimension import _dimension_cache
    from qunits.unit import _unit_cache

    pintcache = os.path.join(os.path.dirname(__file__), "__pintcache__")
    p = UnitRegistry(cache_folder=pintcache)


    def bench_init(name, ureg, n=100_000) -> float:
        m = ureg.m
        mm = ureg.mm

        t0 = time.perf_counter()
        for _ in range(n):
            _ = (3 * m) + (4 * mm)  # type: ignore

        dt = time.perf_counter() - t0
        print(f"init({name}): {dt:.2f} s")
        return dt


    def bench_inplace(name, ureg, n: int = 100_000) -> float:
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


    def bench_units(name, ureg, n=1_000_000) -> float:
        m = ureg.m
        s = ureg.s

        t0 = time.perf_counter()
        for _ in range(n):
            _ = m / s
            _ = m * s

        dt = time.perf_counter() - t0
        print(f"arithmetics({name}): {dt:.2f} s")
        return dt


    def bench_array_ops(name, ureg, q, n=1_000) -> float:
        arr = np.ones(1_000_000)
        a = q(arr, ureg.m)
        b = q(arr, ureg.mm)

        t0 = time.perf_counter()
        for _ in range(n):
            _ = a + b

        dt = time.perf_counter() - t0
        print(f"array_ops({name}): {dt:.2f} s")
        return dt


    def bench_conversion(name, ureg, q, n=1_000) -> float:
        m = ureg.m
        mm = ureg.mm
        arr = np.ones(1_000_000)
        a = q(arr, mm)

        t0 = time.perf_counter()
        for _ in range(n):
            _ = a.to(m)

        dt = time.perf_counter() - t0
        print(f"conversion({name}): {dt:.2f} s")
        return dt


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


def pycode_to_html(code):
    style = get_style_by_name(STYLE)
    lexer = get_lexer_by_name("python", stripall=True)
    formatter = HtmlFormatter(linenos=False, cssclass="py-source", style=style)
    html = highlight(code, lexer, formatter)
    print(html)


def gen_pycode_css():
    style = get_style_by_name(STYLE)
    formatter = HtmlFormatter(cssclass="py-source", style=style)
    css = formatter.get_style_defs()
    with open(os.path.join(os.pardir, "_sass", "pycode.scss"), "w") as css_file:
        css_file.write(css)


def gen_example(n):
    # with open(os.path.join(os.pardir, os.pardir, "examples", "overview_tut.py"), "r") as py_file:
    #     code = py_file.read()
    code = inspect.getsource(eval(f"example_{n}"))
    pycode_to_html(code)


if __name__ == "__main__":
    # gen_pycode_css()
    gen_example(2)
    example_2()
