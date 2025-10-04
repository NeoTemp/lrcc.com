from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Union

# Configure high precision to minimize floating errors before quantization
getcontext().prec = 28

_CENTS = Decimal("0.01")


@dataclass(frozen=True)
class Money:
    """Immutable monetary amount with cent-level precision.

    Internally stores a Decimal quantized to cents using bankers-friendly rounding (HALF_UP).
    """

    amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", self._quantize(self.amount))

    @staticmethod
    def _to_decimal(value: Union[str, float, int, Decimal, "Money"]) -> Decimal:
        if isinstance(value, Money):
            return value.amount
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int,)):
            return Decimal(value)
        if isinstance(value, float):
            # Avoid float binary rounding issues by converting through string
            return Decimal(str(value))
        if isinstance(value, str):
            cleaned = value.strip().replace("$", "").replace(",", "")
            return Decimal(cleaned)
        raise TypeError(f"Unsupported type for money conversion: {type(value)}")

    @classmethod
    def from_value(cls, value: Union[str, float, int, Decimal, "Money"]) -> "Money":
        return cls(cls._to_decimal(value))

    @classmethod
    def zero(cls) -> "Money":
        return cls(Decimal("0"))

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_UP)

    # Arithmetic operations return new Money instances
    def add(self, other: Union["Money", str, float, int, Decimal]) -> "Money":
        other_decimal = self._to_decimal(other)
        return Money(self.amount + other_decimal)

    def subtract(self, other: Union["Money", str, float, int, Decimal]) -> "Money":
        other_decimal = self._to_decimal(other)
        return Money(self.amount - other_decimal)

    def multiply(self, multiplier: Union[int, float, Decimal]) -> "Money":
        if isinstance(multiplier, int):
            return Money(self.amount * Decimal(multiplier))
        if isinstance(multiplier, float):
            return Money(self.amount * Decimal(str(multiplier)))
        if isinstance(multiplier, Decimal):
            return Money(self.amount * multiplier)
        raise TypeError("Multiplier must be int, float, or Decimal")

    def min(self, other: Union["Money", str, float, int, Decimal]) -> "Money":
        other_decimal = self._to_decimal(other)
        return Money(self.amount if self.amount <= other_decimal else other_decimal)

    def is_negative(self) -> bool:
        return self.amount < 0

    def __str__(self) -> str:
        return f"${self.amount:.2f}"

    def __repr__(self) -> str:
        return f"Money(amount=Decimal('{self.amount}'))"
