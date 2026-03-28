import math
from typing import overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

from qunits.dimension import (
    Dimension,
    Dimensionless,
    add_dimension,
)
from qunits.prefix import PREFIX_DICT_EXP

__all__ = ["Quantity", "Unit"]


type int_like = int | np.integer
type float_like = float | np.floating
type scalar = int_like | float_like | NDArray[np.integer | np.floating]
type array_like = ArrayLike

UNIT_SYSTEMS = {"si"}

_unit_cache: dict[tuple[tuple[int, ...], float], "Unit"] = {}


class Unit:
    """The base class for units."""

    __array_priority__ = 1000

    def __new__(
        cls,
        scale: scalar = 1.0,
        dimension: type[Dimension] = Dimensionless,
        symbol: str | None = None,
        prefix_exp: int | None = None,
    ) -> "Unit":
        key = (dimension.vec, float(scale))
        return _unit_cache.setdefault(key, super().__new__(cls))

    def __init__(
        self,
        scale: scalar = 1.0,
        dimension: type[Dimension] = Dimensionless,
        symbol: str | None = None,
        prefix_exp: int | None = None,
    ) -> None:
        """The base class for units.

        Args:
            scale: The scale by which the unit is multiplied (e.g., 1 for Tesla, 1e-4 for Gauss).
            dimension: The dimension of the unit (e.g., Length, Mass, Time).
            symbol: The symbol of the unit (e.g., "m" for meter, "s" for second).
            prefix_exp: The exponent of the prefix (e.g., -3 for milli, 3 for kilo).
        """
        self.scale = float(scale)
        self.dimension = dimension

        if not hasattr(self, "symbol"):
            self.symbol = symbol
        if not hasattr(self, "prefix_exp"):
            self.prefix_exp = prefix_exp

    @property
    def dim(self) -> type[Dimension]:
        return self.dimension

    @property
    def d(self) -> type[Dimension]:
        return self.dimension

    def to(self, unit: "Unit | str") -> "Quantity":
        """Convert the unit into a `Unit` in the target unit (system).

        Args:
            unit: The target unit as a `Unit` instance (e.g., `u.m`),
                or the name of the target unit system (e.g., `"si"`).

            Returns:
                A `Quantity` instance representing the converted unit in the target unit (system).
        """
        if isinstance(unit, str):
            if unit.lower() == "si":
                return self.si()

            raise ValueError(
                f"Unknown unit system: {unit}. Please use one of {UNIT_SYSTEMS},"
                f" or a valid `Unit` instance, such as `u.m`."
            )

        if isinstance(unit, Unit):
            dim_vec = tuple(a - b for a, b in zip(unit.d.vec, self.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            return Quantity(self.scale / unit.scale, unit)

        raise TypeError(
            f"Invalid type of `unit`: {type(unit)}. Please use a `str` from the available unit systems {UNIT_SYSTEMS},"
            f" or a valid `Unit` instance, such as `u.m`."
        )

    def si(self) -> "Quantity":
        """Convert the unit into a `Quantity` in SI units."""
        if self.scale == 1.0:
            return Quantity(1.0, self)

        return Quantity(self.scale, Unit(1.0, dimension=self.d, symbol=self.d.si_symbol, prefix_exp=0))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.scale:.1e}, {self.d.name})"

    def __str__(self) -> str:
        if self.d.prefixed:
            prefix_exp = math.log10(self.scale)

            if self.prefix_exp is None:
                if prefix_exp.is_integer() and int(prefix_exp) in PREFIX_DICT_EXP:
                    self.prefix_exp = int(prefix_exp)

                if self.prefix_exp is None:
                    return self.__repr__()

            prefix = PREFIX_DICT_EXP.get(self.prefix_exp, "?")
            if prefix == "?":
                return self.__repr__()

            if self.symbol is None:
                if prefix_exp != self.prefix_exp:
                    return self.__repr__()

                self.symbol = self.d.si_symbol

            return f"{prefix}{self.symbol}"

        if self.symbol is None:
            if self.scale != 1.0:
                return self.__repr__()

            self.symbol = self.d.si_symbol

        return self.symbol

    @overload
    def __mul__(self, other: array_like) -> "Quantity": ...

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
    def __rmul__(self, other: array_like) -> "Quantity": ...

    @overload
    def __rmul__(self, other: "Unit") -> "Unit": ...

    def __rmul__(self, other):
        """Multiply two units."""
        return self.__mul__(other)

    @overload
    def __truediv__(self, other: array_like) -> "Quantity": ...

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
    def __rtruediv__(self, other: array_like) -> "Quantity": ...

    @overload
    def __rtruediv__(self, other: "Unit") -> "Unit": ...

    def __rtruediv__(self, other):
        """Divide two units."""
        if isinstance(other, Unit):
            return other.__truediv__(self)

        dim_vec = tuple(-x for x in self.d.vec)
        dimension = add_dimension(dim_vec)

        unit = Unit(scale=1 / self.scale, dimension=dimension)
        return Quantity(other, unit)

    def __pow__(self, power: int_like) -> "Unit":
        dim_vec = tuple(x * power for x in self.d.vec)
        dimension = add_dimension(dim_vec)

        scale = self.scale**power
        return Unit(scale=scale, dimension=dimension)


