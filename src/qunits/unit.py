from typing import Any, Protocol, overload, runtime_checkable

from qunits.dimension import (
    AmountOfSubstance,
    Dimension,
    ElectricCurrent,
    Length,
    LuminousIntensity,
    Mass,
    Temperature,
    Time,
)

SYMBOLS = {
    "m": Length,
    "g": Mass,
    "s": Time,
    "A": ElectricCurrent,
    "K": Temperature,
    "mol": AmountOfSubstance,
    "cd": LuminousIntensity,
}

SYMBOL_FACTORS: dict[str, float] = {
    "m": 1.0,
    "g": 1.0,
    "s": 1.0,
    "A": 1.0,
    "K": 1.0,
    "mol": 1.0,
    "cd": 1.0,
}


@runtime_checkable
class SupportsMul[T](Protocol):
    def __mul__(self, other: Any) -> T: ...


class Quantity[T: object, D: Dimension]:
    """The base class for quantities."""

    def __init__(self, value: T, unit: "Unit[D]") -> None:
        """Initialize a quantity with a value and a unit.

        Args:
            value: The value of the quantity.
            unit: The unit of the quantity.
        """
        self.value = value
        self.unit = unit


class Unit[D: Dimension]:
    def __init__(self, factor: float = 1.0, prefix: float = 1.0) -> None:
        """The base class for units.

        Args:
            factor: The factor by which the unit is multiplied (e.g., 1 for meter, 0.001 for millimeter).
            prefix: The prefix associated with the unit (e.g., kilo, milli).
        """
        self.factor = factor
        self.prefix = prefix

    def si(self) -> "Unit[D]":
        """Convert the unit to its SI equivalent."""
        return Unit(self.factor * self.prefix)

    def __repr__(self) -> str:
        return f"Unit[{self.__class__.__name__}](factor={self.factor: .1e}, prefix={self.prefix: .1e})"

    def __str__(self) -> str:
        return f"{self.factor * self.prefix: .1e}"

    @overload
    def __mul__[T](self, other: SupportsMul[T]) -> Quantity[T, D]: ...

    @overload
    def __mul__(self, other: "Unit[Any]") -> "Unit[Any]": ...

    def __mul__(self, other):
        """Multiply two units."""
        if isinstance(other, Unit):
            return Unit()
        return Quantity(other, self)
