from typing import TYPE_CHECKING, Any, Literal, cast, overload

import numpy as np
from numpy._core.multiarray import flagsobj
from numpy.typing import ArrayLike, NDArray

from qunits.dimension import (
    Dimension,
    Dimensionless,
    add_dimension,
    inv_dimension,
    new_dimension,
    pow_dimension,
    sub_dimension,
)
from qunits.prefix import Context, ExpMap, merge_exp_maps

if TYPE_CHECKING:
    from numpy._core._internal import _ctypes

__all__ = ["Quantity", "Unit"]


type int_like = int | np.integer
type float_like = float | np.floating
type scalar = int_like | float_like
type array_like = ArrayLike

_trigonometric_functions = {np.sin, np.cos, np.tan}
_additive_functions = {np.add, np.subtract}

_unit_cache: dict[ExpMap, "Unit"] = {}


def _cast(value: array_like) -> float | NDArray[np.float64]:
    if isinstance(value, np.ndarray):
        return value.astype(np.float64, copy=False)

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    return np.asarray(value, dtype=np.float64)


def _to(_unit: "Unit", unit: "Unit | None") -> tuple[float, "Unit"]:
    if unit is None:
        return _unit.scale, Unit(1.0, _unit.d.si_map, _unit.d, _unit.context)

    if isinstance(unit, Unit):
        if unit.d != _unit.d:
            raise ValueError(
                f"Dimension mismatch in unit conversion. Cannot convert from {_unit.d.name} to {unit.d.name}."
            )

        return _unit.scale / unit.scale, unit

    raise TypeError(
        f"Invalid type of `unit`: {type(unit)}. Please use a `Unit` instance, or `None` to convert to SI base units."
    )


class Unit:
    """The base class for units."""

    __array_priority__ = 1000
    __slots__ = ("context", "dimension", "exp_map", "scale")

    context: Context
    """The context of the unit. Units with different contexts are not compatible for addition or subtraction,"""
    dimension: type[Dimension]
    exp_map: ExpMap
    scale: float

    def __new__(
        cls,
        scale: scalar,
        exp_map: ExpMap,
        dimension: type[Dimension],
        context: Context,
    ) -> "Unit":
        """Create a new `Unit` instance.
        
        :param scale: The scale factor of the unit relative to the SI base units.
        :param exp_map: The `ExpMap` of the unit.
        :param dimension: The `Dimension` of the unit.
        :param context: The `Context` of the unit.

        :returns: (unit) A new `Unit` instance with the specified properties.
        """
        unit = _unit_cache.get(exp_map)
        if unit is not None:
            return unit

        unit = super().__new__(cls)
        unit.scale = float(scale)
        unit.exp_map = exp_map
        unit.dimension = dimension
        unit.context = context
        return _unit_cache.setdefault(exp_map, unit)

    @property
    def dim(self) -> type[Dimension]:
        """The `Dimension` of the unit."""
        return self.dimension

    @property
    def d(self) -> type[Dimension]:
        """The `Dimension` of the unit."""
        return self.dimension

    def to(self, unit: "Unit | None") -> "Quantity":
        """Convert the unit into a `Quantity` in the target `Unit`.

        :param unit: The target unit as a `Unit` instance (e.g., `u.m`),
            or `None` to convert to SI base units.

        :returns: (quantity) The unit converted into the target `Unit`.
        """
        return Quantity(*_to(self, unit))

    def to_base_units(self) -> "Quantity":
        """Convert the unit into a `Quantity` in SI base units.

        :returns: (quantity) The unit converted into a `Quantity` in base units.
        """

        return self.to(None)

    def si(self) -> "Quantity":
        """Convert the unit into a `Quantity` in SI units.

        :returns: (quantity) The unit as a `Quantity` in SI units.
        """
        return self.to_base_units()

    def __repr__(self) -> str:
        num: list[str] = []
        den: list[str] = []
        for symbol, exp in self.exp_map:
            exp_abs = abs(exp)
            factor = f"{symbol}{f'^{exp_abs}' if exp_abs != 1 else ''}"
            (num if exp > 0 else den).append(factor)

        if not num:
            num.append("1")

        if den:
            return f"{'⋅'.join(num)}/{'⋅'.join(den)}"
        return "⋅".join(num)

    @overload
    def __mul__(self, other: array_like) -> "Quantity": ...

    @overload
    def __mul__(self, other: "Unit") -> "Unit": ...

    def __mul__(self, other):
        """Multiply two units."""
        if isinstance(other, Unit):
            scale = self.scale * other.scale
            exp_map = merge_exp_maps(self.exp_map, other.exp_map, 1)
            dimension = new_dimension(self.d, add_dimension, other.d.vec)

            context = Context.I
            if self.context:
                context = Context.I if other.context else self.context
            elif other.context:
                context = Context.I if self.context else other.context

            return Unit(scale, exp_map, dimension, context)

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
            scale = self.scale / other.scale

            exp_map = merge_exp_maps(self.exp_map, other.exp_map, -1)
            dimension = new_dimension(self.d, sub_dimension, other.d.vec)
            context = self.context if self.context and not other.context else Context.I

            return Unit(scale, exp_map, dimension, context)

        return Quantity(1.0 / other, self)

    @overload
    def __rtruediv__(self, other: array_like) -> "Quantity": ...

    @overload
    def __rtruediv__(self, other: "Unit") -> "Unit": ...

    def __rtruediv__(self, other):
        """Divide two units."""
        if isinstance(other, Unit):
            return other.__truediv__(self)

        scale = 1.0 / self.scale
        exp_map = merge_exp_maps(frozenset(), self.exp_map, -1)
        dimension = new_dimension(self.d, inv_dimension)

        unit = Unit(scale, exp_map, dimension, Context.I)
        return Quantity(other, unit)

    def __pow__(self, power: int_like) -> "Unit":
        scale = self.scale**power
        exp_map = frozenset((symbol, exp * power) for symbol, exp in self.exp_map)
        dimension = new_dimension(self.d, pow_dimension, int(power))

        context = self.context if self.context and power == 1 else Context.I

        return Unit(scale, exp_map, dimension, context)


