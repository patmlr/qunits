
import os
import inspect
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


STYLE = "tango"


def example_0():
    from qunits import u

    B = 0.42 * u.T  # >>> 0.42 T


def example_1():
    from qunits import u
    # This imports all default units with prefixes.

    s = 8 * u.m
    dt = 2 * u.ms
    v = s / dt

    print(v.unit.d, v)
    # 4.0e3 m/s

    a = v / (2 * u.s)

    print(a.unit.d, a)
    # 4.0e3 m/s^2

    f = 200 * u.kg * a
    print(f.unit.d, f)
    # 8.0e5 N



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
    gen_example(1)
    example_1()
