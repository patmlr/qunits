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

_dimension_cache: dict[tuple[int, ...], type["Dimension"]] = {}


class Dimension:
    """The base class for dimensions."""

    name: str
    si_symbol: str
    prefixed: bool

    vec: tuple[int, ...]


# Special dimensions for dimensionless quantities


class Dimensionless(Dimension):
    """The dimension of dimensionless quantities."""

    name: str = "Dimensionless"
    si_symbol: str = ""
    prefixed = False

    vec = (0, 0, 0, 0, 0, 0, 0)


_dimension_cache.setdefault(Dimensionless.vec, Dimensionless)


# Base dimensions


class Time(Dimension):
    """The dimension of time."""

    name: str = "Time"
    si_symbol: str = "s"
    prefixed = True

    vec = (1, 0, 0, 0, 0, 0, 0)


class Length(Dimension):
    """The dimension of length."""

    name: str = "Length"
    si_symbol: str = "m"
    prefixed = True

    vec = (0, 1, 0, 0, 0, 0, 0)


class Mass(Dimension):
    """The dimension of mass."""

    name: str = "Mass"
    si_symbol: str = "g"
    prefixed = True

    vec = (0, 0, 1, 0, 0, 0, 0)


class ElectricCurrent(Dimension):
    """The dimension of electric current."""

    name: str = "ElectricCurrent"
    si_symbol: str = "A"
    prefixed = True

    vec = (0, 0, 0, 1, 0, 0, 0)


class Temperature(Dimension):
    """The dimension of temperature."""

    name: str = "Temperature"
    si_symbol: str = "K"
    prefixed = True

    vec = (0, 0, 0, 0, 1, 0, 0)


class AmountOfSubstance(Dimension):
    """The dimension of amount of substance."""

    name: str = "AmountOfSubstance"
    si_symbol: str = "mol"
    prefixed = True

    vec = (0, 0, 0, 0, 0, 1, 0)


class LuminousIntensity(Dimension):
    """The dimension of luminous intensity."""

    name: str = "LuminousIntensity"
    si_symbol: str = "cd"
    prefixed = True

    vec = (0, 0, 0, 0, 0, 0, 1)


_base_dimensions = (Time, Length, Mass, ElectricCurrent, Temperature, AmountOfSubstance, LuminousIntensity)

for _b in _base_dimensions:
    _dimension_cache.setdefault(_b.vec, _b)


# Composite dimensions


class Frequency(Dimension):
    """The dimension of frequency."""

    name: str = "Frequency"
    si_symbol: str = "Hz"
    prefixed = True

    vec = tuple(-t for t in Time.vec)


class Area(Dimension):
    """The dimension of area."""

    name: str = "Area"
    si_symbol: str = "m^2"
    prefixed = False

    vec = tuple(2 * l for l in Length.vec)


class Volume(Dimension):
    """The dimension of volume."""

    name: str = "Volume"
    si_symbol: str = "m^3"
    prefixed = False

    vec = tuple(3 * l for l in Length.vec)


class Velocity(Dimension):
    """The dimension of velocity."""

    name: str = "Velocity"
    si_symbol: str = "m/s"
    prefixed = False

    vec = tuple(l - t for l, t in zip(Length.vec, Time.vec))


class Acceleration(Dimension):
    """The dimension of acceleration."""

    name: str = "Acceleration"
    si_symbol: str = "m/s^2"
    prefixed = False

    vec = tuple(l - 2 * t for l, t in zip(Length.vec, Time.vec))


class Jerk(Dimension):
    """The dimension of jerk."""

    name: str = "Jerk"
    si_symbol: str = "m/s^3"
    prefixed = False

    vec = tuple(l - 3 * t for l, t in zip(Length.vec, Time.vec))


class Force(Dimension):
    """The dimension of force."""

    name: str = "Force"
    si_symbol: str = "N"
    prefixed = True

    vec = tuple(m + a for m, a in zip(Mass.vec, Acceleration.vec))


