"""
Units system and dimensional analysis for Spruce.

This module provides a comprehensive units system for physics-based modeling,
including dimensional analysis, unit conversion, and validation of physical equations.
"""

from typing import Dict, Union, Optional, Tuple
from dataclasses import dataclass
import math


class DimensionalError(Exception):
    """Raised when dimensional analysis fails."""
    pass


@dataclass(frozen=True)
class Dimension:
    """Represents the dimensional formula of a physical quantity.
    
    Uses the seven SI base dimensions:
    - length (L): meter
    - mass (M): kilogram  
    - time (T): second
    - electric_current (I): ampere
    - temperature (Θ): kelvin
    - amount (N): mole
    - luminous_intensity (J): candela
    """
    length: int = 0
    mass: int = 0
    time: int = 0
    electric_current: int = 0
    temperature: int = 0
    amount: int = 0
    luminous_intensity: int = 0
    
    def __mul__(self, other: 'Dimension') -> 'Dimension':
        """Multiply dimensions (add exponents)."""
        return Dimension(
            length=self.length + other.length,
            mass=self.mass + other.mass,
            time=self.time + other.time,
            electric_current=self.electric_current + other.electric_current,
            temperature=self.temperature + other.temperature,
            amount=self.amount + other.amount,
            luminous_intensity=self.luminous_intensity + other.luminous_intensity
        )
    
    def __truediv__(self, other: 'Dimension') -> 'Dimension':
        """Divide dimensions (subtract exponents)."""
        return Dimension(
            length=self.length - other.length,
            mass=self.mass - other.mass,
            time=self.time - other.time,
            electric_current=self.electric_current - other.electric_current,
            temperature=self.temperature - other.temperature,
            amount=self.amount - other.amount,
            luminous_intensity=self.luminous_intensity - other.luminous_intensity
        )
    
    def __pow__(self, exponent: Union[int, float]) -> 'Dimension':
        """Raise dimension to a power."""
        if isinstance(exponent, float) and not exponent.is_integer():
            # For fractional powers, check if all dimensions are divisible
            for dim_value in [self.length, self.mass, self.time, self.electric_current,
                            self.temperature, self.amount, self.luminous_intensity]:
                if dim_value != 0 and (dim_value * exponent) != int(dim_value * exponent):
                    raise DimensionalError(f"Fractional power {exponent} not valid for dimension {self}")
        
        exp_int = int(exponent) if isinstance(exponent, float) and exponent.is_integer() else exponent
        return Dimension(
            length=self.length * exp_int,
            mass=self.mass * exp_int,
            time=self.time * exp_int,
            electric_current=self.electric_current * exp_int,
            temperature=self.temperature * exp_int,
            amount=self.amount * exp_int,
            luminous_intensity=self.luminous_intensity * exp_int
        )
    
    def is_dimensionless(self) -> bool:
        """Check if this is a dimensionless quantity."""
        return all(getattr(self, field.name) == 0 for field in self.__dataclass_fields__.values())
    
    def __str__(self) -> str:
        """String representation of dimension."""
        if self.is_dimensionless():
            return "1"
        
        parts = []
        symbols = {
            'length': 'L',
            'mass': 'M', 
            'time': 'T',
            'electric_current': 'I',
            'temperature': 'Θ',
            'amount': 'N',
            'luminous_intensity': 'J'
        }
        
        for field_name, symbol in symbols.items():
            value = getattr(self, field_name)
            if value == 1:
                parts.append(symbol)
            elif value != 0:
                parts.append(f"{symbol}^{value}")
        
        return "·".join(parts) if parts else "1"


# Base dimensions
DIMENSIONLESS = Dimension()
LENGTH = Dimension(length=1)
MASS = Dimension(mass=1)
TIME = Dimension(time=1)
ELECTRIC_CURRENT = Dimension(electric_current=1)
TEMPERATURE = Dimension(temperature=1)
AMOUNT = Dimension(amount=1)
LUMINOUS_INTENSITY = Dimension(luminous_intensity=1)

