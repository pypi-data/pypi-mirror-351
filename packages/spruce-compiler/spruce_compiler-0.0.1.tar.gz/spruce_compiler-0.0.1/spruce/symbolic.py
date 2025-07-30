"""
Symbolic automatic differentiation engine for Spruce.

This module provides symbolic expression manipulation and automatic differentiation
capabilities for physics-based modeling. Expressions are built from variables and
operations, and can be differentiated symbolically.
"""

import math
from typing import Union, Dict, Set, Any, Optional
from abc import ABC, abstractmethod


class Expression(ABC):
    """Base class for all symbolic expressions."""
    
    @abstractmethod
    def diff(self, var: 'Variable') -> 'Expression':
        """Compute the derivative with respect to a variable."""
        pass
    
    @abstractmethod
    def evaluate(self, values: Dict[str, float]) -> float:
        """Evaluate the expression given variable values."""
        pass
    
    @abstractmethod
    def variables(self) -> Set[str]:
        """Return the set of variable names in this expression."""
        pass
    
    @abstractmethod
    def simplify(self) -> 'Expression':
        """Return a simplified version of this expression."""
        pass
    
    @abstractmethod
    def to_cpp(self) -> str:
        """Generate C++ code for this expression."""
        pass
    
    def __str__(self) -> str:
        return self._to_string()
    
    @abstractmethod
    def _to_string(self) -> str:
        """Internal string representation."""
        pass
    
    # Arithmetic operations
    def __add__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Add(self, other)
    
    def __radd__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Add(other, self)
    
    def __sub__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Sub(self, other)
    
    def __rsub__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Sub(other, self)
    
    def __mul__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Mul(self, other)
    
    def __rmul__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Mul(other, self)
    
    def __truediv__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Div(self, other)
    
    def __rtruediv__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Div(other, self)
    
    def __pow__(self, other: Union['Expression', float]) -> 'Expression':
        if isinstance(other, (int, float)):
            other = Constant(float(other))
        return Power(self, other)
    
    def __neg__(self) -> 'Expression':
        return Mul(Constant(-1.0), self)


class Variable(Expression):
    """A symbolic variable."""
    
    def __init__(self, name: str):
        self.name = name
    
    def diff(self, var: 'Variable') -> Expression:
        if self.name == var.name:
            return Constant(1.0)
        else:
            return Constant(0.0)
    
    def evaluate(self, values: Dict[str, float]) -> float:
        if self.name not in values:
            raise ValueError(f"Variable '{self.name}' not found in values")
        return values[self.name]
    
    def variables(self) -> Set[str]:
        return {self.name}
    
    def simplify(self) -> Expression:
        return self
    
    def to_cpp(self) -> str:
        return self.name
    
    def _to_string(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class Constant(Expression):
    """A constant value."""
    
    def __init__(self, value: float):
        self.value = float(value)
    
    def diff(self, var: Variable) -> Expression:
        return Constant(0.0)
    
    def evaluate(self, values: Dict[str, float]) -> float:
        return self.value
    
    def variables(self) -> Set[str]:
        return set()
    
    def simplify(self) -> Expression:
        return self
    
    def to_cpp(self) -> str:
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)
    
    def _to_string(self) -> str:
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Constant) and abs(self.value - other.value) < 1e-12
    
    def __hash__(self) -> int:
        return hash(self.value)


class BinaryOp(Expression):
    """Base class for binary operations."""
    
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def variables(self) -> Set[str]:
        return self.left.variables() | self.right.variables()
    
    def evaluate(self, values: Dict[str, float]) -> float:
        return self._evaluate_op(self.left.evaluate(values), self.right.evaluate(values))
    
    @abstractmethod
    def _evaluate_op(self, left_val: float, right_val: float) -> float:
        pass


class Add(BinaryOp):
    """Addition operation."""
    
    def diff(self, var: Variable) -> Expression:
        return Add(self.left.diff(var), self.right.diff(var))
    
    def _evaluate_op(self, left_val: float, right_val: float) -> float:
        return left_val + right_val
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # 0 + x = x
        if isinstance(left, Constant) and left.value == 0:
            return right
        # x + 0 = x
        if isinstance(right, Constant) and right.value == 0:
            return left
        # c1 + c2 = c3
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value + right.value)
        
        return Add(left, right)
    
    def to_cpp(self) -> str:
        return f"({self.left.to_cpp()} + {self.right.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"({self.left} + {self.right})"


