from qunits.prefix import PREFIX_DICT, Prefix
from qunits.unit import SYMBOL_FACTORS, SYMBOLS


def generate_units() -> None:
    """Generate units with prefixes."""
    dimensions = set(SYMBOLS.values())
    with open("src/qunits/si.py", "w") as f:
        f.write("# Auto-generated units with prefixes\n\n")
        f.write(f"from qunits.dimension import {', '.join(d.__name__ for d in dimensions)}\n")
        f.write("from qunits.unit import Unit\n\n\n")
        f.write('class si:\n    """The SI unit system."""\n\n')

        for symbol, dimension in SYMBOLS.items():
            for prefix_str in PREFIX_DICT:
                factor = SYMBOL_FACTORS[symbol]
                prefix = Prefix.from_str(prefix_str)
                unit_name = f"{prefix_str}{symbol}"

                unit_name = unit_name.replace("µ", "u")
                unit_name = unit_name.replace("as", "attosecond")

                f.write(f"    {unit_name} = Unit[{dimension.__name__}](factor={factor: .1e}, prefix={prefix: .1e})\n")


if __name__ == "__main__":
    generate_units()
