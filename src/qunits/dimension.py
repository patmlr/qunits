import numpy as np


class Dimension:
    """The base class for dimensions."""

    name: str
    si_symbol: str

    vec: np.ndarray


# Base dimensions

class Dimensionless(Dimension):
    """The dimension of dimensionless quantities."""

    name: str = "Dimensionless"
    si_symbol: str = ""

    vec = np.zeros(7, dtype=int)


class Time(Dimension):
    """The dimension of time."""

    name: str = "Time"
    si_symbol: str = "s"

    vec = np.array([1, 0, 0, 0, 0, 0, 0], dtype=int)


class Length(Dimension):
    """The dimension of length."""

    name: str = "Length"
    si_symbol: str = "m"

    vec = np.array([0, 1, 0, 0, 0, 0, 0], dtype=int)


class Mass(Dimension):
    """The dimension of mass."""

    name: str = "Mass"
    si_symbol: str = "g"

    vec = np.array([0, 0, 1, 0, 0, 0, 0], dtype=int)


class ElectricCurrent(Dimension):
    """The dimension of electric current."""

    name: str = "ElectricCurrent"
    si_symbol: str = "A"

    vec = np.array([0, 0, 0, 1, 0, 0, 0], dtype=int)


class Temperature(Dimension):
    """The dimension of temperature."""

    name: str = "Temperature"
    si_symbol: str = "K"

    vec = np.array([0, 0, 0, 0, 1, 0, 0], dtype=int)


class AmountOfSubstance(Dimension):
    """The dimension of amount of substance."""

    name: str = "AmountOfSubstance"
    si_symbol: str = "mol"

    vec = np.array([0, 0, 0, 0, 0, 1, 0], dtype=int)


class LuminousIntensity(Dimension):
    """The dimension of luminous intensity."""

    name: str = "LuminousIntensity"
    si_symbol: str = "cd"

    vec = np.array([0, 0, 0, 0, 0, 0, 1], dtype=int)


# Composite dimensions

class Velocity(Dimension):
    """The dimension of velocity."""

    name: str = "Velocity"
    si_symbol: str = "m/s"

    vec = Length.vec - Time.vec


def find_dimension(dim_vec: np.ndarray) -> type[Dimension] | None:
    """Find the dimension corresponding to a given dimension vector."""
    for dim_cls in Dimension.__subclasses__():
        if np.array_equal(dim_vec, dim_cls.vec):
            return dim_cls

    return None
