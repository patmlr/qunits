import math
from typing import Any, overload

from numpy import any, complexfloating, floating, integer, number
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
    find_dimension,
)
from qunits.prefix import PREFIX_DICT_EXP

type int_like = integer | int
type scalar = int | integer | float | floating
type complexscalar = number | scalar | complex | complexfloating
type numeric = complexscalar | NDArray[Any]

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


_unit_cache: dict[tuple[bytes, float, float], "Unit"] = {}


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
            dim_vec = self.unit.d.vec - other.unit.d.vec
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            return Quantity(self.value + other.value * other.unit.prefix / self.unit.prefix, self.unit)

        return Quantity(self.value + other, self.unit)

    @overload
    def __radd__(self, other: scalar) -> "Quantity[T]": ...
    
    @overload
    def __radd__[T_: scalar](self, other: "Quantity[T_]") -> "Quantity[T]": ...

    @overload
    def __radd__(self, other: "Quantity[NDArray[Any]]") -> "Quantity[NDArray[Any]]": ...

    def __radd__(self, other):
        return self.__add__(other)

    # def __sub__[T_: numeric](self, other: "Quantity[T_]") -> "Quantity[T_]":
    #     dim_vec = self.unit.d.vec - other.unit.d.vec
    #     if any(dim_vec):
    #         raise ValueError("Dimension mismatch")

    #     return Quantity(self.value - other.value * other.unit.prefix / self.unit.prefix, self.unit)

    # def __mul__(self, other):
    #     if isinstance(other, Quantity):
    #         return Quantity(self.value * other.value, self.unit * other.unit)
    #     else:
    #         return Quantity(self.value * other, self.unit)

    # def __truediv__(self, other):
    #     if isinstance(other, Quantity):
    #         return Quantity(self.value / other.value, self.unit / other.unit)
    #     elif isinstance(other, Unit):
    #         return Quantity(self.value, self.unit / other)
    #     else:
    #         return Quantity(self.value / other, self.unit)


class Unit:
    __array_priority__ = 1000
    _cache: dict = _unit_cache

    def __new__(cls, factor: float = 1.0, prefix: float = 1.0, dimension: type[Dimension] | None = None) -> "Unit":
        if dimension is None:
            dimension = Dimensionless

        key = (dimension.vec.tobytes(), factor, prefix)
        if key in cls._cache:
            return cls._cache[key]
        
        instance = super().__new__(cls)
        cls._cache[key] = instance
        return instance

    def __init__(self, factor: float = 1.0, prefix: float = 1.0, dimension: type[Dimension] | None = None) -> None:
        """The base class for units.

        Args:
            factor: The factor by which the unit is multiplied (e.g., 1 for Tesla, 1e-4 for Gauss).
            prefix: The prefix associated with the unit (e.g., 1e3 for kilo, 1e-3 for milli).
            dimension: The dimension of the unit (e.g., Length, Mass, Time).
        """
        self.factor = factor
        self.prefix = prefix
        if dimension is None:
            dimension = Dimensionless
        self.dimension = dimension

    @property
    def dim(self) -> type[Dimension]:
        return self.dimension

    @property
    def d(self) -> type[Dimension]:
        return self.dimension

    def si(self) -> "Unit":
        """Convert the unit to its SI equivalent."""
        return Unit(self.factor * self.prefix, dimension=self.dim)

    def __repr__(self) -> str:
        return f"Unit(factor={self.factor: .1e}, prefix={self.prefix: .1e}, dimension={self.dim.name})"

    def __str__(self) -> str:
        exp = int(math.log10(self.prefix))
        symbol = PREFIX_DICT_EXP.get(exp)
        return f"{symbol}{self.dim.si_symbol}"

    @overload
    def __mul__[T: scalar](self, other: T) -> Quantity[T]: ...

    @overload
    def __mul__(self, other: NDArray[Any]) -> Quantity[NDArray[Any]]: ...

    @overload
    def __mul__(self, other: "Unit") -> "Unit": ...

    def __mul__(self, other):
        """Multiply two units."""
        if isinstance(other, Unit):
            dim_vec = self.d.vec + other.d.vec
            dimension = find_dimension(dim_vec)
            if dimension is None:
                dim_name = f"{self.d.name}{other.d.name}"
                dimension = type(
                    dim_name,
                    (Dimension,),
                    {"name": dim_name, "vec": dim_vec, "si_symbol": f"{self.d.si_symbol}*{other.d.si_symbol}"},
                )

            factor = self.factor * other.factor
            prefix = self.prefix * other.prefix

            key = (dim_vec.tobytes(), factor, prefix)
            if key in self._cache:
                return self._cache[key]

            unit = Unit(factor=factor, prefix=prefix, dimension=dimension)
            self._cache[key] = unit
            return unit

        return Quantity(other, self)

    @overload
    def __rmul__[T: scalar](self, other: T) -> Quantity[T]: ...

    @overload
    def __rmul__(self, other: NDArray[Any]) -> Quantity[NDArray[Any]]: ...

    @overload
    def __rmul__(self, other: "Unit") -> "Unit": ...

    def __rmul__(self, other):
        """Multiply two units."""
        return self.__mul__(other)

    @overload
    def __truediv__[T: scalar](self, other: T) -> Quantity[T]: ...

    @overload
    def __truediv__(self, other: NDArray[Any]) -> Quantity[NDArray[Any]]: ...

    @overload
    def __truediv__(self, other: "Unit") -> "Unit": ...

    def __truediv__(self, other):
        if isinstance(other, Unit):
            dim_vec = self.d.vec - other.d.vec
            dimension = find_dimension(dim_vec)
            if dimension is None:
                dim_name = f"{self.d.name}Per{other.d.name}"
                dimension = type(
                    dim_name,
                    (Dimension,),
                    {"name": dim_name, "vec": dim_vec, "si_symbol": f"{self.d.si_symbol}/{other.d.si_symbol}"},
                )

            factor = self.factor / other.factor
            prefix = self.prefix / other.prefix

            key = (dim_vec.tobytes(), factor, prefix)
            if key in self._cache:
                return self._cache[key]

            unit = Unit(factor=factor, prefix=prefix, dimension=dimension)
            self._cache[key] = unit
            return unit

        return Quantity(other, self)

    @overload
    def __rtruediv__[T: scalar](self, other: T) -> Quantity[T]: ...

    @overload
    def __rtruediv__(self, other: NDArray[Any]) -> Quantity[NDArray[Any]]: ...

    @overload
    def __rtruediv__(self, other: "Unit") -> "Unit": ...

    def __rtruediv__(self, other):
        """Divide two units."""
        return self.__truediv__(other)

    def __pow__(self, power: int_like) -> "Unit":
        dim_vec = self.d.vec * power
        dimension = find_dimension(dim_vec)
        if dimension is None:
            dim_name = f"{self.d.name}To{power}"
            dimension = type(
                dim_name,
                (Dimension,),
                {"name": dim_name, "vec": dim_vec, "si_symbol": f"{self.d.si_symbol}^{power}"},
            )

        factor = self.factor**power
        prefix = self.prefix**power

        key = (dim_vec.tobytes(), factor, prefix)
        if key in self._cache:
            return self._cache[key]

        unit = Unit(factor=factor, prefix=prefix, dimension=dimension)
        self._cache[key] = unit
        return unit
