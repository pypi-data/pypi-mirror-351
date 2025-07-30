#!/usr/bin/env python3
"""
Spruce Compiler CLI - Units system and automatic differentiation engine.

This pre-alpha version demonstrates the core foundational components:
- Dimensional analysis and units system
- Symbolic automatic differentiation
- Basic expression manipulation and optimization
"""

import argparse
import sys
from typing import Dict, Any

from .symbolic import Variable, Expression, diff, sin, cos, exp, ln, sqrt
from .units import (
    Unit, Quantity, DimensionalError, 
    meter, kilogram, second, newton, joule, hertz, millimeter,
    m, kg, s, N, J, Hz, Q
)


def demo_symbolic_ad():
    """Demonstrate symbolic automatic differentiation capabilities."""
    print("=== Symbolic Automatic Differentiation Demo ===\n")
    
    # Create variables
    x = Variable('x')
    t = Variable('t')
    
    # Define some physics expressions
    print("1. Simple harmonic oscillator energy:")
    k = Variable('k')  # spring constant
    m = Variable('m')  # mass
    
    # Kinetic energy: T = (1/2) * m * v^2, where v = dx/dt
    v = Variable('v')
    kinetic = 0.5 * m * v**2
    print(f"   Kinetic energy: T = {kinetic}")
    
    # Potential energy: V = (1/2) * k * x^2
    potential = 0.5 * k * x**2
    print(f"   Potential energy: V = {potential}")
    
    # Total energy
    total_energy = kinetic + potential
    print(f"   Total energy: H = {total_energy}")
    
    # Compute forces via automatic differentiation
    force = -diff(potential, x)
    print(f"   Force: F = -dV/dx = {force}")
    
    print("\n2. Trigonometric functions:")
    trig_expr = sin(x) * cos(x)
    print(f"   f(x) = {trig_expr}")
    
    trig_derivative = diff(trig_expr, x)
    print(f"   f'(x) = {trig_derivative}")
    
    print("\n3. Exponential decay:")
    decay_expr = exp(-t / Variable('tau'))
    print(f"   f(t) = {decay_expr}")
    
    decay_derivative = diff(decay_expr, t)
    print(f"   f'(t) = {decay_derivative}")
    
    print("\n4. C++ code generation:")
    print(f"   Force in C++: {force.to_cpp()}")
    print(f"   Trig derivative in C++: {trig_derivative.to_cpp()}")
    
    print("\n5. Expression evaluation:")
    values = {'x': 1.0, 'k': 100.0}
    try:
        force_value = force.evaluate(values)
        print(f"   Force at x=1.0, k=100.0: {force_value} N")
    except ValueError as e:
        print(f"   Evaluation error: {e}")


def demo_units_system():
    """Demonstrate units system and dimensional analysis."""
    print("\n=== Units System and Dimensional Analysis Demo ===\n")
    
    print("1. Creating physical quantities:")
    length = Quantity(0.65, meter)
    mass_density = Quantity(7850, kg / (m**3))
    frequency = Quantity(440, Hz)
    
    print(f"   String length: {length}")
    print(f"   Steel density: {mass_density}")
    print(f"   Frequency: {frequency}")
    
    print("\n2. Unit conversions:")
    length_mm = length.to(millimeter)  # Convert to mm
    print(f"   Length in mm: {length_mm}")
    
    print("\n3. Dimensional analysis in physics calculations:")
    try:
        # Calculate string tension from frequency (simplified)
        # T = (2*L*f)^2 * μ, where μ is linear mass density
        
        # First, we need linear mass density (mass per unit length)
        # For a cylindrical string: μ = ρ * A = ρ * π * (d/2)^2
        diameter = Quantity(1.0, millimeter)  # 1mm diameter
        area = 3.14159 * (diameter / 2)**2
        linear_density = mass_density * area
        
        print(f"   String diameter: {diameter}")
        print(f"   Cross-sectional area: {area}")
        print(f"   Linear mass density: {linear_density}")
        
        # Calculate tension
        tension_factor = (2 * length * frequency)**2
        tension = tension_factor * linear_density
        
        print(f"   Tension calculation factor: {tension_factor}")
        print(f"   String tension: {tension}")
        print(f"   Tension in Newtons: {tension.to(N)}")
        
    except DimensionalError as e:
        print(f"   Dimensional error: {e}")
    
    print("\n4. Dimensional error detection:")
    try:
        # This should fail - can't add length and mass
        invalid = length + Quantity(1.0, kg)
        print(f"   This shouldn't print: {invalid}")
    except DimensionalError as e:
        print(f"   ✓ Caught dimensional error: {e}")
    
    print("\n5. Unit arithmetic:")
    velocity_unit = m / s
    acceleration_unit = velocity_unit / s
    force_unit = kg * acceleration_unit
    
    print(f"   Velocity unit: {velocity_unit}")
    print(f"   Acceleration unit: {acceleration_unit}")
    print(f"   Force unit: {force_unit}")
    print(f"   Force unit dimension: {force_unit.dimension}")


