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

The dashboard provides a quick view of:

Total invoices

Approved invoices

Review-required invoices

Unpaid value

Total invoice value

Expected vs Actual amounts

Invoice volume

Payment status

Validation mix

Review queue

Recent invoices

Charts can be explored across Day, Week, Month, and Year.

🛠️ Built With

🐍 Python · 🎈 Streamlit · 🧩 Pydantic · ⚡ Groq · 🐼 Pandas · 📊 Plotly · 🗄️ SQLite · 🔐 python-dotenv

🚀 Run Locally

Clone the repository:

git clone https://github.com/buildwithharshit/paperwork-hub.git
cd paperwork-hub

Create and activate a virtual environment:

python -m venv .venv

Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create a .env file:

GROQ_API_KEY=your_api_key_here

Run the application:

streamlit run app.py

🧪 Test It

Generate test invoices with:

python generate_test_data.py

Test scenarios include:

✅ Valid invoices

⚠️ Line-item mismatches

⚠️ Subtotal mismatches

⚠️ Total mismatches

⚠️ Tax discrepancies

🔁 Duplicate invoices

📦 Batch processing

🔐 Security

Sensitive files such as .env, .venv/, __pycache__/, and invoices.db are excluded from the repository.

Never commit your API key.

🔮 What's Next

📄 PDF invoice support

🖼️ OCR and image invoices

☁️ Cloud database

👥 Multi-user access

🔐 Role-based permissions

📧 Automated notifications

🔗 Accounting integrations

👨‍💻 Built by Harshit Yadav

Business × Finance × Technology × Automation

GitHub

⭐ Paperwork Hub — from invoice documents to verified financial records.
