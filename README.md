📄 Paperwork Hub
Invoice processing, financial verification, and exception management for small businesses.

Paperwork Hub is a lightweight invoice processing application that converts invoice documents into structured financial data, independently verifies calculations, detects discrepancies and duplicates, and provides a dashboard for monitoring invoice activity.

💡 Core Idea
Extract → Validate → Verify → Approve or Review → Store → Analyze

✨ Features
📥 Invoice Processing
Upload one or multiple invoice documents

Extract structured invoice information

Process invoices individually or in batches

Handle invalid or unreadable documents safely

Prevent duplicate invoice records

🧮 Financial Verification
Paperwork Hub independently verifies important invoice calculations:

Quantity × Unit Price = Line Item Amount

Sum of Line Items = Subtotal

Subtotal + Tax = Total

₹0.01 tolerance for financial calculations

Duplicate invoice number detection

🛡️ Validation & Review
Invoices are automatically classified into two outcomes:

✅ Approved

All validation and financial checks pass.

⚠️ Human Review

One or more checks fail and the invoice requires manual attention.

The system also stores the reason behind validation issues for easier review.

📊 Dashboard
Monitor invoice activity through:

📄 Total invoices

✅ Approved invoices

⚠️ Review-required invoices

💰 Unpaid invoice value

💵 Total invoice value

📈 Expected vs Actual values

📊 Invoice volume

🧾 Validation mix

💳 Payment status

⚠️ Review queue

🕒 Recent invoices

Interactive charts allow users to explore invoice activity across different time periods.

🗂️ Invoice History
Search invoices by number or vendor

Filter by validation status

View complete invoice details

Review validation differences

View payment status

Delete selected invoices

Clear the database when required

📤 Data Export
Invoice data can be exported as CSV for further analysis or reporting.

🎨 User Experience
Clean and minimal interface

Light and dark mode

Interactive charts

Responsive dashboard layout

Clear validation states

Business-focused workflow

🧠 How It Works
                📄 Invoice Document
                        │
                        ▼
              🔍 Document Extraction
                        │
                        ▼
             📦 Structured Invoice Data
                        │
                        ▼
                🧩 Pydantic Validation
                        │
                        ▼
          🧮 Deterministic Financial Checks
                        │
                 ┌──────┴──────┐
                 │             │
                 ▼             ▼
            ✅ Approved    ⚠️ Human Review
                 │             │
                 └──────┬──────┘
                        ▼
                 🗄️ SQLite Database
                        │
                        ▼
              📊 Dashboard & History
🔑 Why this architecture?
The extraction layer handles the difficult problem of converting unstructured invoice information into structured data.

The financial verification layer then independently checks those extracted values using deterministic Python rules.

This separation means the application does not simply trust extracted financial values.

Instead:

Unstructured information is extracted automatically, while financial calculations are verified explicitly.

🧮 Financial Validation
Each invoice goes through multiple checks.

Validation	Rule
Line Item	Quantity × Unit Price = Amount
Subtotal	Σ Line Items = Subtotal
Total	Subtotal + Tax = Total
Precision	Differences within ₹0.01 are accepted
Duplicate	Invoice numbers must be unique
Example
If an invoice contains:

Quantity:   5
Unit Price: ₹200
Amount:     ₹1,000
The system verifies:

5 × ₹200 = ₹1,000
If the numbers do not match, the invoice is sent for Human Review instead of being automatically approved.

📊 Dashboard Overview
The dashboard provides both operational and financial visibility.

Key Metrics
📄 Total invoices

✅ Approved invoices

⚠️ Review-required invoices

💰 Unpaid invoice value

💵 Total invoice value

Analytics
The application includes interactive visualizations for:

Expected vs Actual invoice values

Invoice volume over time

Processing status

Payment status

Validation mix

Review queue

Recent invoice activity

Charts can be viewed across different periods:

Day → Week → Month → Year