# Derived dimensions commonly used in physics
AREA = LENGTH ** 2
VOLUME = LENGTH ** 3
VELOCITY = LENGTH / TIME
ACCELERATION = VELOCITY / TIME
FORCE = MASS * ACCELERATION
ENERGY = FORCE * LENGTH
POWER = ENERGY / TIME
PRESSURE = FORCE / AREA
FREQUENCY = DIMENSIONLESS / TIME
ANGULAR_FREQUENCY = FREQUENCY
DENSITY = MASS / VOLUME
MOMENTUM = MASS * VELOCITY
ANGULAR_MOMENTUM = MOMENTUM * LENGTH
TORQUE = FORCE * LENGTH
ELECTRIC_CHARGE = ELECTRIC_CURRENT * TIME
VOLTAGE = ENERGY / ELECTRIC_CHARGE
RESISTANCE = VOLTAGE / ELECTRIC_CURRENT
CAPACITANCE = ELECTRIC_CHARGE / VOLTAGE
INDUCTANCE = VOLTAGE * TIME / ELECTRIC_CURRENT
MAGNETIC_FIELD = FORCE / (ELECTRIC_CURRENT * LENGTH)


class Unit:
    """Represents a physical unit with dimension and scale factor."""
    
    def __init__(self, name: str, symbol: str, dimension: Dimension, scale: float = 1.0):
        self.name = name
        self.symbol = symbol
        self.dimension = dimension
        self.scale = scale  # Scale factor relative to SI base unit
    
    def __mul__(self, other: 'Unit') -> 'Unit':
        """Multiply units."""
        return Unit(
            name=f"{self.name}·{other.name}",
            symbol=f"{self.symbol}·{other.symbol}",
            dimension=self.dimension * other.dimension,
            scale=self.scale * other.scale
        )
    
    def __truediv__(self, other: 'Unit') -> 'Unit':
        """Divide units."""
        return Unit(
            name=f"{self.name}/{other.name}",
            symbol=f"{self.symbol}/{other.symbol}",
            dimension=self.dimension / other.dimension,
            scale=self.scale / other.scale
        )
    
    def __pow__(self, exponent: Union[int, float]) -> 'Unit':
        """Raise unit to a power."""
        return Unit(
            name=f"{self.name}^{exponent}",
            symbol=f"{self.symbol}^{exponent}",
            dimension=self.dimension ** exponent,
            scale=self.scale ** exponent
        )
    
    def is_compatible(self, other: 'Unit') -> bool:
        """Check if two units have the same dimension."""
        return self.dimension == other.dimension
    
    def conversion_factor(self, other: 'Unit') -> float:
        """Get conversion factor from this unit to another compatible unit."""
        if not self.is_compatible(other):
            raise DimensionalError(f"Cannot convert {self.symbol} to {other.symbol}: incompatible dimensions")
        return self.scale / other.scale
    
    def __str__(self) -> str:
        return self.symbol
    
    def __repr__(self) -> str:
        return f"Unit({self.name}, {self.symbol}, {self.dimension}, {self.scale})"


# SI Base Units
meter = Unit("meter", "m", LENGTH)
kilogram = Unit("kilogram", "kg", MASS)
second = Unit("second", "s", TIME)
ampere = Unit("ampere", "A", ELECTRIC_CURRENT)
kelvin = Unit("kelvin", "K", TEMPERATURE)
mole = Unit("mole", "mol", AMOUNT)
candela = Unit("candela", "cd", LUMINOUS_INTENSITY)

# Common length units
millimeter = Unit("millimeter", "mm", LENGTH, 1e-3)
centimeter = Unit("centimeter", "cm", LENGTH, 1e-2)
kilometer = Unit("kilometer", "km", LENGTH, 1e3)
inch = Unit("inch", "in", LENGTH, 0.0254)
foot = Unit("foot", "ft", LENGTH, 0.3048)

