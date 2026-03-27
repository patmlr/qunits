from qunits.dimension import SYMBOL_FACTORS, SYMBOL_PREFIXES, SYMBOLS
from qunits.prefix import PREFIX_DICT


def generate_units() -> None:
    """Generate units with prefixes."""
    dimensions = sorted(set(SYMBOLS.values()), key=lambda d: d.__name__)
    with open("src/qunits/si.py", "w") as f:
        f.write("# Auto-generated units with prefixes\n\n")
        f.write(f"from qunits.dimension import {', '.join(d.__name__ for d in dimensions)}\n")
        f.write("from qunits.unit import Unit\n\n\n")
        f.write('class si:\n    """The SI unit system."""\n\n')

        for symbol, dimension in SYMBOLS.items():
            for prefix_str, prefix_exp in PREFIX_DICT.items():
                if not (SYMBOL_PREFIXES[symbol][0] <= prefix_exp <= SYMBOL_PREFIXES[symbol][1]):
                    continue

                prefix = 10**prefix_exp
                factor = SYMBOL_FACTORS[symbol]
                scale = prefix * factor

                unit_name = f"{prefix_str}{symbol}"
                unit_name = unit_name.replace("as", "attosecond")

                f.write(
                    f"    {unit_name} = Unit("
                    f'{scale:.1e}, {dimension.__name__}, symbol="{symbol}", prefix_exp={prefix_exp})\n'
                )


if __name__ == "__main__":
    generate_units()
