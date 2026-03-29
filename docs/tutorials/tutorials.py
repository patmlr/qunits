
import os
import inspect
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


STYLE = "tango"


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
