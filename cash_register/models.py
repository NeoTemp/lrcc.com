from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .money import Money


@dataclass
class LineItem:
    name: str
    unit_price: Money
    quantity: int = 1
    percent_discount: Decimal = Decimal("0")  # Applies to line after fixed
    fixed_discount_per_unit: Optional[Money] = None

    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)

    def discount(self) -> Money:
        # Fixed discount capped to subtotal
        subtotal = self.subtotal()
        fixed_total = Money.zero()
        if self.fixed_discount_per_unit is not None:
            fixed_total = self.fixed_discount_per_unit.multiply(self.quantity)
            fixed_total = fixed_total.min(subtotal)

        # Percent discount applied after fixed
        after_fixed = subtotal.subtract(fixed_total)
        percent = self.percent_discount if self.percent_discount else Decimal("0")
        if percent < 0:
            percent = Decimal("0")
        if percent > 100:
            percent = Decimal("100")
        percent_amount = Money(after_fixed.amount * (percent / Decimal("100")))

        total_discount = fixed_total.add(percent_amount)
        return total_discount.min(subtotal)

    def total(self) -> Money:
        return self.subtotal().subtract(self.discount())
