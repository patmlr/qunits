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

CONTEXT_DICT: dict[str, str] = {
    "angle": "rad",
}
CONTEXT_DICT_UNIT: dict[str, str] = {v: k for k, v in CONTEXT_DICT.items()}
