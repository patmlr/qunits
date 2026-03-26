from typing import Any, overload

from numpy import any, floating, integer
from numpy.typing import NDArray

from qunits.dimension import (
    AmountOfSubstance,
    Dimension,
    Dimensionless,
    ElectricCurrent,
    Length,
    LuminousIntensity,
    Mass,
    Temperature,
    Time,
    add_dimension,
)
from qunits.prefix import PREFIX_DICT_EXP

type int_like = int | integer
type float_like = float | floating
type scalar = int_like | float_like
type numeric = scalar | NDArray[Any]

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


_unit_cache: dict[tuple[tuple[int, ...], float], "Unit"] = {}


class Unit:
    """The base class for units."""

    __array_priority__ = 1000

    def __new__(
        cls,
        scale: float = 1.0,
        dimension: type[Dimension] = Dimensionless,
        symbol: str | None = None,
        prefix_exp: int = 0,
    ) -> "Unit":
        key = (dimension.vec, scale)
        return _unit_cache.setdefault(key, super().__new__(cls))

    def __init__(
        self,
        scale: float = 1.0,
        dimension: type[Dimension] = Dimensionless,
        symbol: str | None = None,
        prefix_exp: int = 0,
    ) -> None:
        """The base class for units.

        Args:
            scale: The scale by which the unit is multiplied (e.g., 1 for Tesla, 1e-4 for Gauss).
            dimension: The dimension of the unit (e.g., Length, Mass, Time).
            symbol: The symbol of the unit (e.g., "m" for meter, "s" for second).
            prefix_exp: The exponent of the prefix (e.g., 3 for kilo, -3 for milli).
        """
        self.scale = scale
        self.dimension = dimension

        if symbol is None:
            symbol = dimension.si_symbol if scale == 1.0 else "?"
        self.symbol = symbol

        self.prefix_exp = prefix_exp

    @property
    def dim(self) -> type[Dimension]:
        return self.dimension

    @property
    def d(self) -> type[Dimension]:
        return self.dimension

    def si(self) -> "Unit":
        """Convert the unit to its SI equivalent."""
        return Unit(self.scale, dimension=self.d, symbol=self.symbol)

    def __repr__(self) -> str:
        return f"Unit({self.scale: .1e}, {self.d.name})"

    def __str__(self) -> str:
        prefix = PREFIX_DICT_EXP.get(self.prefix_exp, "")

        if self.symbol == "?":
            return f"{prefix}:{self.__repr__()}"

        return prefix + self.symbol

    @overload
    def __mul__[T: scalar](self, other: T) -> "Quantity[T]": ...

    @overload
    def __mul__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __mul__(self, other: "Unit") -> "Unit": ...

    def __mul__(self, other):
        """Multiply two units."""
        if isinstance(other, Unit):
            dim_vec = tuple(a + b for a, b in zip(self.d.vec, other.d.vec))
            dimension = add_dimension(dim_vec)

            scale = self.scale * other.scale
            return Unit(scale=scale, dimension=dimension)

        return Quantity(other, self)

    @overload
    def __rmul__[T: scalar](self, other: T) -> "Quantity[T]": ...

    @overload
    def __rmul__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __rmul__(self, other: "Unit") -> "Unit": ...

    def __rmul__(self, other):
        """Multiply two units."""
        return self.__mul__(other)

    @overload
    def __truediv__[T: scalar](self, other: T) -> "Quantity[T]": ...

    @overload
    def __truediv__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __truediv__(self, other: "Unit") -> "Unit": ...

    def __truediv__(self, other):
        if isinstance(other, Unit):
            dim_vec = tuple(a - b for a, b in zip(self.d.vec, other.d.vec))
            dimension = add_dimension(dim_vec)

            scale = self.scale / other.scale
            return Unit(scale=scale, dimension=dimension)

        return Quantity(other, self)

    @overload
    def __rtruediv__[T: scalar](self, other: T) -> "Quantity[T]": ...

    @overload
    def __rtruediv__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __rtruediv__(self, other: "Unit") -> "Unit": ...

    def __rtruediv__(self, other):
        """Divide two units."""
        if isinstance(other, Unit):
            dim_vec = tuple(a - b for a, b in zip(other.d.vec, self.d.vec))
            dimension = add_dimension(dim_vec)

            scale = other.scale / self.scale
            return Unit(scale=scale, dimension=dimension)

        dim_vec = tuple(-x for x in self.d.vec)
        dimension = add_dimension(dim_vec)

        unit = Unit(scale=1 / self.scale, dimension=dimension)
        return Quantity(other, unit)

    def __pow__(self, power: int_like) -> "Unit":
        dim_vec = tuple(x * power for x in self.d.vec)
        dimension = add_dimension(dim_vec)

        scale = self.scale**power
        return Unit(scale=scale, dimension=dimension)


