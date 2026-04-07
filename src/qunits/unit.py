import math
from typing import TYPE_CHECKING, Any, Literal, overload

import numpy as np
from numpy._core.multiarray import flagsobj
from numpy.typing import ArrayLike, NDArray

from qunits.dimension import (
    Dimension,
    Dimensionless,
    add_dimension,
)
from qunits.prefix import CONTEXT_DICT, PREFIX_DICT_EXP

if TYPE_CHECKING:
    from numpy._core._internal import _ctypes

__all__ = ["Quantity", "Unit"]


type int_like = int | np.integer
type float_like = float | np.floating
type scalar = int_like | float_like | NDArray[np.integer | np.floating]
type array_like = ArrayLike

_trigonometric_functions = {np.sin, np.cos, np.tan}
_additive_functions = {np.add, np.subtract}

UNIT_SYSTEMS = {"si"}

_unit_cache: dict[tuple[tuple[int, ...], float, str], "Unit"] = {}


class Unit:
    """The base class for units."""

    __array_priority__ = 1000

    def __new__(
        cls,
        scale: scalar = 1.0,
        dimension: type[Dimension] = Dimensionless,
        context: str = "",
        symbol: str | None = None,
        prefix_exp: int | None = None,
    ) -> "Unit":
        key = (dimension.vec, float(scale), context)
        return _unit_cache.setdefault(key, super().__new__(cls))

    def __init__(
        self,
        scale: scalar = 1.0,
        dimension: type[Dimension] = Dimensionless,
        context: str = "",
        symbol: str | None = None,
        prefix_exp: int | None = None,
    ) -> None:
        """The base class for units.

        Creating a new unit with the same `dimension` and `scale` of an existing unit
        will return the cached instance.
        The `symbol` and `prefix_exp` attributes are only used for string representation
        and are set to the first created unit.

        :param scale: The scale by which the unit is multiplied (e.g., `1.0` for Tesla, `1e-4` for Gauss).
        :param dimension: The dimension of the unit (e.g., `Length`, `Mass`, `Time`).
        :param context: The context of the unit (e.g., `""`, `"angle"`, `"solid-angle"`).
        :param symbol: The symbol of the unit (e.g., `"m"` for meter, `"s"` for second).
        :param prefix_exp: The exponent of the prefix (e.g., `-3` for milli, `3` for kilo).
        """
        self.scale = float(scale)
        self.dimension = dimension
        self.context = context

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
        """Convert the unit into a `Quantity` in the target `Unit` (system).

        :param unit: The target unit as a `Unit` instance (e.g., `u.m`),
            or the name of the target unit system (e.g., `"si"`). Available unit systems: `{"si"}`.

        :returns: (quantity) The unit converted into the target `Unit` (system).
        """
        if isinstance(unit, str):
            if unit.lower() == "si":
                return self.si()

            raise ValueError(
                f"Unknown unit system: {unit}. Please use one of {UNIT_SYSTEMS},"
                f" or a valid `Unit` instance, such as `u.m`."
            )

        if isinstance(unit, Unit):
            if unit.d != self.d:
                raise ValueError(
                    f"Dimension mismatch in unit conversion. Cannot convert from {self.d.name} to {unit.d.name}."
                )

            return Quantity(self.scale / unit.scale, unit)

        raise TypeError(
            f"Invalid type of `unit`: {type(unit)}. Please use a `str` from the available unit systems {UNIT_SYSTEMS},"
            f" or a valid `Unit` instance, such as `u.m`."
        )
    
    def to_base_units(self, system: str = "si") -> "Quantity":
        """Convert the unit into a `Quantity` in base units in the specified unit system.

        :param system: The target unit system (e.g., `"si"`). Available unit systems: `{"si"}`.

        :returns: (quantity) The unit converted into a `Quantity` in base units.
        """
        if system.lower() == "si":
            return self.si()

        raise ValueError(f"Unknown unit system: {system}. Please use one of {UNIT_SYSTEMS}.")

    def si(self) -> "Quantity":
        """Convert the unit into a `Quantity` in SI units.

        :returns: (quantity) The unit as a `Quantity` in SI units.
        """
        if self.scale == 1.0:
            return Quantity(1.0, self)

        return Quantity(
            self.scale, Unit(1.0, dimension=self.d, context=self.context, symbol=self.d.si_symbol, prefix_exp=0)
        )

    def __repr__(self) -> str:
        context_str = f', "{self.context}"' if self.context else ""
        return f"{self.__class__.__name__}({self.scale:e}, {self.d.name}{context_str})"

    def __str__(self) -> str:
        context_str = f"*{CONTEXT_DICT.get(self.context, '')}" if self.context else ""

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

            if f"*{self.symbol}" == context_str:
                context_str = ""
            return f"{prefix}{self.symbol}{context_str}"

        if self.symbol is None:
            if self.scale != 1.0:
                return self.__repr__()

            self.symbol = self.d.si_symbol

        if f"*{self.symbol}" == context_str:
            context_str = ""
        return f"{self.symbol}{context_str}"

    @overload
    def __mul__(self, other: array_like) -> "Quantity": ...

    @overload
    def __mul__(self, other: "Unit") -> "Unit": ...

    def __mul__(self, other):
        """Multiply two units."""
        if isinstance(other, Unit):
            dim_vec = tuple(a + b for a, b in zip(self.d.vec, other.d.vec))
            dimension = add_dimension(dim_vec)

            prefix_exp = None
            if self.prefix_exp is not None and other.prefix_exp is not None:
                prefix_exp = self.prefix_exp + other.prefix_exp

            context = ""
            if self.context:
                context = "" if other.context else self.context
            elif other.context:
                context = "" if self.context else other.context

            scale = self.scale * other.scale
            return Unit(scale=scale, dimension=dimension, context=context, prefix_exp=prefix_exp)

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

            prefix_exp = None
            if self.prefix_exp is not None and other.prefix_exp is not None:
                prefix_exp = self.prefix_exp - other.prefix_exp

            context = self.context if self.context and not other.context else ""

            scale = self.scale / other.scale
            return Unit(scale=scale, dimension=dimension, context=context, prefix_exp=prefix_exp)

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

        prefix_exp = None
        if self.prefix_exp is not None:
            prefix_exp = -self.prefix_exp

        unit = Unit(scale=1 / self.scale, dimension=dimension, prefix_exp=prefix_exp)
        return Quantity(other, unit)

    def __pow__(self, power: int_like) -> "Unit":
        dim_vec = tuple(x * power for x in self.d.vec)
        dimension = add_dimension(dim_vec)

        prefix_exp = None
        if self.prefix_exp is not None:
            prefix_exp = self.prefix_exp * power

        context = self.context if self.context and power == 1 else ""

        scale = self.scale**power
        return Unit(scale=scale, dimension=dimension, context=context, prefix_exp=prefix_exp)