class Quantity:
    """The base class for quantities."""

    __array_priority__ = 1000

    def __init__(self, value: array_like, unit: "Unit | None" = None) -> None:
        """Initialize a quantity with a value and a unit.

        Args:
            value: The value of the quantity.
            unit: The unit of the quantity.
        """
        self.value = np.asarray(value, dtype=np.float64)
        if unit is None:
            unit = Unit()
        self.unit = unit

    def to(self, unit: "Unit | str") -> "Quantity":
        """Convert the quantity into a `Quantity` in the target unit (system).

        Args:
            unit: The target unit as a `Unit` instance (e.g., `u.m`),
                or the name of the target unit system (e.g., `"si"`).

        Returns:
            A `Quantity` instance representing the converted quantity in the target unit (system).
        """
        q = self.unit.to(unit)
        return Quantity(self.value * q.value, q.unit)

    def si(self) -> "Quantity":
        """Convert the unit into a `Quantity` in SI units."""
        q = self.unit.si()
        return Quantity(self.value * q.value, q.unit)

    def __repr__(self) -> str:
        return f"{self.value} {self.unit}"

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    def __add__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            dim_vec = tuple(a - b for a, b in zip(u.d.vec, other.unit.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            scale = other.unit.scale / u.scale

            result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
            np.multiply(other.value, scale, out=result)
            np.add(self.value, result, out=result)

            return Quantity(result, self.unit)

        return Quantity(self.value + np.asarray(other, dtype=np.float64), self.unit)

    def __radd__(self, other: "array_like | Quantity") -> "Quantity":
        return self.__add__(other)

    def __sub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            dim_vec = tuple(a - b for a, b in zip(u.d.vec, other.unit.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            scale = other.unit.scale / u.scale
            result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
            np.multiply(other.value, scale, out=result)
            np.subtract(self.value, result, out=result)
            return Quantity(result, u)

        return Quantity(self.value - np.asarray(other, dtype=np.float64), self.unit)

    def __rsub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            dim_vec = tuple(a - b for a, b in zip(u.d.vec, other.unit.d.vec))
            if any(dim_vec):
                raise ValueError("Dimension mismatch")

            scale = other.unit.scale / u.scale
            result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
            np.multiply(other.value, scale, out=result)
            np.subtract(result, self.value, out=result)
            return Quantity(result, u)

        return Quantity(np.asarray(other, dtype=np.float64) - self.value, self.unit)

    def __mul__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit * other.unit)

        if isinstance(other, Unit):
            return Quantity(self.value, self.unit * other)

        return Quantity(self.value * np.asarray(other, dtype=np.float64), self.unit)

    def __rmul__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        return self.__mul__(other)

    def __truediv__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, self.unit / other.unit)

        if isinstance(other, Unit):
            return Quantity(self.value, self.unit / other)

        return Quantity(self.value / np.asarray(other, dtype=np.float64), self.unit)

    def __rtruediv__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(other.value / self.value, other.unit / self.unit)

        if isinstance(other, Unit):
            return Quantity(1 / self.value, other / self.unit)

        return Quantity(np.asarray(other, dtype=np.float64) / self.value, Unit() / self.unit)