I = Unit(1.0, frozenset(), Dimensionless, Context.I)


class Quantity:
    """The base class for quantities."""

    __array_priority__ = 1000
    __slots__ = ("unit", "value")

    value: float | NDArray[np.float64]
    unit: Unit

    def __init__(self, value: "array_like | Quantity", unit: "Unit | None" = None) -> None:
        """The base class for quantities with units.

        :param value: The value of the quantity.
        :param unit: The unit of the quantity.
        """
        if isinstance(value, Quantity):
            if unit is not None:
                value = value.to(unit)
            self.value = value.value
            self.unit = value.unit
        else:
            self.value = _cast(value)

            if unit is None:
                unit = I
            self.unit = unit

    def to(self, unit: "Unit | None") -> "Quantity":
        """Convert the quantity into a `Quantity` in the target `Unit`.

        :param unit: The target unit as a `Unit` instance (e.g., `u.m`),
            or `None` to convert to SI base units.

        :returns: (quantity) The quantity converted into the target `Unit`.
        """
        scale, _unit = _to(self.unit, unit)
        return Quantity(self.value * scale, _unit)

    def to_base_units(self) -> "Quantity":
        """Convert the quantity into a `Quantity` in SI base units.

        :returns: (quantity) The quantity converted into SI base units.
        """
        return self.to(None)

    def si(self) -> "Quantity":
        """Convert the quantity into a `Quantity` in SI units.

        :returns: (quantity) The quantity converted into SI units.
        """
        return self.to_base_units()

    def magnitude_as(self, unit: "Unit | None") -> float | NDArray[np.float64]:
        """Get the magnitude of the quantity in the specified unit.

        :param unit: The target unit as a `Unit` instance (e.g., `u.m`),
            or `None` to convert to SI base units.

        :returns: (magnitude) The magnitude of the quantity in the specified unit.
        """
        scale, _ = _to(self.unit, unit)
        return self.value * scale

    def m_as(self, unit: "Unit | None") -> float | NDArray[np.float64]:
        """Get the magnitude of the quantity in the specified unit.

        :param unit: The target unit as a `Unit` instance (e.g., `u.m`),
            or `None` to convert to SI base units.

        :returns: (magnitude) The magnitude of the quantity in the specified unit.
        """
        return self.magnitude_as(unit)

    @property
    def magnitude(self) -> float | NDArray[np.float64]:
        """The magnitude of the quantity, i.e., the value without the current unit."""
        return self.value

    @property
    def m(self) -> float | NDArray[np.float64]:
        """The magnitude of the quantity, i.e., the value without the current unit."""
        return self.value

    @property
    def T(self) -> "Quantity":
        """The transpose of the quantity."""
        if isinstance(self.value, np.ndarray):
            return Quantity(self.value.T, self.unit)
        return self

    @property
    def data(self) -> memoryview:
        """A `memoryview` of the data of the quantity if the value is an array."""
        if isinstance(self.value, np.ndarray):
            return self.value.data
        raise NotImplementedError("The `data` property is only available for `Quantity` instances with array values.")

    @property
    def flags(self) -> flagsobj:
        """The flags of the quantity, if the value is an array."""
        if isinstance(self.value, np.ndarray):
            return self.value.flags
        raise NotImplementedError("The `flags` property is only available for `Quantity` instances with array values.")

    @property
    def dtype(self) -> np.dtype[np.float64]:
        """The data type of the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.dtype
        return np.dtype(np.float64)

    @property
    def size(self) -> int:
        """The number of elements in the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.size
        return 1

    @property
    def itemsize(self) -> int:
        """The size in bytes of each element in the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.itemsize
        return np.dtype(np.float64).itemsize

    @property
    def nbytes(self) -> int:
        """The total number of bytes consumed by the elements of the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.nbytes
        return np.dtype(np.float64).itemsize

    @property
    def ndim(self) -> int:
        """The number of array dimensions of the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.ndim
        return 0

    @property
    def shape(self) -> tuple[int, ...]:
        """The array shape of the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.shape
        return ()

    @property
    def strides(self) -> tuple[int, ...]:
        """The strides of the quantity."""
        if isinstance(self.value, np.ndarray):
            return self.value.strides
        return ()

    @property
    def ctypes(self) -> "_ctypes[int]":
        """The ctypes of the quantity if the value is an array."""
        if isinstance(self.value, np.ndarray):
            return self.value.ctypes
        raise NotImplementedError("The `ctypes` property is only available for `Quantity` instances with array values.")

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
                raise ValueError(f"Dimension mismatch in addition. Cannot add {u.d.name} and {other.unit.d.name}.")

            scale = other.unit.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.add(self.value, result, out=result)
                return Quantity(result, u)
            return Quantity(self.value + other.value * scale, self.unit)

        return Quantity(self.value + _cast(other), self.unit)

    def __radd__(self, other: "array_like | Quantity") -> "Quantity":
        return self.__add__(other)

    def __iadd__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            if u.d != other.unit.d:
                raise ValueError(f"Dimension mismatch in addition. Cannot add {u.d.name} and {other.unit.d.name}.")

            scale = other.unit.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.add(self.value, result, out=self.value)
            else:
                self.value += other.value * scale

            return self

        self.value += _cast(other)
        return self

    def __sub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            if u.d != other.unit.d:
                raise ValueError(
                    f"Dimension mismatch in subtraction. Cannot subtract {u.d.name} and {other.unit.d.name}."
                )

            scale = other.unit.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.subtract(self.value, result, out=result)
                return Quantity(result, u)
            return Quantity(self.value - other.value * scale, u)

        return Quantity(self.value - _cast(other), self.unit)

    def __rsub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            if u.d != other.unit.d:
                raise ValueError(
                    f"Dimension mismatch in subtraction. Cannot subtract {u.d.name} and {other.unit.d.name}."
                )

            scale = other.unit.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.subtract(result, self.value, out=result)
                return Quantity(result, u)
            return Quantity(other.value * scale - self.value, u)

        return Quantity(_cast(other) - self.value, self.unit)

    def __isub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            if u.d != other.unit.d:
                raise ValueError(
                    f"Dimension mismatch in subtraction. Cannot subtract {u.d.name} and {other.unit.d.name}."
                )

            scale = other.unit.scale / u.scale
            if isinstance(self.value, float) or isinstance(other.value, float):
                self.value -= other.value * scale
                return self

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.subtract(self.value, result, out=self.value)
            else:
                self.value -= other.value * scale

            return self

        self.value -= _cast(other)
        return self

    def __mul__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit * other.unit)

        if isinstance(other, Unit):
            return Quantity(self.value, self.unit * other)

        return Quantity(self.value * _cast(other), self.unit)

    def __rmul__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        return self.__mul__(other)

    def __imul__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            self.value *= other.value
            self.unit *= other.unit
            return self

        if isinstance(other, Unit):
            self.unit *= other
            return self

        self.value *= _cast(other)
        return self

    def __truediv__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, self.unit / other.unit)

        if isinstance(other, Unit):
            return Quantity(self.value, self.unit / other)

        return Quantity(self.value / _cast(other), self.unit)

    def __rtruediv__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(other.value / self.value, other.unit / self.unit)

        if isinstance(other, Unit):
            return Quantity(1 / self.value, other / self.unit)

        return Quantity(_cast(other) / self.value, I / self.unit)

    def __itruediv__(self, other: "array_like | Unit | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            self.value /= other.value
            self.unit /= other.unit
            return self

        if isinstance(other, Unit):
            self.unit /= other
            return self

        self.value /= _cast(other)
        return self

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

        _ufunc = cast("Any", ufunc)

        if ufunc in _trigonometric_functions:
            unit = units[0]
            if unit.d != Dimensionless or unit.context != Context.ANGLE:
                raise TypeError(
                    f"Trigonometric functions require dimensionless units with Context.{Context.ANGLE.name}."
                    " Use `u.rad` or `u.pi` for angles."
                )

            result = _ufunc(*values, **kwargs)
            return Quantity(result, I)

        if ufunc in _additive_functions:
            u0, u1 = units
            if u0.d != u1.d:
                raise ValueError(
                    f"Dimension mismatch in {ufunc.__name__}. Cannot {ufunc.__name__} {u0.d.name} and {u1.d.name}."
                )

            result = _ufunc(*values, **kwargs)
            return Quantity(result, u0)

        if ufunc is np.multiply:
            u0, u1 = units
            u = u0 * u1
            result = _ufunc(*values, **kwargs)
            return Quantity(result, u)

        if ufunc is np.divide:
            u0, u1 = units
            u = u0 / u1
            result = _ufunc(*values, **kwargs)
            return Quantity(result, u)

        raise NotImplementedError(f"`numpy.{ufunc.__name__}` not supported.")
