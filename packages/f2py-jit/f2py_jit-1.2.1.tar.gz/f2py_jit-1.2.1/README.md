f2py-jit
==================

[![pypi](https://img.shields.io/pypi/v/f2py-jit.svg)](https://pypi.python.org/pypi/f2py-jit/)
[![version](https://img.shields.io/pypi/pyversions/f2py-jit.svg)](https://pypi.python.org/pypi/f2py-jit/)
[![license](https://img.shields.io/pypi/l/f2py-jit.svg)](https://en.wikipedia.org/wiki/GNU_General_Public_License)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fframagit.org%2Fcoslo%2Ff2py-jit/HEAD?labpath=docs%2Findex.ipynb)
[![pipeline status](https://framagit.org/coslo/f2py-jit/badges/master/pipeline.svg)](https://framagit.org/coslo/f2py-jit/-/commits/master)
[![coverage report](https://framagit.org/coslo/f2py-jit/badges/master/coverage.svg)](https://framagit.org/coslo/f2py-jit/-/commits/master)

Just-in-time compilation of Fortran code in Python via [f2py](https://numpy.org/doc/stable/f2py/).

Check out the [documentation](https://coslo.frama.io/f2py-jit/) for full details.

Quick start
-----------

Start from a piece of Fortran `code.f90`
```fortran
subroutine hello()
  print*, "Hello world!"
end subroutine
```

Compile the code, import it and execute it
```python
from f2py_jit import jit
f90 = jit('code.f90')
f90.hello()
```

Do the same but from a python string containing the source block
```python
source = """
subroutine hello()
  print*, "Hello world!"
end subroutine
"""
f90 = jit(source)
f90.hello()
```

If the Fortran source contains multiple subroutines calling each other, `f2py` will not perform interprocedural optimizations (at least not by default). `f2py_jit` can inline the source code before compiling it, and you will get a [performace boost](https://coslo.frama.io/f2py-jit/tutorial/#performance) [**This feature is experimental**]
```python
f90 = jit('code.f90', inline=True)
```

Features
--------
- Compilation of Fortran source blocks as Python strings
- Caching of module builds across executions
- Support for Fortran derived types via f90wrap
- Inlining to improve performance (experimental)

Dependencies
------------

- `numpy`
- Fortran compiler (ex. `gfortran`)

The package currently supports Python versions from 3.7 to 3.13. 

Note that Python versions >= 3.12 will use the `meson` backend to build Fortran extensions, which has slower build times than `distutils` (used by default in versions < 3.12).

Installation
------------
From pip
```
pip install f2py-jit
```

To install the package with support for derived types (courtesy of [f90wrap](https://github.com/jameskermode/f90wrap)
```
pip install f2py-jit[types]
```
Note that this requires Python >= 3.8.

From source
```
git clone https://framagit.org/coslo/f2py-jit.git
cd f2py_jit
pip install .
```

Credits
-------
Part of this code is adapted from `numpy.f2py` module by Pearu Peterson, in accordance with the NumPy license.

Authors
-------
Daniele Coslovich: https://www.units.it/daniele.coslovich/