class Pressure(Dimension):
    """The dimension of pressure."""

    name: str = "Pressure"
    si_symbol: str = "Pa"
    prefixed = True

    vec = tuple(f - a for f, a in zip(Force.vec, Area.vec))


class Energy(Dimension):
    """The dimension of energy."""

    name: str = "Energy"
    si_symbol: str = "J"
    prefixed = True

    vec = tuple(f + l for f, l in zip(Force.vec, Length.vec))


class Power(Dimension):
    """The dimension of power."""

    name: str = "Power"
    si_symbol: str = "W"
    prefixed = True

    vec = tuple(e - t for e, t in zip(Energy.vec, Time.vec))


class Action(Dimension):
    """The dimension of action."""

    name: str = "Action"
    si_symbol: str = "J*s"
    prefixed = False

    vec = tuple(e + t for e, t in zip(Energy.vec, Time.vec))


class Charge(Dimension):
    """The dimension of electric charge."""

    name: str = "Charge"
    si_symbol: str = "C"
    prefixed = True

    vec = tuple(i + t for i, t in zip(ElectricCurrent.vec, Time.vec))


class Voltage(Dimension):
    """The dimension of electric potential difference."""

    name: str = "Voltage"
    si_symbol: str = "V"
    prefixed = True

    vec = tuple(e - q for e, q in zip(Energy.vec, Charge.vec))


class Capacitance(Dimension):
    """The dimension of capacitance."""

    name: str = "Capacitance"
    si_symbol: str = "F"
    prefixed = True

    vec = tuple(q - v for q, v in zip(Charge.vec, Voltage.vec))


class Resistance(Dimension):
    """The dimension of electric resistance."""

    name: str = "Resistance"
    si_symbol: str = "Ohm"
    prefixed = True

    vec = tuple(v - i for v, i in zip(Voltage.vec, ElectricCurrent.vec))


class ElectricField(Dimension):
    """The dimension of electric field."""

    name: str = "ElectricField"
    si_symbol: str = "V/m"
    prefixed = False

    vec = tuple(v - l for v, l in zip(Voltage.vec, Length.vec))


class MagneticInduction(Dimension):
    """The dimension of magnetic induction."""

    name: str = "MagneticInduction"
    si_symbol: str = "T"
    prefixed = True

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


def add_dimension(vec: tuple[int, ...]) -> type["Dimension"]:
    """Get a dimension class from a vector."""
    dimension = _dimension_cache.get(vec)

    if dimension is not None:
        return dimension

    n_positive = sum(1 for v in vec if v > 0)
    n_negative = sum(1 for v in vec if v < 0)

    name = ""
    si_symbol = "1"
    if n_positive:
        name = "".join(f"{d.name}{f'{v}' if v != 1 else ''}" for v, d in zip(vec, _base_dimensions) if v > 0)
        si_symbol = "*".join(
            f"{d.si_symbol}{f'^{v}' if v != 1 else ''}" for v, d in zip(vec, _base_dimensions) if v > 0
        )

    if n_negative:
        name_n = "".join(f"{d.name}{f'{-v}' if -v != 1 else ''}" for v, d in zip(vec, _base_dimensions) if v < 0)
        name += f"__Per__{name_n}"
        si_symbol_n = "*".join(
            f"{d.si_symbol}{f'^{-v}' if -v != 1 else ''}" for v, d in zip(vec, _base_dimensions) if v < 0
        )
        si_symbol += f"/({si_symbol_n})" if n_negative > 1 else f"/{si_symbol_n}"

    dimension = type(
        name,
        (Dimension,),
        {"name": name, "vec": vec, "si_symbol": si_symbol, "prefixed": False},
    )

    _dimension_cache[vec] = dimension
    return dimension


if __name__ == "__main__":
    for dim in _dimension_cache.values():
        assert add_dimension(dim.vec) is dim

    print(f"dimension cache size: {len(_dimension_cache)}")
