# Paperwork Hub

Paperwork Hub is an invoice processing and financial verification application built for small businesses.

It converts invoice documents into structured information, independently verifies financial calculations, stores the results in SQLite, and provides a dashboard for monitoring invoice activity and exceptions.

## What It Does

Paperwork Hub allows users to:

- Upload one or multiple invoice documents
- Extract structured invoice information
- Validate invoice line-item calculations
- Verify subtotal, tax, and total values
- Detect financial discrepancies
- Identify duplicate invoices
- Automatically classify invoices as Approved or Human Review
- Store processed invoices in SQLite
- Search and filter invoice history
- Review individual invoice details
- Delete selected invoices or clear the database
- View financial and processing dashboards
- Download invoice data as CSV
- Switch between light and dark mode

## How It Works

The application follows this workflow:

Invoice Document
       ↓
Document Extraction
       ↓
Structured Invoice Data
       ↓
Pydantic Validation
       ↓
Deterministic Financial Checks
       ↓
Approved / Human Review
       ↓
SQLite Database
       ↓
Dashboard & Invoice History

The extraction layer handles unstructured invoice information, while the financial verification layer independently checks the extracted values using deterministic Python rules.

## Financial Validation

The system checks:

- Quantity × Unit Price = Line Item Amount
- Sum of Line Items = Subtotal
- Subtotal + Tax = Total
- Financial differences within a small ₹0.01 tolerance
- Duplicate invoice numbers

Invoices that pass all checks are marked as:

**Approved**

Invoices with discrepancies are marked as:

**Human Review**

## Dashboard

The dashboard provides visibility into:

- Total number of invoices
- Approved invoices
- Invoices requiring review
- Unpaid invoice value
- Total invoice value
- Expected vs Actual values
- Invoice volume
- Validation mix
- Payment status
- Review queue
- Recent invoices

## Tech Stack

- Python
- Streamlit
- Pydantic
- Groq
- Pandas
- Plotly
- SQLite
- python-dotenv

## Project Structure

```text
Paperwork Hub/
│
├── .streamlit/
│   └── config.toml
│
├── ui/
│   ├── __init__.py
│   ├── charts.py
│   ├── components.py
│   └── theme.py
│
├── app.py
├── database.py
├── invoice_processor.py
├── validator.py
├── generate_test_data.py
├── sample_invoice.txt
├── requirements.txt
├── README.md
└── .gitignore