def demo_physics_modeling():
    """Demonstrate physics modeling with symbolic expressions and units."""
    print("\n=== Physics Modeling Demo ===\n")
    
    print("1. String wave equation energy functions:")
    
    # Symbolic variables for string physics
    u = Variable('u')        # displacement
    u_t = Variable('u_t')    # time derivative
    u_x = Variable('u_x')    # spatial derivative
    T = Variable('T')        # tension
    rho = Variable('rho')    # linear density
    
    # Kinetic energy density: (1/2) * ρ * (∂u/∂t)^2
    kinetic_density = 0.5 * rho * u_t**2
    print(f"   Kinetic energy density: {kinetic_density}")
    
    # Potential energy density: (1/2) * T * (∂u/∂x)^2
    potential_density = 0.5 * T * u_x**2
    print(f"   Potential energy density: {potential_density}")
    
    # Total Hamiltonian density
    hamiltonian_density = kinetic_density + potential_density
    print(f"   Hamiltonian density: H = {hamiltonian_density}")
    
    print("\n2. Automatic force derivation:")
    # Force from potential energy: F = -∂H/∂u_x (simplified)
    force_density = -diff(potential_density, u_x)
    print(f"   Force density: f = -∂V/∂u_x = {force_density}")
    
    print("\n3. Generated C++ code for real-time audio:")
    print("   ```cpp")
    print(f"   // Hamiltonian density: {hamiltonian_density.to_cpp()}")
    print(f"   // Force density: {force_density.to_cpp()}")
    print("   ```")
    
    print("\n4. Units validation for string parameters:")
    try:
        # Define physical parameters with units
        string_tension = Quantity(100.0, N)
        string_density = Quantity(0.001, kg / m)
        
        print(f"   String tension: {string_tension}")
        print(f"   Linear density: {string_density}")
        
        # Calculate wave speed: c = sqrt(T/ρ)
        wave_speed_squared = string_tension / string_density
        print(f"   Wave speed squared: {wave_speed_squared}")
        print(f"   Wave speed: {wave_speed_squared.sqrt()}")
        
    except DimensionalError as e:
        print(f"   Dimensional error: {e}")


def run_interactive_mode():
    """Run interactive mode for experimenting with expressions and units."""
    print("\n=== Interactive Mode ===")
    print("Enter symbolic expressions or unit calculations.")
    print("Examples:")
    print("  expr: x**2 + sin(x)")
    print("  diff: x**2 + sin(x), x")
    print("  unit: 440 Hz")
    print("  quit: exit")
    print()
    
    while True:
        try:
            user_input = input("spruce> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.startswith('expr:'):
                # Parse and display expression
                expr_str = user_input[5:].strip()
                print(f"Expression parsing not implemented yet: {expr_str}")
                print("Use the demo functions to see symbolic AD capabilities.")
                
            elif user_input.startswith('diff:'):
                # Parse and differentiate expression
                diff_str = user_input[5:].strip()
                print(f"Differentiation parsing not implemented yet: {diff_str}")
                print("Use the demo functions to see automatic differentiation.")
                
            elif user_input.startswith('unit:'):
                # Parse and display unit
                unit_str = user_input[5:].strip()
                print(f"Unit parsing not implemented yet: {unit_str}")
                print("Use the demo functions to see units system.")
                
            elif user_input == 'demo':
                demo_symbolic_ad()
                demo_units_system()
                demo_physics_modeling()
                
            else:
                print("Unknown command. Try 'demo', 'expr:', 'diff:', 'unit:', or 'quit'")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spruce Compiler - Units system and automatic differentiation engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spruce demo              # Run all demos
  spruce demo --symbolic   # Demo symbolic AD only
  spruce demo --units      # Demo units system only
  spruce demo --physics    # Demo physics modeling only
  spruce interactive       # Interactive mode
  spruce version           # Show version info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration of capabilities')
    demo_parser.add_argument('--symbolic', action='store_true', 
                           help='Demo symbolic automatic differentiation only')
    demo_parser.add_argument('--units', action='store_true',
                           help='Demo units system only')
    demo_parser.add_argument('--physics', action='store_true',
                           help='Demo physics modeling only')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Run in interactive mode')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        if args.symbolic:
            demo_symbolic_ad()
        elif args.units:
            demo_units_system()
        elif args.physics:
            demo_physics_modeling()
        else:
            # Run all demos
            demo_symbolic_ad()
            demo_units_system()
            demo_physics_modeling()
            
    elif args.command == 'interactive':
        run_interactive_mode()
        
    elif args.command == 'version':
        from . import __version__, __author__, __email__
        print(f"Spruce Compiler v{__version__}")
        print(f"Author: {__author__}")
        print(f"Email: {__email__}")
        print("\nThis pre-alpha version provides:")
        print("- Symbolic automatic differentiation engine")
        print("- Comprehensive units system with dimensional analysis")
        print("- Basic physics modeling capabilities")
        print("\nFuture versions will include the full port-Hamiltonian compilation pipeline.")
        
    else:
        # Default: show help and run a quick demo
        parser.print_help()
        print("\n" + "="*60)
        print("Quick Demo:")
        print("="*60)
        demo_symbolic_ad()


if __name__ == '__main__':
    main() 