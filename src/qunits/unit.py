from math import isclose
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
from qunits.prefix import CONTEXT_DICT, Context, ExpMap, merge_exp_maps

if TYPE_CHECKING:
    from numpy._core._internal import _ctypes

__all__ = ["Quantity", "Unit"]


type int_like = int | np.integer
"""A Python or numpy integer."""
type float_like = float | np.floating
"""A Python or numpy float."""
type scalar = int_like | float_like
"""A Python or numpy integer or float."""
type array_like = ArrayLike
"""Anything that `np.asarray` converts to an array, e.g. a number, a list or an array."""

_trigonometric_functions = {np.sin, np.cos, np.tan}
_additive_functions = {np.add, np.subtract}

_unit_cache: dict[ExpMap, "Unit"] = {}


def _cast(value: array_like) -> float | NDArray[np.float64]:
    if isinstance(value, np.ndarray):
        return value.astype(np.float64, copy=False)

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    return np.asarray(value, dtype=np.float64)


def _format(value: float | NDArray[np.float64]) -> str:
    if isinstance(value, float):
        return repr(float(f"{value:.15g}"))
    return str(value)


def _number(value: array_like, unit: "Unit") -> float | NDArray[np.float64]:
    value = _cast(value)
    return value if unit.scale == 1.0 else value / unit.scale


def _to(source: "Unit", target: "Unit | None") -> tuple[float, "Unit"]:
    if target is None:
        exp_map = source.d.si_map
        if source.context:
            exp_map = merge_exp_maps(exp_map, frozenset({(CONTEXT_DICT[source.context], 1)}), 1)
        return source.scale, _unit(1.0, exp_map, source.d, source.context)

    if isinstance(target, Unit):
        if target.d is not source.d:
            raise ValueError(
                f"Dimension mismatch in unit conversion. Cannot convert from {source.d.name} to {target.d.name}."
            )
        if target.context is not source.context:
            raise ValueError(
                f"Context mismatch in unit conversion. Cannot convert from context {source.context.name}"
                f" to context {target.context.name}."
            )

        return source.scale / target.scale, target

    raise TypeError(
        f"Invalid type of `unit`: {type(target)}. Please use a `Unit` instance, or `None` to convert to SI units."
    )


def _unit(scale: scalar, exp_map: ExpMap, dimension: type[Dimension], context: Context) -> "Unit":
    unit = _unit_cache.get(exp_map)
    if unit is not None:
        return unit

    unit = object.__new__(Unit)
    unit.scale = float(scale)
    unit.exp_map = exp_map
    unit.dimension = dimension
    unit.context = context
    return _unit_cache.setdefault(exp_map, unit)


def _mismatch(operation: str, verb: str, a: "Unit", b: "Unit") -> ValueError:
    if a.d is not b.d:
        return ValueError(f"Dimension mismatch in {operation}. Cannot {verb} {a.d.name} and {b.d.name}.")
    return ValueError(
        f"Context mismatch in {operation}. Cannot {verb} {a.d.name} with context {a.context.name}"
        f" and {b.d.name} with context {b.context.name}."
    )


