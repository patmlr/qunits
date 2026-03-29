<h1>
<img src="https://raw.githubusercontent.com/patmlr/qunits/main/docs/assets/img/logo.svg" width="300">
</h1><hr>

[![Static Badge](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Static Badge](https://img.shields.io/badge/License-MIT-slateblue)](https://github.com/patmlr/qunits/blob/main/LICENSE)

## NOTE: Early development. Not fully functional yet.

The [_qunits_](https://pypi.org/project/qunits/) Python package provides a performant, verbose and generic physical unit system.
Tutorials and the API documentation are available on the [_Homepage_](https://patmlr.github.io/qunits/).
Additional example scripts can be found in the example folder on [_GitHub_](https://github.com/patmlr/qunits).

### Getting started

```python
from qunits import u

q = 2 * u.e  # >>> 2.0 e
v = 2e5 * u.m / u.s  # >>> 200000.0 m/s
B = 0.42 * u.mT  # >>> 0.42 mT

F = q * v * B  # >>> 2.69165674512e-17 N
```

### Dependencies

- [_NumPy_](http://www.numpy.org/)
- [_SciPy_](http://www.scipy.org/)

### Modules

- _dimension_: Contains the dimension definitions.
- _registry_: Contains the unit registry `u`.
- _unit_: Contains the `Unit` and the `Quantity` classes.