🏗️ Project Architecture
Paperwork Hub
│
├── 📱 Streamlit Application
│       │
│       ├── Dashboard
│       ├── Process Invoice
│       └── Invoice History
│
├── 🔍 Invoice Processing
│       │
│       └── Structured Data Extraction
│
├── 🧩 Validation Layer
│       │
│       ├── Pydantic Validation
│       └── Financial Rules
│
├── 🧮 Verification Layer
│       │
│       ├── Line Item Checks
│       ├── Subtotal Checks
│       ├── Tax Checks
│       ├── Total Checks
│       └── Duplicate Detection
│
├── 🗄️ Database Layer
│       │
│       └── SQLite
│
└── 📊 Analytics Layer
        │
        ├── Plotly Charts
        ├── Invoice Metrics
        └── CSV Export
🛠️ Tech Stack
Technology	Purpose
🐍 Python	Core application logic
🎈 Streamlit	Web application and UI
🧩 Pydantic	Structured data validation
⚡ Groq	Invoice information extraction
🐼 Pandas	Data processing
📊 Plotly	Interactive visualizations
🗄️ SQLite	Local invoice database
🔐 python-dotenv	Environment configuration
📁 Project Structure
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
File Responsibilities
app.py — Main Streamlit application and page routing.

invoice_processor.py — Invoice extraction and processing.

validator.py — Pydantic models and deterministic financial validation.

database.py — SQLite storage and database operations.

ui/charts.py — Dashboard visualizations.

ui/components.py — Reusable interface components.

ui/theme.py — Centralized light and dark theme configuration.

generate_test_data.py — Generates invoice data for testing.

🚀 Getting Started
1. Clone the repository
git clone https://github.com/buildwithharshit/paperwork-hub.git
cd paperwork-hub
2. Create a virtual environment
python -m venv .venv
3. Activate the environment
Windows
.venv\Scripts\activate
macOS / Linux
source .venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
5. Configure the API key
Create a .env file in the project root:

GROQ_API_KEY=your_api_key_here
🔐 Never commit your .env file or expose your API key publicly.

6. Run the application
streamlit run app.py
The application will open in your browser.

🧪 Testing
The project includes a sample invoice and a test-data generator.

Run:

python generate_test_data.py
The system can be tested against different scenarios:

✅ Correct invoices

⚠️ Subtotal mismatches

⚠️ Total mismatches

⚠️ Line-item mismatches

⚠️ Tax discrepancies

🔁 Duplicate invoices

📦 Batch processing

🔐 Data & Security
The project intentionally keeps sensitive configuration outside the repository.

The following are excluded through .gitignore:

.env
.venv/
__pycache__/
invoices.db
API credentials should always be stored through environment variables rather than directly inside the source code.

🎯 Design Principles
1. Separate extraction from verification
Information extraction and financial verification are treated as different problems.

2. Use deterministic rules for financial calculations
Important calculations should be explicit and reproducible.

3. Make exceptions visible
When something does not pass validation, the system clearly identifies it instead of silently accepting it.

4. Keep the workflow simple
Upload
  ↓
Extract
  ↓
Validate
  ↓
Verify
  ↓
Approve / Review
  ↓
Store
  ↓
Analyze
🔮 Future Improvements
Potential future extensions include:

📄 PDF invoice support

🖼️ OCR and image-based invoice processing

☁️ Cloud database support

👥 Multi-user accounts

🔐 Role-based permissions

📧 Automated notifications

📈 Advanced financial analytics

🔗 Accounting software integrations

☁️ Cloud deployment

📱 Improved mobile experience

💼 Why I Built This
Paperwork Hub was built as a practical project around a real business workflow:

Invoices contain unstructured information, but financial decisions require structured and reliable data.

The project explores how software, automation, and deterministic business logic can work together to reduce repetitive paperwork while keeping important financial checks transparent.

👨‍💻 Author
Harshit Yadav
Built while exploring the intersection of:

Business × Finance × Technology × Automation

GitHub:
https://github.com/buildwithharshit

⭐ Paperwork Hub
From invoice documents → to structured data → to verified financial records.

If you find the project interesting, feel free to explore the code, test it with your own invoice examples, and build on top of it.
