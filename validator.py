from dataclasses import dataclass

from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    description: str
    quantity: float = Field(
        gt=0
    )
    unit_price: float = Field(
        ge=0
    )
    amount: float = Field(
        ge=0
    )


class Invoice(BaseModel):
    invoice_number: str
    vendor: str
    invoice_date: str

    items: list[InvoiceItem]

    subtotal: float = Field(
        ge=0
    )

    tax: float = Field(
        ge=0
    )

    total: float = Field(
        ge=0
    )

    due_date: str
    payment_status: str


@dataclass
class ValidationResult:
    status: str
    difference: float
    audit_reason: str
    item_errors: list[str]
    calculated_subtotal: float
    expected_total: float
    subtotal_difference: float


def validate_invoice(invoice):
    item_errors = []

    calculated_subtotal = 0.0

    for item in invoice.items:
        expected_item_amount = round(
            item.quantity
            * item.unit_price,
            2,
        )

        item_difference = round(
            item.amount
            - expected_item_amount,
            2,
        )

        if abs(
            item_difference
        ) >= 0.01:
            item_errors.append(
                f"{item.description}: "
                f"expected "
                f"₹{expected_item_amount:,.2f}, "
                f"but extracted "
                f"₹{item.amount:,.2f}"
            )

        calculated_subtotal += (
            item.amount
        )

    calculated_subtotal = round(
        calculated_subtotal,
        2,
    )

    subtotal_difference = round(
        calculated_subtotal
        - invoice.subtotal,
        2,
    )

    expected_total = round(
        invoice.subtotal
        + invoice.tax,
        2,
    )

    difference = round(
        invoice.total
        - expected_total,
        2,
    )

    all_checks_passed = (
        not item_errors
        and abs(
            subtotal_difference
        ) < 0.01
        and abs(
            difference
        ) < 0.01
    )

    if all_checks_passed:
        status = "Approved"

        audit_reason = (
            "All line-item calculations, "
            "subtotal, tax and total "
            "checks passed."
        )

    else:
        status = "Human Review"

        reasons = []

        if item_errors:
            reasons.append(
                "one or more line items "
                "have a calculation mismatch"
            )

        if abs(
            subtotal_difference
        ) >= 0.01:
            reasons.append(
                "line-item subtotal "
                f"differs by "
                f"₹{subtotal_difference:,.2f}"
            )

        if abs(
            difference
        ) >= 0.01:
            reasons.append(
                "invoice total "
                f"differs by "
                f"₹{difference:,.2f}"
            )

        audit_reason = "; ".join(
            reasons
        )

    return ValidationResult(
        status=status,
        difference=difference,
        audit_reason=audit_reason,
        item_errors=item_errors,
        calculated_subtotal=calculated_subtotal,
        expected_total=expected_total,
        subtotal_difference=subtotal_difference,
    )