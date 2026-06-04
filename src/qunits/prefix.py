from enum import IntEnum
from typing import Literal

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

type ExpMap = frozenset[tuple[str, int]]


def _merge_exp_maps(a: ExpMap, b: ExpMap, sign_b: Literal[1, -1]) -> ExpMap:
    exp_dict = dict(a)
    for symbol, exp in b:
        new = exp_dict.get(symbol, 0) + sign_b * exp
        if new:
            exp_dict[symbol] = new
        else:
            exp_dict.pop(symbol, None)
    return frozenset(exp_dict.items())


class Context(IntEnum):
    """The context of a unit."""

    I = 0
    ANGLE = 1


CONTEXT_DICT: dict[Context, str] = {
    Context.ANGLE: "rad",
}
CONTEXT_DICT_UNIT: dict[str, Context] = {v: k for k, v in CONTEXT_DICT.items()}