class Quantity[T: numeric]:
    """The base class for quantities."""

    __array_priority__ = 1000

    def __init__(self, value: T, unit: "Unit | None" = None) -> None:
        """Initialize a quantity with a value and a unit.

        Args:
            value: The value of the quantity.
            unit: The unit of the quantity.
        """
        self.value = value
        if unit is None:
            unit = Unit()
        self.unit = unit

    def __repr__(self) -> str:
        return f"{self.value} {self.unit}"

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    @overload
    def __add__(self, other: scalar) -> "Quantity[T]": ...

    @overload
    def __add__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __add__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    def __add__(self, other):
        if isinstance(other, Quantity):
            u = self.unit
            dim_vec = tuple(a - b for a, b in zip(u.d.vec, other.unit.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            scale = other.unit.scale / u.scale
            return Quantity(self.value + other.value * scale, self.unit)

        return Quantity(self.value + other, self.unit)

    @overload
    def __radd__(self, other: scalar) -> "Quantity[T]": ...

    @overload
    def __radd__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __radd__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    def __radd__(self, other):
        return self.__add__(other)

    @overload
    def __sub__(self, other: scalar) -> "Quantity[T]": ...

    @overload
    def __sub__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __sub__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    def __sub__(self, other):
        if isinstance(other, Quantity):
            u = self.unit
            dim_vec = tuple(a - b for a, b in zip(u.d.vec, other.unit.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            scale = other.unit.scale / u.scale
            return Quantity(self.value - other.value * scale, u)

        return Quantity(self.value - other, self.unit)

    @overload
    def __rsub__(self, other: scalar) -> "Quantity[T]": ...

    @overload
    def __rsub__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __rsub__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    def __rsub__(self, other):
        if isinstance(other, Quantity):
            u = self.unit
            dim_vec = tuple(a - b for a, b in zip(u.d.vec, other.unit.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            scale = other.unit.scale / u.scale
            return Quantity(other.value * scale - self.value, u)

        return Quantity(other - self.value, self.unit)

    @overload
    def __mul__(self, other: scalar) -> "Quantity[float]": ...

    @overload
    def __mul__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __mul__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __mul__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    @overload
    def __mul__(self, other: "Unit") -> "Quantity[T]": ...

    def __mul__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit * other.unit)

        if isinstance(other, Unit):
            return Quantity(self.value, self.unit * other)

        return Quantity(self.value * other, self.unit)

    @overload
    def __rmul__(self, other: scalar) -> "Quantity[float]": ...

    @overload
    def __rmul__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __rmul__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __rmul__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    @overload
    def __rmul__(self, other: "Unit") -> "Quantity[T]": ...

    def __rmul__(self, other):
        return self.__mul__(other)

    @overload
    def __truediv__(self, other: scalar) -> "Quantity[float]": ...

    @overload
    def __truediv__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __truediv__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __truediv__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    @overload
    def __truediv__(self, other: "Unit") -> "Quantity[T]": ...

    def __truediv__(self, other):
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, self.unit / other.unit)

        if isinstance(other, Unit):
            return Quantity(self.value, self.unit / other)

        return Quantity(self.value / other, self.unit)

    @overload
    def __rtruediv__(self, other: scalar) -> "Quantity[float]": ...

    @overload
    def __rtruediv__(self, other: NDArray[Any]) -> "Quantity[NDArray[Any]]": ...

    @overload
    def __rtruediv__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __rtruediv__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    @overload
    def __rtruediv__(self, other: "Unit") -> "Quantity[T]": ...

    def __rtruediv__(self, other):
        if isinstance(other, Quantity):
            return Quantity(other.value / self.value, other.unit / self.unit)

        if isinstance(other, Unit):
            return Quantity(1 / self.value, other / self.unit)

        return Quantity(other / self.value, Unit() / self.unit)
