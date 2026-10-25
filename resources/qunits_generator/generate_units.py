import os
from math import log10

from config import SYMBOL_CONTEXTS, SYMBOL_DOCS, SYMBOL_FACTORS, SYMBOL_PREFIXES, SYMBOLS

from qunits.prefix import PREFIX_DICT, Context

REGISTRY_DOC = '''    """
    The unit registry: the SI units with prefixes, and further common units and physical constants as units.

    - The prefixes are written in ASCII, e.g. `u.us` for microsecond. The attosecond is `u.attosecond`, because `as`
      is a keyword.
    - The units are named by their symbols, e.g. `u.Ohm` for ohm and `u.G` for gauss.
    - `u.I` is the dimensionless unit and `u.percent` is 0.01.
    - The angle units `u.rad` and `u.pi` (pi rad) have the context `Context.ANGLE`.
    - `u.c`, `u.h` and `u.e` are the speed of light, the Planck constant and the elementary charge, and `u.u` is the
      atomic mass unit.
    """
'''


def _literal(value: float) -> str:
    """The float literal of `value` in the format of ruff, e.g. 1.0e03 and 1.0e-03."""
    return f"{value:.1e}".replace("e+", "e")


def generate_units() -> None:
    """Generate units with prefixes."""
    path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "src", "qunits", "registry.py")
    dimensions = sorted(set(SYMBOLS.values()), key=lambda d: d.__name__)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Auto-generated units with prefixes\n\n")
        f.write("from math import pi\n\n")
        f.write("import scipy.constants as sc\n\n")
        f.write("from qunits.dimension import (\n")
        f.write(f"    {',\n    '.join(d.__name__ for d in dimensions)},\n)\n")
        f.write("from qunits.prefix import Context\n")
        f.write("from qunits.unit import I, Unit\n\n")
        f.write('__all__ = ["u"]\n\n\n')
        f.write(f"class u:\n{REGISTRY_DOC}\n")
        f.write('    I = I\n    """The dimensionless unit."""\n\n')

        for symbol, dimension in SYMBOLS.items():
            for prefix_str, prefix_exp in PREFIX_DICT.items():
                if not (SYMBOL_PREFIXES[symbol][0] <= prefix_exp <= SYMBOL_PREFIXES[symbol][1]):
                    continue

                factor, factor_str = SYMBOL_FACTORS[symbol]
                context = SYMBOL_CONTEXTS.get(symbol, Context.I)
                context_str = f"Context.{context.name}"

                power = log10(factor)
                if power.is_integer():
                    scale_str = _literal(10.0 ** (prefix_exp + int(power)))
                else:
                    scale_str = f"{_literal(10.0**prefix_exp)} * {factor_str}"

                unit_name = f"{prefix_str}{symbol}"
                unit_name = unit_name.replace("as", "attosecond")

                exp_map = f'frozenset({{("{unit_name}", 1)}})'

                f.write(f"    {unit_name} = Unit({scale_str}, {exp_map}, {dimension.__name__}, {context_str})\n")
                if prefix_exp == 0 and symbol in SYMBOL_DOCS:
                    f.write(f'    """{SYMBOL_DOCS[symbol]}"""\n')


if __name__ == "__main__":
    generate_units()
