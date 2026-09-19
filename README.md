📄 Paperwork Hub

Smart invoice processing and financial verification for small businesses.

Paperwork Hub turns invoice documents into structured financial data, checks the numbers independently, detects discrepancies and duplicates, and gives businesses a clean dashboard to monitor their paperwork.

💡 Core Idea

Extract → Validate → Verify → Approve or Review → Store → Analyze

✨ Features

📥 Upload single or multiple invoices

🔍 Extract structured invoice information

🧮 Verify line items, subtotal, tax, and total

🔁 Detect duplicate invoices

⚠️ Automatically flag invoices for Human Review

✅ Approve invoices that pass all checks

🗄️ Store invoice records in SQLite

📊 Monitor financial and processing activity

🔎 Search and filter invoice history

📤 Export invoice data as CSV

🌓 Switch between light and dark mode

📦 Process invoices in batches

🧠 How It Works

Invoice documents are converted into structured data and then independently checked using deterministic Python rules.

📄 Invoice
   ↓
🔍 Extract
   ↓
🧩 Validate
   ↓
🧮 Verify
   ↓
✅ Approved / ⚠️ Human Review
   ↓
🗄️ Store
   ↓
📊 Analyze

The important design principle is simple:

Use automated extraction for unstructured information and deterministic rules for financial verification.

🧮 Financial Checks

Paperwork Hub verifies:

Quantity × Unit Price = Line Item Amount

Sum of Line Items = Subtotal

Subtotal + Tax = Total

₹0.01 calculation tolerance

Unique invoice numbers

Invoices that pass the checks are Approved.
Invoices with discrepancies are sent to Human Review with the validation reason stored.

📊 Dashboard

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