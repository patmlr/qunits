_dimension_cache: dict[tuple[int, ...], type["Dimension"]] = {}


class Dimension:
    """The base class for dimensions."""

    name: str
    si_symbol: str

    vec: tuple[int, ...]


# Special dimensions for dimensionless quantities


class Dimensionless(Dimension):
    """The dimension of dimensionless quantities."""

    name: str = "Dimensionless"
    si_symbol: str = ""

    vec = (0, 0, 0, 0, 0, 0, 0)


_dimension_cache.setdefault(Dimensionless.vec, Dimensionless)


# Base dimensions


class Time(Dimension):
    """The dimension of time."""

    name: str = "Time"
    si_symbol: str = "s"

    vec = (1, 0, 0, 0, 0, 0, 0)


class Length(Dimension):
    """The dimension of length."""

    name: str = "Length"
    si_symbol: str = "m"

    vec = (0, 1, 0, 0, 0, 0, 0)


class Mass(Dimension):
    """The dimension of mass."""

    name: str = "Mass"
    si_symbol: str = "g"

    vec = (0, 0, 1, 0, 0, 0, 0)


class ElectricCurrent(Dimension):
    """The dimension of electric current."""

    name: str = "ElectricCurrent"
    si_symbol: str = "A"

    vec = (0, 0, 0, 1, 0, 0, 0)


class Temperature(Dimension):
    """The dimension of temperature."""

    name: str = "Temperature"
    si_symbol: str = "K"

    vec = (0, 0, 0, 0, 1, 0, 0)


class AmountOfSubstance(Dimension):
    """The dimension of amount of substance."""

    name: str = "AmountOfSubstance"
    si_symbol: str = "mol"

    vec = (0, 0, 0, 0, 0, 1, 0)


class LuminousIntensity(Dimension):
    """The dimension of luminous intensity."""

    name: str = "LuminousIntensity"
    si_symbol: str = "cd"

    vec = (0, 0, 0, 0, 0, 0, 1)


_base_dimensions = (Time, Length, Mass, ElectricCurrent, Temperature, AmountOfSubstance, LuminousIntensity)

for _b in _base_dimensions:
    _dimension_cache.setdefault(_b.vec, _b)


# Composite dimensions


class Velocity(Dimension):
    """The dimension of velocity."""

    name: str = "Velocity"
    si_symbol: str = "m/s"

    vec = tuple(l - t for l, t in zip(Length.vec, Time.vec))


_composite_dimensions = (Velocity,)

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
        name = "".join(f"{d.name}{v}" for v, d in zip(vec, _base_dimensions) if v > 0)
        si_symbol = "*".join(f"{d.si_symbol}^{v}" for v, d in zip(vec, _base_dimensions) if v > 0)

    if n_negative:
        name_n = "".join(f"{d.name}{-v}" for v, d in zip(vec, _base_dimensions) if v < 0)
        name += f"_Per_{name_n}"
        si_symbol_n = "*".join(f"{d.si_symbol}^{-v}" for v, d in zip(vec, _base_dimensions) if v < 0)
        si_symbol += f"/({si_symbol_n})" if n_negative > 1 else f"/{si_symbol_n}"

    dimension = type(
        name,
        (Dimension,),
        {"name": name, "vec": vec, "si_symbol": si_symbol},
    )

    _dimension_cache[vec] = dimension
    return dimension
