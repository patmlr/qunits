from collections.abc import Callable
from typing import Any

from qunits.prefix import ExpMap, merge_exp_maps

__all__ = [
    "Acceleration",
    "Action",
    "AmountOfSubstance",
    "Area",
    "Capacitance",
    "Charge",
    "Dimensionless",
    "ElectricCurrent",
    "ElectricField",
    "Energy",
    "Force",
    "Frequency",
    "Jerk",
    "Length",
    "LuminousIntensity",
    "MagneticInduction",
    "Mass",
    "Power",
    "Pressure",
    "Resistance",
    "Temperature",
    "Time",
    "Velocity",
    "Voltage",
    "Volume",
]

type DimensionVec = tuple[int, ...]

_dimension_cache: dict[DimensionVec, type["Dimension"]] = {}


class Dimension:
    """The base class for dimensions."""

    name: str
    si_map: ExpMap

    vec: DimensionVec


# Special dimensions for dimensionless quantities


class Dimensionless(Dimension):
    """The dimension of dimensionless quantities."""

    name = "Dimensionless"
    si_map = frozenset()

    vec = (0, 0, 0, 0, 0, 0, 0)


_dimension_cache.setdefault(Dimensionless.vec, Dimensionless)


# Base dimensions


class Time(Dimension):
    """The dimension of time."""

    name = "Time"
    si_map = frozenset({("s", 1)})

    vec = (1, 0, 0, 0, 0, 0, 0)


class Length(Dimension):
    """The dimension of length."""

    name = "Length"
    si_map = frozenset({("m", 1)})

    vec = (0, 1, 0, 0, 0, 0, 0)


class Mass(Dimension):
    """The dimension of mass."""

    name = "Mass"
    si_map = frozenset({("kg", 1)})

    vec = (0, 0, 1, 0, 0, 0, 0)


class ElectricCurrent(Dimension):
    """The dimension of electric current."""

    name = "ElectricCurrent"
    si_map = frozenset({("A", 1)})

    vec = (0, 0, 0, 1, 0, 0, 0)


class Temperature(Dimension):
    """The dimension of temperature."""

    name = "Temperature"
    si_map = frozenset({("K", 1)})

    vec = (0, 0, 0, 0, 1, 0, 0)


class AmountOfSubstance(Dimension):
    """The dimension of amount of substance."""

    name = "AmountOfSubstance"
    si_map = frozenset({("mol", 1)})

    vec = (0, 0, 0, 0, 0, 1, 0)


class LuminousIntensity(Dimension):
    """The dimension of luminous intensity."""

    name = "LuminousIntensity"
    si_map = frozenset({("cd", 1)})

    vec = (0, 0, 0, 0, 0, 0, 1)


_base_dimensions = (Time, Length, Mass, ElectricCurrent, Temperature, AmountOfSubstance, LuminousIntensity)

for _b in _base_dimensions:
    _dimension_cache.setdefault(_b.vec, _b)


# Composite dimensions


class Frequency(Dimension):
    """The dimension of frequency."""

    name = "Frequency"
    si_map = frozenset({("Hz", 1)})

    vec = tuple(-t for t in Time.vec)


class Area(Dimension):
    """The dimension of area."""

    name = "Area"
    si_map = frozenset({("m^2", 2)})

    vec = tuple(2 * l for l in Length.vec)


class Volume(Dimension):
    """The dimension of volume."""

    name = "Volume"
    si_map = frozenset({("m^3", 3)})

    vec = tuple(3 * l for l in Length.vec)


class Velocity(Dimension):
    """The dimension of velocity."""

    name = "Velocity"
    si_map = frozenset({("m", 1), ("s", -1)})

    vec = tuple(l - t for l, t in zip(Length.vec, Time.vec))


class Acceleration(Dimension):
    """The dimension of acceleration."""

    name = "Acceleration"
    si_map = frozenset({("m", 1), ("s", -2)})

    vec = tuple(l - 2 * t for l, t in zip(Length.vec, Time.vec))


class Jerk(Dimension):
    """The dimension of jerk."""

    name = "Jerk"
    si_map = frozenset({("m", 1), ("s", -3)})

    vec = tuple(l - 3 * t for l, t in zip(Length.vec, Time.vec))


class Force(Dimension):
    """The dimension of force."""

    name = "Force"
    si_map = frozenset({("N", 1)})

    vec = tuple(m + a for m, a in zip(Mass.vec, Acceleration.vec))


class Pressure(Dimension):
    """The dimension of pressure."""

    name = "Pressure"
    si_map = frozenset({("Pa", 1)})

    vec = tuple(f - a for f, a in zip(Force.vec, Area.vec))


class Energy(Dimension):
    """The dimension of energy."""

    name = "Energy"
    si_map = frozenset({("J", 1)})

    vec = tuple(f + l for f, l in zip(Force.vec, Length.vec))


class Power(Dimension):
    """The dimension of power."""

    name = "Power"
    si_map = frozenset({("W", 1)})

    vec = tuple(e - t for e, t in zip(Energy.vec, Time.vec))


class Action(Dimension):
    """The dimension of action."""

    name = "Action"
    si_map = frozenset({("J", 1), ("s", 1)})

    vec = tuple(e + t for e, t in zip(Energy.vec, Time.vec))


