import sqlite3
from datetime import date

from database import create_database


DATABASE_NAME = "invoices.db"


def main():
    create_database()

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    try:
        cursor = connection.cursor()

        today = str(
            date.today()
        )

        rows = [
            (
                "DEMO-1001",
                "Northstar Supplies",
                today,
                10000.0,
                1800.0,
                11800.0,
                today,
                "Paid",
                "Approved",
                0.0,
                "Demo record: all checks passed.",
            ),
            (
                "DEMO-1002",
                "Vertex Office Co.",
                today,
                12500.0,
                2250.0,
                14800.0,
                today,
                "Unpaid",
                "Human Review",
                50.0,
                (
                    "Demo record: total differs "
                    "from subtotal + tax."
                ),
            ),
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO invoices (
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
            rows,
        )

        connection.commit()

        print(
            "Test data created."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()