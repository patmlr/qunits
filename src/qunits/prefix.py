import math

PREFIX_DICT_EXP: dict[int, str] = {
    -30: "q",
    -27: "r",
    -24: "y",
    -21: "z",
    -18: "a",
    -15: "f",
    -12: "p",
    -9: "n",
    -6: "u",
    -3: "m",
    0: "",
    3: "k",
    6: "M",
    9: "G",
    12: "T",
    15: "P",
    18: "E",
    21: "Z",
    24: "Y",
    27: "R",
    30: "Q",
}
PREFIX_DICT: dict[str, int] = {v: k for k, v in PREFIX_DICT_EXP.items()}


class Prefix:
    """A class for prefixes."""

    @classmethod
    def from_str(cls, symbol: str) -> float:
        """Create a prefix from a string.

        Args:
            symbol: The symbol of the prefix (e.g., "k" for kilo).
        """
        exp = PREFIX_DICT.get(symbol)
        if exp is None:
            raise ValueError(f"Invalid prefix symbol: {symbol}")

        return 10**exp

    @classmethod
    def from_exp(cls, exp: int) -> float:
        """Create a prefix from an integer exponent.

        Args:
            exp: The exponent by which the unit is multiplied (e.g., 3 for kilo).
        """
        symbol = PREFIX_DICT_EXP.get(exp)
        if symbol is None:
            raise ValueError(f"Invalid integer exponent: {exp}")

        return 10**exp

    @classmethod
    def from_float(cls, factor: float) -> float:
        """Create a prefix from a float.

        Args:
            factor: The factor by which the unit is multiplied.
        """
        exp = int(math.log10(factor))
        symbol = PREFIX_DICT_EXP.get(exp)
        if symbol is None:
            raise ValueError(f"Invalid prefix factor: {factor}")

        return factor