I = Unit()


class Quantity:
    """The base class for quantities."""

    __array_priority__ = 1000

    def __init__(self, value: "array_like | Quantity", unit: "Unit | None" = None) -> None:
        """The base class for quantities.

        - Multiplying or dividing an `array_like` with a `Unit` will return a `Quantity`.
        - Multiplying or dividing a `Quantity` by a `Unit` will return a new `Quantity`
         with the same value and the combined unit.
        - Multiplying or dividing two `Quantity` instances will return a new `Quantity`
         with the combined value and the combined unit.
        - Multiplying or dividing a `Quantity` by an `array_like` will return a new `Quantity`
        with the scaled value and the same unit.

        :param value: The value of the quantity.
        :param unit: The unit of the quantity.
        """
        if isinstance(value, Quantity):
            if unit is not None:
                value = value.to(unit)
            self.value = value.value
            self.unit = value.unit
        else:
            self.value = np.asarray(value, dtype=np.float64)
            if unit is None:
                unit = I
            self.unit = unit

    def to(self, unit: "Unit | str") -> "Quantity":
        """Convert the quantity into a `Quantity` in the target `Unit` (system).

        :param unit: The target unit as a `Unit` instance (e.g., `u.m`),
            or the name of the target unit system (e.g., `"si"`). Available unit systems: `{"si"}`.

        :returns: (quantity) The quantity converted into the target `Unit` (system).
        """
        q = self.unit.to(unit)
        return Quantity(self.value * q.value, q.unit)
    
    def to_base_units(self, system: str = "si") -> "Quantity":
        """Convert the quantity into a `Quantity` in base units in the specified unit system.

        :param system: The target unit system (e.g., `"si"`). Available unit systems: `{"si"}`.

        :returns: (quantity) The quantity converted into base units.
        """
        if system.lower() == "si":
            return self.si()

        raise ValueError(f"Unknown unit system: {system}. Please use one of {UNIT_SYSTEMS}.")

    def si(self) -> "Quantity":
        """Convert the quantity into a `Quantity` in SI units.

        :returns: (quantity) The quantity converted into SI units.
        """
        q = self.unit.si()
        return Quantity(self.value * q.value, q.unit)
    
    @property
    def magnitude(self) -> NDArray[np.float64]:
        """The magnitude of the quantity, i.e., the value without the unit."""
        return self.value
    
    @property
    def m(self) -> NDArray[np.float64]:
        """The magnitude of the quantity, i.e., the value without the unit."""
        return self.value
    
    @property
    def T(self) -> "Quantity":
        return Quantity(self.value.T, self.unit)

    @property
    def data(self) -> memoryview:
        return self.value.data

    @property
    def flags(self) -> flagsobj:
        return self.value.flags

    @property
    def dtype(self) -> np.dtype[np.float64]:
        return self.value.dtype

    @property
    def size(self) -> int:
        return self.value.size

    @property
    def itemsize(self) -> int:
        return self.value.itemsize

    @property
    def nbytes(self) -> int:
        return self.value.nbytes

    @property
    def ndim(self) -> int:
        return self.value.ndim

    @property
    def shape(self) -> tuple[int, ...]:
        return self.value.shape

    @property
    def strides(self) -> tuple[int, ...]:
        return self.value.strides

    @property
    def ctypes(self) -> "_ctypes[int]":
        return self.value.ctypes

    def __repr__(self) -> str:
        return f"{self.value} {self.unit}"

    def __str__(self) -> str:
        if "Unit" in str(self.unit):
            return f"{self.value * self.unit.scale} {self.unit.si().unit}"

        return f"{self.value} {self.unit}"

    def __add__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            if u.d != other.unit.d:
                raise ValueError(
                    f"Dimension mismatch in addition. Cannot add {u.d.name} and {other.unit.d.name}."
                )

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
            if u.d != other.unit.d:
                raise ValueError(
                    f"Dimension mismatch in subtraction. Cannot subtract {u.d.name} and {other.unit.d.name}."
                )


            scale = other.unit.scale / u.scale
            result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
            np.multiply(other.value, scale, out=result)
            np.subtract(self.value, result, out=result)
            return Quantity(result, u)

        return Quantity(self.value - np.asarray(other, dtype=np.float64), self.unit)

    def __rsub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            if u.d != other.unit.d:
                raise ValueError(
                    f"Dimension mismatch in subtraction. Cannot subtract {u.d.name} and {other.unit.d.name}."
                )

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

        return Quantity(np.asarray(other, dtype=np.float64) / self.value, I / self.unit)

    def __array_ufunc__(
        self,
        ufunc: np.ufunc,
        method: Literal["__call__", "reduce", "reduceat", "accumulate", "outer", "at"],
        *inputs: Any,
        **kwargs: Any,
    ) -> "Quantity":
        if method != "__call__":
            raise NotImplementedError(f"Method {method} not supported for `numpy.{ufunc.__name__}`")

        values = [x.value if isinstance(x, Quantity) else x for x in inputs]
        units = [x.unit if isinstance(x, Quantity) else I for x in inputs]

        if ufunc in _trigonometric_functions:
            unit = units[0]
            if unit.d != Dimensionless or unit.context != "angle":
                raise TypeError(
                    'Trigonometric functions require dimensionless units with "angle" context.'
                    ' Use `u.rad` or `u.pi` for angles.'
                )

            result = ufunc(*values, **kwargs)
            return Quantity(result, unit)

        if ufunc in _additive_functions:
            u0, u1 = units
            if u0.d != u1.d:
                raise ValueError(
                    f"Dimension mismatch in {ufunc.__name__}. Cannot {ufunc.__name__} {u0.d.name} and {u1.d.name}."
                )

            result = ufunc(*values, **kwargs)
            return Quantity(result, u0)

        if ufunc is np.multiply:
            u0, u1 = units
            u = u0 * u1
            result = ufunc(*values, **kwargs)
            return Quantity(result, u)

        if ufunc is np.divide:
            u0, u1 = units
            u = u0 / u1
            result = ufunc(*values, **kwargs)
            return Quantity(result, u)

        raise NotImplementedError(f"`numpy.{ufunc.__name__}` not supported.")
