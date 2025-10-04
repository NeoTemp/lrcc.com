from __future__ import annotations

from datetime import datetime

from .money import Money
from .register import CashRegister


def _fmt(m: Money) -> str:
    return f"${m.amount:.2f}"


def generate_receipt_text(register: CashRegister, cash_tendered: Money, change_due: Money) -> str:
    lines: list[str] = []
    lines.append("RECEIPT")
    lines.append(f"Date: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("-" * 40)
    lines.append("Items:")

    for idx, item in enumerate(register.line_items):
        lines.append(f"{idx + 1:>2}. {item.name} x{item.quantity} @ {_fmt(item.unit_price)}")
        if item.percent_discount and item.percent_discount != 0:
            lines.append(f"    Line percent discount: {item.percent_discount}%")
        if item.fixed_discount_per_unit is not None and item.fixed_discount_per_unit.amount != 0:
            lines.append(f"    Line fixed discount: {_fmt(item.fixed_discount_per_unit)} each")
        lines.append(
            f"    Subtotal: {_fmt(item.subtotal())}  Discount: {_fmt(item.discount())}  Total: {_fmt(item.total())}"
        )

    lines.append("-" * 40)
    lines.append(f"Subtotal: {_fmt(register.subtotal_before_discounts())}")
    lines.append(f"Line discounts: -{_fmt(register.line_discounts_total())}")
    lines.append(f"After line discounts: {_fmt(register.subtotal_after_line_discounts())}")

    order_disc = register.order_level_discount()
    if order_disc.amount != 0:
        lines.append(f"Order discount: -{_fmt(order_disc)}")

    lines.append(f"Pre-tax total: {_fmt(register.pre_tax_total())}")
    lines.append(f"Tax ({register.tax_rate_percent}%): {_fmt(register.tax_amount())}")
    lines.append(f"Grand total: {_fmt(register.grand_total())}")

    lines.append(f"Cash tendered: {_fmt(cash_tendered)}")
    lines.append(f"Change: {_fmt(change_due)}")
    lines.append("-" * 40)
    lines.append("Thank you for your purchase!")

    return "\n".join(lines)