class Unit:
    """
    A physical unit. Units are usually taken from the registry [`u`] and combined with `*`, `/` and `**` (integer
    powers). Multiplying a number or an array with a unit creates a [`Quantity`].

    There is exactly one unit per exponent map, so units can be compared with `is`.
    """

    __array_priority__ = 1000
    __slots__ = ("context", "dimension", "exp_map", "scale")

    context: Context
    """
    The [`Context`] of the unit. Only quantities with the same dimension and context can be added, subtracted or
    converted into each other.
    """
    dimension: type[Dimension]
    """The [`Dimension`] of the unit."""
    exp_map: ExpMap
    """
    The [`ExpMap`] of the unit, e.g. `frozenset({("m", 1), ("s", -1)})` for m/s. It identifies the unit and is how
    the unit is printed.
    """
    scale: float
    """The scale factor of the unit relative to the SI unit of its dimension, e.g. 1000.0 for km."""

    def __new__(
        cls,
        scale: scalar,
        exp_map: ExpMap,
        dimension: type[Dimension],
        context: Context,
    ) -> "Unit":
        """
        Defines a new unit. If the unit is already defined with the same scale, dimension and context, the existing
        unit is returned.

        :param scale: The scale factor of the unit relative to the SI unit of its dimension, e.g. 1000.0 for km.
        :param exp_map: The exponent map of the unit, e.g. `frozenset({("km", 1)})`.
        :param dimension: The [`Dimension`] of the unit.
        :param context: The [`Context`] of the unit.
        :raises ValueError: If a unit with the same `exp_map` but another scale, dimension or context is defined.
        """
        unit = _unit_cache.get(exp_map)
        if unit is None:
            return _unit(scale, exp_map, dimension, Context(context))

        if unit.dimension is not dimension or unit.context != context or not isclose(unit.scale, scale):
            raise ValueError(
                f"The unit {unit} is already defined with scale {unit.scale}, dimension {unit.d.name}"
                f" and context {unit.context.name}."
            )
        return unit

    @property
    def dim(self) -> type[Dimension]:
        """The [`Dimension`] of the unit, same as `dimension`."""
        return self.dimension

    @property
    def d(self) -> type[Dimension]:
        """The [`Dimension`] of the unit, same as `dimension`."""
        return self.dimension

    def to(self, unit: "Unit | None") -> "Quantity":
        """
        Convert the unit into a [`Quantity`] in the target unit, e.g. `u.km.to(u.m)` is 1000.0 m.

        :param unit: The target unit, e.g. `u.m`, or `None` for the SI unit of the dimension.
        :returns: (quantity) The unit as a quantity in the target unit.
        :raises ValueError: If the target unit has another dimension or context.
        :raises TypeError: If `unit` is neither a [`Unit`] nor `None`.
        """
        return Quantity(*_to(self, unit))

    def to_base_units(self) -> "Quantity":
        """
        Convert the unit into a [`Quantity`] in the SI unit of its dimension, e.g. J for eV and rad for mrad.
        Same as [`Unit.si`].

        :returns: (quantity) The unit as a quantity in the SI unit of its dimension.
        """
        return self.to(None)

    def si(self) -> "Quantity":
        """
        Convert the unit into a [`Quantity`] in the SI unit of its dimension, e.g. J for eV and rad for mrad.
        Same as [`Unit.to_base_units`].

        :returns: (quantity) The unit as a quantity in the SI unit of its dimension.
        """
        return self.to_base_units()

    def __repr__(self) -> str:
        num: list[str] = []
        den: list[str] = []
        for symbol, exp in sorted(self.exp_map):
            exp_abs = abs(exp)
            factor = f"{symbol}{f'^{exp_abs}' if exp_abs != 1 else ''}"
            (num if exp > 0 else den).append(factor)

        if not num:
            num.append("1")

        if den:
            return f"{'⋅'.join(num)}/{'⋅'.join(den)}"
        return "⋅".join(num)

    @overload
    def __mul__(self, other: "Unit") -> "Unit": ...

    @overload
    def __mul__(self, other: array_like) -> "Quantity": ...

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

            return _unit(scale, exp_map, dimension, context)

        return Quantity(other, self)

    @overload
    def __rmul__(self, other: "Unit") -> "Unit": ...

    @overload
    def __rmul__(self, other: array_like) -> "Quantity": ...

    def __rmul__(self, other):
        """Multiply two units."""
        return self.__mul__(other)

    @overload
    def __truediv__(self, other: "Unit") -> "Unit": ...

    @overload
    def __truediv__(self, other: array_like) -> "Quantity": ...

    def __truediv__(self, other):
        if isinstance(other, Unit):
            scale = self.scale / other.scale

            exp_map = merge_exp_maps(self.exp_map, other.exp_map, -1)
            dimension = new_dimension(self.d, sub_dimension, other.d.vec)
            context = self.context if self.context and not other.context else Context.I

            return _unit(scale, exp_map, dimension, context)

        return Quantity(1.0 / other, self)

    @overload
    def __rtruediv__(self, other: "Unit") -> "Unit": ...

    @overload
    def __rtruediv__(self, other: array_like) -> "Quantity": ...

    def __rtruediv__(self, other):
        """Divide two units."""
        if isinstance(other, Unit):
            return other.__truediv__(self)

        scale = 1.0 / self.scale
        exp_map = merge_exp_maps(frozenset(), self.exp_map, -1)
        dimension = new_dimension(self.d, inv_dimension)

        unit = _unit(scale, exp_map, dimension, Context.I)
        return Quantity(other, unit)

    def __pow__(self, power: int_like) -> "Unit":
        scale = self.scale**power
        exp_map = frozenset((symbol, exp * power) for symbol, exp in self.exp_map)
        dimension = new_dimension(self.d, pow_dimension, int(power))

        context = self.context if self.context and power == 1 else Context.I

        return _unit(scale, exp_map, dimension, context)


I = Unit(1.0, frozenset(), Dimensionless, Context.I)


