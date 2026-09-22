from backend.database import SessionLocal
from backend.models import Invoice, Customer

def get_overdue_invoices(db_path=None):
    """
    Adapter: Fetch overdue records from PostgreSQL database via backend models.
    Matches the schema expected by the AI agent.
    """
    try:
        db = SessionLocal()
        
        # AI expects a list of dictionaries with specific keys
        # Join Invoice and Customer to get all needed fields
        results = (
            db.query(Invoice, Customer)
            .join(Customer, Invoice.customer_id == Customer.id)
            .filter(Invoice.status == "OVERDUE")
            .all()
        )
        
        data = []
        for invoice, customer in results:
            data.append({
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "customer_name": customer.name,
                "amount": invoice.amount,
                "email": customer.email,
                "status": invoice.status,
                "days_overdue": invoice.days_overdue
            })
            
        db.close()
        return data
    except Exception as e:
        return {"error": str(e)}
