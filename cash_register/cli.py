from __future__ import annotations

import argparse
import os
from datetime import datetime
from decimal import Decimal

from .money import Money
from .register import CashRegister
from .receipt import generate_receipt_text

RECEIPTS_DIR = "/workspace/receipts"


def _ensure_receipts_dir() -> None:
    os.makedirs(RECEIPTS_DIR, exist_ok=True)


def run_demo() -> str:
    register = CashRegister()
    register.set_tax_rate(Decimal("8.25"))

    register.add_item("Milk", Money.from_value("3.49"), quantity=2)
    register.add_item("Bread", Money.from_value("2.29"), quantity=1)
    register.add_item("Eggs", Money.from_value("4.19"), quantity=1, percent_discount=Decimal("5"))

    register.apply_order_percent_discount(Decimal("10"))

    cash_tendered = Money.from_value("20.00")
    change = register.compute_change(cash_tendered)

    receipt_text = generate_receipt_text(register, cash_tendered, change)

    _ensure_receipts_dir()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    receipt_path = os.path.join(RECEIPTS_DIR, f"receipt-{timestamp}.txt")
    with open(receipt_path, "w", encoding="utf-8") as f:
        f.write(receipt_text)

    return receipt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Cash Register CLI")
    parser.add_argument("--demo", action="store_true", help="Run demo and save a sample receipt")

    args = parser.parse_args()

    if args.demo:
        path = run_demo()
        print(f"Demo complete. Saved receipt to: {path}")
    else:
        # Minimal interactive loop (text-mode)
        register = CashRegister()
        print("Cash Register - Interactive Mode")
        print("Type 'help' for commands. 'checkout' to finalize. 'quit' to exit.")
        while True:
            try:
                command = input("> ").strip().lower()
            except EOFError:
                break

            if command in ("quit", "exit"):
                break
            if command == "help":
                print(
                    "Commands: add, tax <percent>, orderdisc <percent>, orderfix <amount>, show, remove <index>, clear, checkout"
                )
                continue
            if command.startswith("tax "):
                try:
                    percent = Decimal(command.split(" ", 1)[1])
                    register.set_tax_rate(percent)
                    print(f"Tax set to {percent}%")
                except Exception as exc:
                    print(f"Error: {exc}")
                continue
            if command.startswith("orderdisc "):
                try:
                    percent = Decimal(command.split(" ", 1)[1])
                    register.apply_order_percent_discount(percent)
                    print(f"Order percent discount set to {percent}%")
                except Exception as exc:
                    print(f"Error: {exc}")
                continue
            if command.startswith("orderfix "):
                try:
                    amount = Money.from_value(command.split(" ", 1)[1])
                    register.apply_order_fixed_discount(amount)
                    print(f"Order fixed discount set to {amount}")
                except Exception as exc:
                    print(f"Error: {exc}")
                continue
            if command == "add":
                try:
                    name = input("Item name: ").strip()
                    price = Money.from_value(input("Unit price: ").strip())
                    qty = int(input("Quantity: ").strip())
                    line_disc = input("Line percent discount (0-100, optional): ").strip()
                    pct = Decimal(line_disc) if line_disc else Decimal("0")
                    register.add_item(name, price, qty, pct)
                    print("Added.")
                except Exception as exc:
                    print(f"Error: {exc}")
                continue
            if command == "show":
                if not register.line_items:
                    print("Cart is empty.")
                else:
                    for idx, item in enumerate(register.line_items):
                        print(f"{idx}: {item.name} x{item.quantity} @ {item.unit_price} -> {item.total()}")
                    print(f"Subtotal: {register.subtotal_before_discounts()}")
                    print(f"Line discounts: -{register.line_discounts_total()}")
                    print(f"After line discounts: {register.subtotal_after_line_discounts()}")
                    print(f"Order discount: -{register.order_level_discount()}")
                    print(f"Pre-tax: {register.pre_tax_total()}")
                    print(f"Tax ({register.tax_rate_percent}%): {register.tax_amount()}")
                    print(f"Grand total: {register.grand_total()}")
                continue
            if command.startswith("remove "):
                try:
                    idx = int(command.split(" ", 1)[1])
                    register.remove_item(idx)
                    print("Removed.")
                except Exception as exc:
                    print(f"Error: {exc}")
                continue
            if command == "clear":
                register.clear_items()
                register.clear_discounts()
                print("Cleared cart and discounts.")
                continue
            if command == "checkout":
                try:
                    if register.is_empty():
                        print("Cart is empty.")
                        continue
                    cash = Money.from_value(input("Cash tendered: ").strip())
                    change = register.compute_change(cash)
                    receipt_text = generate_receipt_text(register, cash, change)
                    _ensure_receipts_dir()
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    receipt_path = os.path.join(RECEIPTS_DIR, f"receipt-{timestamp}.txt")
                    with open(receipt_path, "w", encoding="utf-8") as f:
                        f.write(receipt_text)
                    print(f"Saved receipt to: {receipt_path}")
                except Exception as exc:
                    print(f"Error: {exc}")
                continue

            print("Unknown command. Type 'help'.")


if __name__ == "__main__":
    main()
