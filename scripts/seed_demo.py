"""One-off seed for the explicitly requested live Gmail approval workflow."""

from datetime import date, datetime, time, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database import SessionLocal, engine
from backend.models import Customer, Invoice


def main() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Refusing to seed: DATABASE_URL is not PostgreSQL")

    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == "cust-om").first()
        if customer is None:
            customer = Customer(id="cust-om", name="Om", email="ommanjules@gmail.com", phone="")
            db.add(customer)
        else:
            customer.name = "Om"
            customer.email = "ommanjules@gmail.com"
            customer.phone = ""

        invoice = db.query(Invoice).filter(Invoice.id == "inv-om-001").first()
        due_date = datetime.combine(date.today() - timedelta(days=30), time.min)
        if invoice is None:
            invoice = Invoice(
                id="inv-om-001",
                invoice_number="INV-9001",
                customer_id="cust-om",
                amount=15000,
                due_date=due_date,
                status="OVERDUE",
                days_overdue=30,
            )
            db.add(invoice)
        else:
            invoice.invoice_number = "INV-9001"
            invoice.customer_id = "cust-om"
            invoice.amount = 15000
            invoice.due_date = due_date
            invoice.status = "OVERDUE"
            invoice.days_overdue = 30

        db.commit()
        print("Seeded customer cust-om and invoice inv-om-001")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
