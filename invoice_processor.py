import json
import os
import re

from groq import Groq
from pydantic import ValidationError

from validator import Invoice


MODEL_NAME = "openai/gpt-oss-20b"


class InvoiceProcessingError(Exception):
    """Raised when document processing cannot safely produce an invoice."""


def _clean_json_response(content):
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

    if (
        cleaned.startswith("{")
        and cleaned.endswith("}")
    ):
        return cleaned

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end > start:
        return cleaned[
            start:end + 1
        ]

    raise InvoiceProcessingError(
        "The processing service returned malformed JSON."
    )


def extract_invoice(invoice_text):
    api_key = os.environ.get(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise InvoiceProcessingError(
            "GROQ_API_KEY is not configured."
        )

    client = Groq(
        api_key=api_key
    )

    prompt = f"""
Extract the following information from this invoice:

- invoice_number
- vendor
- invoice_date
- items
- subtotal
- tax
- total
- due_date
- payment_status

For every item inside items, extract:

- description
- quantity
- unit_price
- amount

Return ONLY valid JSON.

Do not use Markdown.
Do not use code fences.
Do not include explanatory text.

Invoice:

{invoice_text}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

    except Exception as exc:
        raise InvoiceProcessingError(
            "The document could not be processed right now."
        ) from exc

    content = ""

    if response.choices:
        message = response.choices[0].message

        content = (
            message.content or ""
        ).strip()

    if not content:
        raise InvoiceProcessingError(
            "The processing service returned an empty response."
        )

    try:
        cleaned_json = _clean_json_response(
            content
        )

        data = json.loads(
            cleaned_json
        )

    except (
        json.JSONDecodeError,
        InvoiceProcessingError,
    ) as exc:
        raise InvoiceProcessingError(
            "The processing service returned malformed invoice data."
        ) from exc

    try:
        return Invoice(
            **data
        )

    except ValidationError as exc:
        raise InvoiceProcessingError(
            "The extracted invoice data failed validation."
        ) from exc