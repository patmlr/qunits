import os

from config import SYMBOL_FACTORS, SYMBOL_PREFIXES, SYMBOLS

from qunits.prefix import PREFIX_DICT


def generate_units() -> None:
    """Generate units with prefixes."""
    path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "src", "qunits", "u.py")
    dimensions = sorted(set(SYMBOLS.values()), key=lambda d: d.__name__)
    with open(path, "w") as f:
        f.write("# Auto-generated units with prefixes\n\n")
        f.write("import scipy.constants as sc\n\n")
        f.write("from qunits.dimension import (\n")
        f.write(f"    {',\n    '.join(d.__name__ for d in dimensions)},\n)\n")
        f.write("from qunits.unit import Unit\n\n\n")
        f.write('class u:\n    """The unit system."""\n\n')

        for symbol, dimension in SYMBOLS.items():
            for prefix_str, prefix_exp in PREFIX_DICT.items():
                if not (SYMBOL_PREFIXES[symbol][0] <= prefix_exp <= SYMBOL_PREFIXES[symbol][1]):
                    continue

                prefix = 10**prefix_exp
                factor = SYMBOL_FACTORS[symbol][0]

                scale_str = f"{prefix:.1e} * {SYMBOL_FACTORS[symbol][1]}" if factor != 1.0 else f"{prefix:.1e}"

                unit_name = f"{prefix_str}{symbol}"
                unit_name = unit_name.replace("as", "attosecond")

                f.write(
                    f"    {unit_name} = Unit("
                    f'{scale_str}, {dimension.__name__}, symbol="{symbol}", prefix_exp={prefix_exp})\n'
                )


if __name__ == "__main__":
    generate_units()
