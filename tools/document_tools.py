from backend.database import SessionLocal
from backend.models import Customer

def search_crm_pdf_notes(customer_name, notes_dir=None):
    """
    Adapter: Fetch alternative contact emails from PostgreSQL database via backend models.
    Matches the schema expected by the AI agent.
    """
    try:
        db = SessionLocal()
        
        # Look for the customer by name
        # In a real system, we'd search CRM notes or alternative contacts.
        # Here we just fetch the customer's email from DB.
        customer = db.query(Customer).filter(Customer.name.ilike(f"%{customer_name}%")).first()
        db.close()
        
        if customer and customer.email:
            return {
                "found": True,
                "email": customer.email,
                "source": "Database CRM"
            }
        else:
            return {"found": False, "email": None}
    except Exception as e:
        return {"error": str(e)}
