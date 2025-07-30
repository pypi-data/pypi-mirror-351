"""
Spruce Compiler - Units system and automatic differentiation engine for physics-based audio synthesis.

This pre-alpha package provides the foundational components for physics-based musical instrument modeling:
- Dimensional analysis and units system
- Symbolic automatic differentiation engine
- Basic expression manipulation and optimization

Future versions will include the full port-Hamiltonian compilation pipeline.
"""

__version__ = "0.0.1"
__author__ = "Spruce Team"
__email__ = "sprucecompiler@gmail.com"

# Core exports
from .symbolic import Variable, Expression, diff
from .units import Unit, Quantity, DimensionalError

__all__ = [
    'Variable', 'Expression', 'diff',
    'Unit', 'Quantity', 'DimensionalError'
] 