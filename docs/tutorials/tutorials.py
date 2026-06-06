
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

    v = 42 * u.m / u.s  # >>> 42.0 m/s
    v += 0.69 * u.mm / u.us  # >>> 732.0 m/s

    s = 101 * u.m + 7 * u.s * v  # >>> 5225.0 m
    s = s.to(u.km)  # >>> 5.225 km


def example_1():
    import numpy as np
    from qunits import u

    q = 2 * u.e  # >>> 2.0 e
    v = 2e5 * u.m / u.s  # >>> 200000.0 m/s
    B = 0.42 * u.mT  # >>> 0.42 mT

    F = q * v * B  # >>> 168000.0 e⋅m⋅mT/s
    F = F.to_base_units()  # >>> 2.6916567451199998e-17 N
    F = F.to(u.e * u.V / u.m)  # >>> 168.0 e⋅V/m

    omega = 2 * u.pi * u.kHz  # >>> 2.0 pi⋅kHz
    T = np.linspace(0, 10, 6) * u.ms  # >>> [ 0.  2.  4.  6.  8. 10.] ms

    Ft = F * np.sin(omega * T)  # >>> [ 0.  -127.14281921  ...  153.37480212] V⋅e/m

    print(q)
    print(v)
    print(B)
    print(F)
    print(omega)
    print(T)
    print(Ft)

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


    def bench_init(name, ureg, n=100_000):
        m = ureg.m
        mm = ureg.mm

        t0 = time.perf_counter()
        for _ in range(n):
            _ = (3 * m) + (4 * mm)  # type: ignore

        dt = time.perf_counter() - t0
        print(f"init({name}): {dt:.2f} s")
        return dt


    def bench_inplace(name, ureg, n=100_000):
        m = ureg.m
        mm = ureg.mm

        a = 3 * m
        b = 4 * mm

        t0 = time.perf_counter()
        for _ in range(n):
            a += b
            a -= b
            a *= b
            a /= b

        dt = time.perf_counter() - t0
        print(f"inplace({name}): {dt:.2f} s")
        return dt


    def bench_units(name, ureg, n=1_000_000):
        m = ureg.m
        s = ureg.s

        t0 = time.perf_counter()
        for _ in range(n):
            _ = m / s
            _ = m * s

        dt = time.perf_counter() - t0
        print(f"units({name}): {dt:.2f} s")
        return dt


    def bench_array_ops(name, ureg, q, n=200):
        arr = np.ones(1_000_000)
        a = q(arr, ureg.m)
        b = q(arr, ureg.mm)

        t0 = time.perf_counter()
        for _ in range(n):
            _ = a + b
            _ = a - b
            _ = a * b
            _ = a / b

        dt = time.perf_counter() - t0
        print(f"array_ops({name}): {dt:.2f} s")
        return dt


    def bench_conversion(name, ureg, q, n=100_000):
        m = ureg.m
        mm = ureg.mm
        a = q(5.0, mm)

        t0 = time.perf_counter()
        for _ in range(n):
            _ = a.to(m)
            _ = a.m_as(m)

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

    n_samples = 200
    dt_pint = bench_array_ops("pint", p, p.Quantity, n=n_samples)
    dt_qunits = bench_array_ops("qunits", u, Quantity, n=n_samples)
    print(f"Speedup: {dt_pint / dt_qunits:.2f}x\n")

    n_samples = 100_000
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
    gen_example(0)
    example_0()