# Common mass units
gram = Unit("gram", "g", MASS, 1e-3)
pound = Unit("pound", "lb", MASS, 0.453592)

# Common time units
millisecond = Unit("millisecond", "ms", TIME, 1e-3)
microsecond = Unit("microsecond", "μs", TIME, 1e-6)
minute = Unit("minute", "min", TIME, 60)
hour = Unit("hour", "h", TIME, 3600)

# Frequency units
hertz = Unit("hertz", "Hz", FREQUENCY)
kilohertz = Unit("kilohertz", "kHz", FREQUENCY, 1e3)

# Force units
newton = Unit("newton", "N", FORCE)

# Energy units
joule = Unit("joule", "J", ENERGY)

# Power units
watt = Unit("watt", "W", POWER)

# Pressure units
pascal = Unit("pascal", "Pa", PRESSURE)

# Electrical units
volt = Unit("volt", "V", VOLTAGE)
ohm = Unit("ohm", "Ω", RESISTANCE)
farad = Unit("farad", "F", CAPACITANCE)
henry = Unit("henry", "H", INDUCTANCE)

# Dimensionless unit
dimensionless = Unit("dimensionless", "1", DIMENSIONLESS)

# Common unit aliases for convenience
m = meter
kg = kilogram
s = second
A = ampere
K = kelvin
mol = mole
cd = candela
mm = millimeter
cm = centimeter
km = kilometer
g = gram
ms = millisecond
Hz = hertz
kHz = kilohertz
N = newton
J = joule
W = watt
Pa = pascal
V = volt


class Quantity:
    """Represents a physical quantity with value and unit."""
    
    def __init__(self, value: float, unit: Unit):
        self.value = float(value)
        self.unit = unit
    
    @property
    def dimension(self) -> Dimension:
        """Get the dimension of this quantity."""
        return self.unit.dimension
    
    def to(self, target_unit: Unit) -> 'Quantity':
        """Convert to another unit."""
        if not self.unit.is_compatible(target_unit):
            raise DimensionalError(
                f"Cannot convert {self.unit.symbol} to {target_unit.symbol}: "
                f"incompatible dimensions ({self.unit.dimension} vs {target_unit.dimension})"
            )
        
        conversion_factor = self.unit.conversion_factor(target_unit)
        return Quantity(self.value * conversion_factor, target_unit)
    
    def to_si(self) -> 'Quantity':
        """Convert to SI base units."""
        si_value = self.value * self.unit.scale
        
        # Construct SI unit from dimension
        si_unit = _dimension_to_si_unit(self.unit.dimension)
        return Quantity(si_value, si_unit)
    
    def __add__(self, other: 'Quantity') -> 'Quantity':
        """Add quantities (must have compatible units)."""
        if not self.unit.is_compatible(other.unit):
            raise DimensionalError(f"Cannot add {self.unit.symbol} and {other.unit.symbol}")
        
        # Convert other to self's unit
        other_converted = other.to(self.unit)
        return Quantity(self.value + other_converted.value, self.unit)
    
    def __sub__(self, other: 'Quantity') -> 'Quantity':
        """Subtract quantities (must have compatible units)."""
        if not self.unit.is_compatible(other.unit):
            raise DimensionalError(f"Cannot subtract {other.unit.symbol} from {self.unit.symbol}")
        
        # Convert other to self's unit
        other_converted = other.to(self.unit)
        return Quantity(self.value - other_converted.value, self.unit)
    
    def __mul__(self, other: Union['Quantity', float]) -> 'Quantity':
        """Multiply quantities or quantity by scalar."""
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit * other.unit)
        else:
            return Quantity(self.value * other, self.unit)
    
    def __rmul__(self, other: float) -> 'Quantity':
        """Right multiply by scalar."""
        return Quantity(self.value * other, self.unit)
    
    def __truediv__(self, other: Union['Quantity', float]) -> 'Quantity':
        """Divide quantities or quantity by scalar."""
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, self.unit / other.unit)
        else:
            return Quantity(self.value / other, self.unit)
    
    def __rtruediv__(self, other: float) -> 'Quantity':
        """Right divide scalar by quantity."""
        return Quantity(other / self.value, dimensionless / self.unit)
    
    def __pow__(self, exponent: Union[int, float]) -> 'Quantity':
        """Raise quantity to a power."""
        return Quantity(self.value ** exponent, self.unit ** exponent)
    
    def __neg__(self) -> 'Quantity':
        """Negate quantity."""
        return Quantity(-self.value, self.unit)
    
    def __abs__(self) -> 'Quantity':
        """Absolute value of quantity."""
        return Quantity(abs(self.value), self.unit)
    
    def sqrt(self) -> 'Quantity':
        """Square root of quantity."""
        return Quantity(math.sqrt(self.value), self.unit ** 0.5)
    
    def __eq__(self, other: 'Quantity') -> bool:
        """Check equality (converts to common unit)."""
        if not isinstance(other, Quantity):
            return False
        if not self.unit.is_compatible(other.unit):
            return False
        
        other_converted = other.to(self.unit)
        return abs(self.value - other_converted.value) < 1e-12
    
    def __str__(self) -> str:
        return f"{self.value} {self.unit.symbol}"
    
    def __repr__(self) -> str:
        return f"Quantity({self.value}, {self.unit.symbol})"