class Charge(Dimension):
    """The dimension of electric charge."""

    name = "Charge"
    si_map = frozenset({("C", 1)})

    vec = tuple(i + t for i, t in zip(ElectricCurrent.vec, Time.vec))


class Voltage(Dimension):
    """The dimension of electric potential difference."""

    name = "Voltage"
    si_map = frozenset({("V", 1)})

    vec = tuple(e - q for e, q in zip(Energy.vec, Charge.vec))


class Capacitance(Dimension):
    """The dimension of capacitance."""

    name = "Capacitance"
    si_map = frozenset({("F", 1)})

    vec = tuple(q - v for q, v in zip(Charge.vec, Voltage.vec))


class Resistance(Dimension):
    """The dimension of electric resistance."""

    name = "Resistance"
    si_map = frozenset({("Ohm", 1)})

    vec = tuple(v - i for v, i in zip(Voltage.vec, ElectricCurrent.vec))


class ElectricField(Dimension):
    """The dimension of electric field."""

    name = "ElectricField"
    si_map = frozenset({("V", 1), ("m", -1)})

    vec = tuple(v - l for v, l in zip(Voltage.vec, Length.vec))


class MagneticInduction(Dimension):
    """The dimension of magnetic induction."""

    name = "MagneticInduction"
    si_map = frozenset({("T", 1)})

    vec = tuple(m - i - 2 * t for m, i, t in zip(Mass.vec, ElectricCurrent.vec, Time.vec))


_composite_dimensions = (
    Frequency,
    Area,
    Volume,
    Velocity,
    Acceleration,
    Jerk,
    Force,
    Pressure,
    Energy,
    Power,
    Action,
    Charge,
    Voltage,
    Capacitance,
    Resistance,
    ElectricField,
    MagneticInduction,
)

for _c in _composite_dimensions:
    _dimension_cache.setdefault(_c.vec, _c)


def id_dimension(vec: DimensionVec) -> DimensionVec:
    return vec


def add_dimension(a: DimensionVec, b: DimensionVec) -> DimensionVec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3], a[4] + b[4], a[5] + b[5], a[6] + b[6])


def sub_dimension(a: DimensionVec, b: DimensionVec) -> DimensionVec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2], a[3] - b[3], a[4] - b[4], a[5] - b[5], a[6] - b[6])


def inv_dimension(a: DimensionVec) -> DimensionVec:
    return (-a[0], -a[1], -a[2], -a[3], -a[4], -a[5], -a[6])


def pow_dimension(a: DimensionVec, power: int) -> DimensionVec:
    return (a[0] * power, a[1] * power, a[2] * power, a[3] * power, a[4] * power, a[5] * power, a[6] * power)


def new_dimension(dimension: type[Dimension], func: Callable[..., DimensionVec], *args: Any) -> type[Dimension]:
    """Get a dimension class from a dimension vector.

    :param dimension: The base dimension.
    :param func: A function that returns a dimension vector.
    :param args: Additional arguments to pass to the function.

    :returns: The dimension class.
    """
    vec = func(dimension.vec, *args)
    dimension_new = _dimension_cache.get(vec)

    if dimension_new is not None:
        return dimension_new

    if func is id_dimension:
        si_map = frozenset((next(iter(dim.si_map))[0], v) for dim, v in zip(_base_dimensions, vec) if v != 0)
        name = "__MUL__".join(f"{dim.name}__POW__{v}" for dim, v in zip(_base_dimensions, vec) if v != 0)

    elif func is add_dimension:
        vec_delta = sub_dimension(vec, dimension.vec)
        dimension_delta = _dimension_cache.get(vec_delta)
        if dimension_delta is None:
            dimension_delta = new_dimension(dimension, id_dimension)
        si_map = merge_exp_maps(dimension.si_map, dimension_delta.si_map, 1)
        name = f"{dimension.name}__MUL__{dimension_delta.name}"

    elif func is sub_dimension:
        vec_delta = sub_dimension(dimension.vec, vec)
        dimension_delta = _dimension_cache.get(vec_delta)
        if dimension_delta is None:
            dimension_delta = new_dimension(dimension, id_dimension)
        si_map = merge_exp_maps(dimension.si_map, dimension_delta.si_map, -1)
        name = f"{dimension.name}__DIV__{dimension_delta.name}"

    elif func is inv_dimension:
        si_map = merge_exp_maps(frozenset(), dimension.si_map, -1)
        name = f"Inv__{dimension.name}"

    elif func is pow_dimension:
        exponent = args[0]
        si_map = frozenset((symbol, exp * exponent) for symbol, exp in dimension.si_map)
        name = f"{dimension.name}__POW__{exponent}"

    else:
        raise ValueError(f"Invalid function `{func}`")

    dimension_new = type(name, (Dimension,), {"name": name, "vec": vec, "si_map": si_map})
    _dimension_cache[vec] = dimension_new
    return dimension_new


if __name__ == "__main__":
    for dim in _dimension_cache.values():
        assert new_dimension(dim, id_dimension) is dim

    print(f"dimension cache size: {len(_dimension_cache)}")
