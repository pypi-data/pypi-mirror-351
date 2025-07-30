# Spruce Compiler - a work in progress

**Units system and automatic differentiation engine**
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A pre-alpha package providing symbolic automatic differentiation and dimensional analysis tools.

## Installation

```bash
pip install spruce-compiler
```

## Quick Start

```python
from spruce import Variable, diff
from spruce.units import Quantity, meter, second

# Symbolic differentiation
x = Variable('x')
expr = x**2 + 3*x
derivative = diff(expr, x)
print(f"f'(x) = {derivative}")

# Units and dimensional analysis
length = Quantity(1.0, meter)
time = Quantity(2.0, second)
velocity = length / time
print(f"Velocity: {velocity}")
```

## CLI

```bash
spruce demo      # Run demonstrations
spruce version   # Show version
```

## License

MIT 