def _dimension_to_si_unit(dimension: Dimension) -> Unit:
    """Convert a dimension to the corresponding SI unit."""
    if dimension.is_dimensionless():
        return dimensionless
    
    # Build compound unit from base units
    unit = dimensionless
    
    if dimension.length != 0:
        unit = unit * (meter ** dimension.length)
    if dimension.mass != 0:
        unit = unit * (kilogram ** dimension.mass)
    if dimension.time != 0:
        unit = unit * (second ** dimension.time)
    if dimension.electric_current != 0:
        unit = unit * (ampere ** dimension.electric_current)
    if dimension.temperature != 0:
        unit = unit * (kelvin ** dimension.temperature)
    if dimension.amount != 0:
        unit = unit * (mole ** dimension.amount)
    if dimension.luminous_intensity != 0:
        unit = unit * (candela ** dimension.luminous_intensity)
    
    return unit


def check_dimensional_consistency(*quantities: Quantity) -> bool:
    """Check if all quantities have the same dimension."""
    if not quantities:
        return True
    
    first_dimension = quantities[0].dimension
    return all(q.dimension == first_dimension for q in quantities)


def parse_unit(unit_string: str) -> Unit:
    """Parse a unit string into a Unit object.
    
    Supports basic operations like multiplication (*), division (/), and powers (^).
    Examples: "m/s", "kg*m/s^2", "Hz"
    """
    # This is a simplified parser - a full implementation would use proper parsing
    unit_string = unit_string.strip()
    
    # Handle some common cases
    unit_map = {
        'm': meter, 'kg': kilogram, 's': second, 'A': ampere, 'K': kelvin,
        'mol': mole, 'cd': candela, 'mm': millimeter, 'cm': centimeter,
        'km': kilometer, 'g': gram, 'ms': millisecond, 'Hz': hertz,
        'kHz': kilohertz, 'N': newton, 'J': joule, 'W': watt, 'Pa': pascal,
        'V': volt, '1': dimensionless, 'dimensionless': dimensionless
    }
    
    if unit_string in unit_map:
        return unit_map[unit_string]
    
    # For now, just return dimensionless for unknown units
    # A full implementation would parse compound units
    return dimensionless


# Convenience functions for creating quantities
def Q(value: float, unit_string: str) -> Quantity:
    """Create a quantity from value and unit string."""
    unit = parse_unit(unit_string)
    return Quantity(value, unit) 