from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from .models import LineItem
from .money import Money


@dataclass
class CashRegister:
    tax_rate_percent: Decimal = Decimal("0")
    line_items: List[LineItem] = field(default_factory=list)
    order_percent_discount: Decimal = Decimal("0")
    order_fixed_discount: Optional[Money] = None

    def add_item(
        self,
        name: str,
        unit_price: Money,
        quantity: int = 1,
        percent_discount: Decimal = Decimal("0"),
        fixed_discount_per_unit: Optional[Money] = None,
    ) -> None:
        self.line_items.append(
            LineItem(
                name=name,
                unit_price=unit_price,
                quantity=quantity,
                percent_discount=percent_discount,
                fixed_discount_per_unit=fixed_discount_per_unit,
            )
        )

    def remove_item(self, index: int) -> None:
        if 0 <= index < len(self.line_items):
            self.line_items.pop(index)
            return
        raise IndexError("Line item index out of range")

    def clear_items(self) -> None:
        self.line_items.clear()

    def set_tax_rate(self, tax_rate_percent: Decimal) -> None:
        self.tax_rate_percent = Decimal(str(tax_rate_percent))

    def apply_order_percent_discount(self, percent: Decimal) -> None:
        self.order_percent_discount = Decimal(str(percent))

    def apply_order_fixed_discount(self, amount: Money) -> None:
        self.order_fixed_discount = amount

    def clear_discounts(self) -> None:
        self.order_percent_discount = Decimal("0")
        self.order_fixed_discount = None
        for item in self.line_items:
            item.percent_discount = Decimal("0")
            item.fixed_discount_per_unit = None

    def subtotal_before_discounts(self) -> Money:
        total = Money.zero()
        for item in self.line_items:
            total = total.add(item.subtotal())
        return total

    def line_discounts_total(self) -> Money:
        total = Money.zero()
        for item in self.line_items:
            total = total.add(item.discount())
        return total

    def subtotal_after_line_discounts(self) -> Money:
        return self.subtotal_before_discounts().subtract(self.line_discounts_total())

    def order_level_discount(self) -> Money:
        base = self.subtotal_after_line_discounts()
        fixed = self.order_fixed_discount if self.order_fixed_discount is not None else Money.zero()
        fixed_capped = fixed.min(base)
        after_fixed = base.subtract(fixed_capped)

        percent = self.order_percent_discount if self.order_percent_discount else Decimal("0")
        if percent < 0:
            percent = Decimal("0")
        if percent > 100:
            percent = Decimal("100")
        percent_amount = Money(after_fixed.amount * (percent / Decimal("100")))

        combined = fixed_capped.add(percent_amount)
        return combined.min(base)

    def pre_tax_total(self) -> Money:
        return self.subtotal_after_line_discounts().subtract(self.order_level_discount())

    def tax_amount(self) -> Money:
        rate = self.tax_rate_percent if self.tax_rate_percent else Decimal("0")
        return Money(self.pre_tax_total().amount * (rate / Decimal("100")))

    def grand_total(self) -> Money:
        return self.pre_tax_total().add(self.tax_amount())

    def compute_change(self, cash_tendered: Money) -> Money:
        change = cash_tendered.subtract(self.grand_total())
        if change.is_negative():
            raise ValueError("Insufficient cash tendered.")
        return change

    def is_empty(self) -> bool:
        return len(self.line_items) == 0