class Sub(BinaryOp):
    """Subtraction operation."""
    
    def diff(self, var: Variable) -> Expression:
        return Sub(self.left.diff(var), self.right.diff(var))
    
    def _evaluate_op(self, left_val: float, right_val: float) -> float:
        return left_val - right_val
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # x - 0 = x
        if isinstance(right, Constant) and right.value == 0:
            return left
        # 0 - x = -x
        if isinstance(left, Constant) and left.value == 0:
            return Mul(Constant(-1.0), right)
        # c1 - c2 = c3
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value - right.value)
        
        return Sub(left, right)
    
    def to_cpp(self) -> str:
        return f"({self.left.to_cpp()} - {self.right.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"({self.left} - {self.right})"


class Mul(BinaryOp):
    """Multiplication operation."""
    
    def diff(self, var: Variable) -> Expression:
        # Product rule: (f*g)' = f'*g + f*g'
        return Add(
            Mul(self.left.diff(var), self.right),
            Mul(self.left, self.right.diff(var))
        )
    
    def _evaluate_op(self, left_val: float, right_val: float) -> float:
        return left_val * right_val
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # 0 * x = 0
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0.0)
        # x * 0 = 0
        if isinstance(right, Constant) and right.value == 0:
            return Constant(0.0)
        # 1 * x = x
        if isinstance(left, Constant) and left.value == 1:
            return right
        # x * 1 = x
        if isinstance(right, Constant) and right.value == 1:
            return left
        # c1 * c2 = c3
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value * right.value)
        
        return Mul(left, right)
    
    def to_cpp(self) -> str:
        return f"({self.left.to_cpp()} * {self.right.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"({self.left} * {self.right})"


class Div(BinaryOp):
    """Division operation."""
    
    def diff(self, var: Variable) -> Expression:
        # Quotient rule: (f/g)' = (f'*g - f*g') / g^2
        numerator = Sub(
            Mul(self.left.diff(var), self.right),
            Mul(self.left, self.right.diff(var))
        )
        denominator = Power(self.right, Constant(2.0))
        return Div(numerator, denominator)
    
    def _evaluate_op(self, left_val: float, right_val: float) -> float:
        if abs(right_val) < 1e-12:
            raise ValueError("Division by zero")
        return left_val / right_val
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # 0 / x = 0 (x != 0)
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0.0)
        # x / 1 = x
        if isinstance(right, Constant) and right.value == 1:
            return left
        # c1 / c2 = c3
        if isinstance(left, Constant) and isinstance(right, Constant):
            if abs(right.value) < 1e-12:
                raise ValueError("Division by zero in simplification")
            return Constant(left.value / right.value)
        
        return Div(left, right)
    
    def to_cpp(self) -> str:
        return f"({self.left.to_cpp()} / {self.right.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"({self.left} / {self.right})"


class Power(BinaryOp):
    """Power operation."""
    
    def diff(self, var: Variable) -> Expression:
        # Power rule: (f^g)' = f^g * (g' * ln(f) + g * f'/f)
        # For constant exponent: (f^c)' = c * f^(c-1) * f'
        if isinstance(self.right, Constant):
            # Constant exponent case
            if self.right.value == 0:
                return Constant(0.0)
            elif self.right.value == 1:
                return self.left.diff(var)
            else:
                return Mul(
                    Mul(self.right, Power(self.left, Constant(self.right.value - 1))),
                    self.left.diff(var)
                )
        else:
            # General case: (f^g)' = f^g * (g' * ln(f) + g * f'/f)
            ln_f = Ln(self.left)
            term1 = Mul(self.right.diff(var), ln_f)
            term2 = Mul(self.right, Div(self.left.diff(var), self.left))
            return Mul(self, Add(term1, term2))
    
    def _evaluate_op(self, left_val: float, right_val: float) -> float:
        if left_val < 0 and right_val != int(right_val):
            raise ValueError("Negative base with non-integer exponent")
        return left_val ** right_val
    
    def simplify(self) -> Expression:
        left = self.left.simplify()
        right = self.right.simplify()
        
        # x^0 = 1
        if isinstance(right, Constant) and right.value == 0:
            return Constant(1.0)
        # x^1 = x
        if isinstance(right, Constant) and right.value == 1:
            return left
        # 0^x = 0 (x > 0)
        if isinstance(left, Constant) and left.value == 0:
            return Constant(0.0)
        # 1^x = 1
        if isinstance(left, Constant) and left.value == 1:
            return Constant(1.0)
        # c1^c2 = c3
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value ** right.value)
        
        return Power(left, right)
    
    def to_cpp(self) -> str:
        return f"pow({self.left.to_cpp()}, {self.right.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"({self.left}^{self.right})"


