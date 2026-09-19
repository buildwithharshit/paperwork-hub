import sqlite3


DATABASE_NAME = "invoices.db"


def create_database():
    connection = sqlite3.connect(
        DATABASE_NAME
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                vendor TEXT,
                invoice_date TEXT,
                subtotal REAL,
                tax REAL,
                total REAL,
                due_date TEXT,
                payment_status TEXT,
                validation_status TEXT,
                difference REAL,
                audit_reason TEXT
            )
            """
        )

        cursor.execute(
            "PRAGMA table_info(invoices)"
        )

        columns = {
            row[1]
            for row in cursor.fetchall()
        }

        if "audit_reason" not in columns:
            cursor.execute(
                """
                ALTER TABLE invoices
                ADD COLUMN audit_reason TEXT
                """
            )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_invoices_invoice_number
            ON invoices(invoice_number)
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def invoice_number_exists(invoice_number):
    connection = sqlite3.connect(
        DATABASE_NAME
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM invoices
            WHERE invoice_number = ?
            LIMIT 1
            """,
            (invoice_number,),
        )

        return cursor.fetchone() is not None

    finally:
        connection.close()


def save_invoice(
    invoice,
    validation_status,
    difference,
    audit_reason,
):
    connection = sqlite3.connect(
        DATABASE_NAME
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO invoices (
                invoice_number,
                vendor,
                invoice_date,
                subtotal,
                tax,
                total,
                due_date,
                payment_status,
                validation_status,
                difference,
                audit_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invoice.invoice_number,
                invoice.vendor,
                invoice.invoice_date,
                invoice.subtotal,
                invoice.tax,
                invoice.total,
                invoice.due_date,
                invoice.payment_status,
                validation_status,
                difference,
                audit_reason,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_invoices():
    connection = sqlite3.connect(
        DATABASE_NAME
    )

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                invoice_number,
                vendor,
                invoice_date,
                subtotal,
                tax,
                total,
                due_date,
                payment_status,
                validation_status,
                difference,
                audit_reason
            FROM invoices
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    print(
        "Database created successfully."
    )