class Quantity:
    """
    A value with a [`Unit`]. The value is a float or a numpy array of floats. Quantities are usually created by
    multiplying a number or an array with a unit, e.g. `3 * u.m`, and support:

    - `+` and `-`, also in place, with quantities of the same dimension and context. The result is in the unit of the
      left operand. Numbers and arrays can only be added to and subtracted from dimensionless quantities without
      context, e.g. `0.5 * u.m / u.km + 1`.
    - `*` and `/`, also in place, with numbers, arrays, units and quantities.
    - `np.add`, `np.subtract`, `np.multiply` and `np.divide`, and `np.sin`, `np.cos` and `np.tan` of angles, i.e.
      dimensionless quantities with the context `Context.ANGLE` such as `u.rad`.

    Other numpy functions and the methods `reduce`, `accumulate`, `outer` and `at` of the numpy functions, e.g.
    `np.sum`, raise a `NotImplementedError`.

    Printed quantities show scalar values rounded to 15 significant digits, e.g. `5.225 km` instead of
    `5.2250000000000005 km`, which hides the rounding errors of the binary floats. The values themselves are not
    rounded. Arrays are printed with the precision of numpy.
    """

    __array_priority__ = 1000
    __slots__ = ("unit", "value")

    value: float | NDArray[np.float64]
    """The value of the quantity in its unit, a float or a numpy array of floats."""
    unit: Unit
    """The [`Unit`] of the quantity."""

    def __init__(self, value: "array_like | Quantity", unit: "Unit | None" = None) -> None:
        """
        :param value: The value, a number, an array-like or a quantity. Numbers are converted to `float` and
            array-likes to numpy arrays of `float64`.
        :param unit: The unit. A quantity `value` is converted to it. Defaults to the unit of a quantity `value`, and
            to the dimensionless unit `u.I` otherwise.
        :raises ValueError: If `value` is a quantity with another dimension or context than `unit`.
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
        """
        Convert the quantity into the target unit.

        :param unit: The target unit, e.g. `u.m`, or `None` for the SI unit of the dimension.
        :returns: (quantity) The quantity in the target unit.
        :raises ValueError: If the target unit has another dimension or context.
        :raises TypeError: If `unit` is neither a [`Unit`] nor `None`.
        """
        scale, target = _to(self.unit, unit)
        return Quantity(self.value * scale, target)

    def to_base_units(self) -> "Quantity":
        """
        Convert the quantity into the SI unit of its dimension, e.g. J for eV and rad for mrad.
        Same as [`Quantity.si`].

        :returns: (quantity) The quantity in the SI unit of its dimension.
        """
        return self.to(None)

    def si(self) -> "Quantity":
        """
        Convert the quantity into the SI unit of its dimension, e.g. J for eV and rad for mrad.
        Same as [`Quantity.to_base_units`].

        :returns: (quantity) The quantity in the SI unit of its dimension.
        """
        return self.to_base_units()

    def magnitude_as(self, unit: "Unit | None") -> float | NDArray[np.float64]:
        """
        Get the value of the quantity in the target unit. Same as [`Quantity.m_as`].

        :param unit: The target unit, e.g. `u.m`, or `None` for the SI unit of the dimension.
        :returns: (magnitude) The value of the quantity in the target unit.
        :raises ValueError: If the target unit has another dimension or context.
        :raises TypeError: If `unit` is neither a [`Unit`] nor `None`.
        """
        scale, _ = _to(self.unit, unit)
        return self.value * scale

    def m_as(self, unit: "Unit | None") -> float | NDArray[np.float64]:
        """
        Get the value of the quantity in the target unit. Same as [`Quantity.magnitude_as`].

        :param unit: The target unit, e.g. `u.m`, or `None` for the SI unit of the dimension.
        :returns: (magnitude) The value of the quantity in the target unit.
        :raises ValueError: If the target unit has another dimension or context.
        :raises TypeError: If `unit` is neither a [`Unit`] nor `None`.
        """
        return self.magnitude_as(unit)

    @property
    def magnitude(self) -> float | NDArray[np.float64]:
        """The value of the quantity in its unit, same as `value`."""
        return self.value

    @property
    def m(self) -> float | NDArray[np.float64]:
        """The value of the quantity in its unit, same as `value`."""
        return self.value

    @property
    def T(self) -> "Quantity":
        """The quantity with the transposed array value. A quantity with a scalar value is returned unchanged."""
        if isinstance(self.value, np.ndarray):
            return Quantity(self.value.T, self.unit)
        return self

    @property
    def data(self) -> memoryview:
        """A `memoryview` of the array value. Raises a `NotImplementedError` for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.data
        raise NotImplementedError("The `data` property is only available for `Quantity` instances with array values.")

    @property
    def flags(self) -> flagsobj:
        """The memory layout flags of the array value. Raises a `NotImplementedError` for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.flags
        raise NotImplementedError("The `flags` property is only available for `Quantity` instances with array values.")

    @property
    def dtype(self) -> np.dtype[np.float64]:
        """The data type of the value, `float64`."""
        if isinstance(self.value, np.ndarray):
            return self.value.dtype
        return np.dtype(np.float64)

    @property
    def size(self) -> int:
        """The number of elements of the value, 1 for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.size
        return 1

    @property
    def itemsize(self) -> int:
        """The size of one element of the value in bytes."""
        if isinstance(self.value, np.ndarray):
            return self.value.itemsize
        return np.dtype(np.float64).itemsize

    @property
    def nbytes(self) -> int:
        """The size of all elements of the value in bytes."""
        if isinstance(self.value, np.ndarray):
            return self.value.nbytes
        return np.dtype(np.float64).itemsize

    @property
    def ndim(self) -> int:
        """The number of array dimensions of the value, 0 for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.ndim
        return 0

    @property
    def shape(self) -> tuple[int, ...]:
        """The shape of the value, `()` for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.shape
        return ()

    @property
    def strides(self) -> tuple[int, ...]:
        """The strides of the array value, `()` for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.strides
        return ()

    @property
    def ctypes(self) -> "_ctypes[int]":
        """The ctypes interface of the array value. Raises a `NotImplementedError` for a scalar value."""
        if isinstance(self.value, np.ndarray):
            return self.value.ctypes
        raise NotImplementedError("The `ctypes` property is only available for `Quantity` instances with array values.")

    def __repr__(self) -> str:
        return f"{_format(self.value)} {self.unit}"

    def __str__(self) -> str:
        if "Unit" in str(self.unit):
            return f"{_format(self.value * self.unit.scale)} {self.unit.si().unit}"

        return f"{_format(self.value)} {self.unit}"

    def __add__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            v = other.unit
            if u.d is not v.d or u.context is not v.context:
                raise _mismatch("addition", "add", u, v)

            scale = v.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.add(self.value, result, out=result)
                return Quantity(result, u)
            return Quantity(self.value + other.value * scale, self.unit)

        u = self.unit
        if u.d is not Dimensionless or u.context:
            raise _mismatch("addition", "add", u, I)
        return Quantity(self.value + _number(other, u), u)

    def __radd__(self, other: "array_like | Quantity") -> "Quantity":
        return self.__add__(other)

    def __iadd__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            v = other.unit
            if u.d is not v.d or u.context is not v.context:
                raise _mismatch("addition", "add", u, v)

            scale = v.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.add(self.value, result, out=self.value)
            else:
                self.value += other.value * scale

            return self

        u = self.unit
        if u.d is not Dimensionless or u.context:
            raise _mismatch("addition", "add", u, I)
        self.value += _number(other, u)
        return self

    def __sub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            v = other.unit
            if u.d is not v.d or u.context is not v.context:
                raise _mismatch("subtraction", "subtract", u, v)

            scale = v.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.subtract(self.value, result, out=result)
                return Quantity(result, u)
            return Quantity(self.value - other.value * scale, u)

        u = self.unit
        if u.d is not Dimensionless or u.context:
            raise _mismatch("subtraction", "subtract", u, I)
        return Quantity(self.value - _number(other, u), u)

    def __rsub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            v = other.unit
            if u.d is not v.d or u.context is not v.context:
                raise _mismatch("subtraction", "subtract", u, v)

            scale = v.scale / u.scale

            if isinstance(self.value, np.ndarray) and isinstance(other.value, np.ndarray):
                result = np.empty_like(self.value if len(self.value.shape) >= len(other.value.shape) else other.value)
                np.multiply(other.value, scale, out=result)
                np.subtract(result, self.value, out=result)
                return Quantity(result, u)
            return Quantity(other.value * scale - self.value, u)

        u = self.unit
        if u.d is not Dimensionless or u.context:
            raise _mismatch("subtraction", "subtract", I, u)
        return Quantity(_number(other, u) - self.value, u)

    def __isub__(self, other: "array_like | Quantity") -> "Quantity":
        if isinstance(other, Quantity):
            u = self.unit
            v = other.unit
            if u.d is not v.d or u.context is not v.context:
                raise _mismatch("subtraction", "subtract", u, v)

            scale = v.scale / u.scale
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

        u = self.unit
        if u.d is not Dimensionless or u.context:
            raise _mismatch("subtraction", "subtract", u, I)
        self.value -= _number(other, u)
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
            if unit.d is not Dimensionless or unit.context is not Context.ANGLE:
                raise TypeError(
                    f"Trigonometric functions require dimensionless units with Context.{Context.ANGLE.name}."
                    " Use `u.rad` or `u.pi` for angles."
                )

            if unit.scale != 1.0:
                values[0] = values[0] * unit.scale
            result = _ufunc(*values, **kwargs)
            return Quantity(result, I)

        if ufunc in _additive_functions:
            u0, u1 = units
            if u0.d is not u1.d or u0.context is not u1.context:
                raise _mismatch(ufunc.__name__, ufunc.__name__, u0, u1)

            if u1.scale != u0.scale:
                values[1] = values[1] * (u1.scale / u0.scale)
                if "out" not in kwargs and isinstance(values[1], np.ndarray) and values[1].shape == np.shape(values[0]):
                    kwargs["out"] = values[1]
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