class UnaryOp(Expression):
    """Base class for unary operations."""
    
    def __init__(self, operand: Expression):
        self.operand = operand
    
    def variables(self) -> Set[str]:
        return self.operand.variables()
    
    def evaluate(self, values: Dict[str, float]) -> float:
        return self._evaluate_op(self.operand.evaluate(values))
    
    @abstractmethod
    def _evaluate_op(self, operand_val: float) -> float:
        pass


class Sin(UnaryOp):
    """Sine function."""
    
    def diff(self, var: Variable) -> Expression:
        return Mul(Cos(self.operand), self.operand.diff(var))
    
    def _evaluate_op(self, operand_val: float) -> float:
        return math.sin(operand_val)
    
    def simplify(self) -> Expression:
        operand = self.operand.simplify()
        if isinstance(operand, Constant):
            return Constant(math.sin(operand.value))
        return Sin(operand)
    
    def to_cpp(self) -> str:
        return f"sin({self.operand.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"sin({self.operand})"


class Cos(UnaryOp):
    """Cosine function."""
    
    def diff(self, var: Variable) -> Expression:
        return Mul(Mul(Constant(-1.0), Sin(self.operand)), self.operand.diff(var))
    
    def _evaluate_op(self, operand_val: float) -> float:
        return math.cos(operand_val)
    
    def simplify(self) -> Expression:
        operand = self.operand.simplify()
        if isinstance(operand, Constant):
            return Constant(math.cos(operand.value))
        return Cos(operand)
    
    def to_cpp(self) -> str:
        return f"cos({self.operand.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"cos({self.operand})"


class Ln(UnaryOp):
    """Natural logarithm function."""
    
    def diff(self, var: Variable) -> Expression:
        return Div(self.operand.diff(var), self.operand)
    
    def _evaluate_op(self, operand_val: float) -> float:
        if operand_val <= 0:
            raise ValueError("Logarithm of non-positive number")
        return math.log(operand_val)
    
    def simplify(self) -> Expression:
        operand = self.operand.simplify()
        if isinstance(operand, Constant):
            if operand.value <= 0:
                raise ValueError("Logarithm of non-positive number")
            return Constant(math.log(operand.value))
        return Ln(operand)
    
    def to_cpp(self) -> str:
        return f"log({self.operand.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"ln({self.operand})"


class Exp(UnaryOp):
    """Exponential function."""
    
    def diff(self, var: Variable) -> Expression:
        return Mul(self, self.operand.diff(var))
    
    def _evaluate_op(self, operand_val: float) -> float:
        return math.exp(operand_val)
    
    def simplify(self) -> Expression:
        operand = self.operand.simplify()
        if isinstance(operand, Constant):
            return Constant(math.exp(operand.value))
        return Exp(operand)
    
    def to_cpp(self) -> str:
        return f"exp({self.operand.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"exp({self.operand})"


class Sqrt(UnaryOp):
    """Square root function."""
    
    def diff(self, var: Variable) -> Expression:
        return Div(self.operand.diff(var), Mul(Constant(2.0), self))
    
    def _evaluate_op(self, operand_val: float) -> float:
        if operand_val < 0:
            raise ValueError("Square root of negative number")
        return math.sqrt(operand_val)
    
    def simplify(self) -> Expression:
        operand = self.operand.simplify()
        if isinstance(operand, Constant):
            if operand.value < 0:
                raise ValueError("Square root of negative number")
            return Constant(math.sqrt(operand.value))
        return Sqrt(operand)
    
    def to_cpp(self) -> str:
        return f"sqrt({self.operand.to_cpp()})"
    
    def _to_string(self) -> str:
        return f"sqrt({self.operand})"


# Convenience functions
def diff(expr: Expression, var: Variable) -> Expression:
    """Compute the derivative of an expression with respect to a variable."""
    return expr.diff(var).simplify()


def sin(expr: Expression) -> Expression:
    """Sine function."""
    return Sin(expr)


def cos(expr: Expression) -> Expression:
    """Cosine function."""
    return Cos(expr)


def ln(expr: Expression) -> Expression:
    """Natural logarithm function."""
    return Ln(expr)


def exp(expr: Expression) -> Expression:
    """Exponential function."""
    return Exp(expr)


def sqrt(expr: Expression) -> Expression:
    """Square root function."""
    return Sqrt(expr)


def pow(base: Expression, exponent: Union[Expression, float]) -> Expression:
    """Power function."""
    if isinstance(exponent, (int, float)):
        exponent = Constant(float(exponent))
    return Power(base, exponent) 