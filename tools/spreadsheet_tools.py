from backend.database import SessionLocal
from backend.models import Payment

def check_bank_reconciliation(invoice_id, csv_path=None):
    """
    Adapter: Check bank reconciliation from PostgreSQL database via backend models.
    Matches the schema expected by the AI agent.
    """
    try:
        db = SessionLocal()
        
        payments = (
            db.query(Payment)
            .filter(Payment.invoice_id == invoice_id, Payment.status == "COMPLETED")
            .all()
        )
        
        transactions = []
        for p in payments:
            transactions.append({
                "id": p.id,
                "amount": p.amount,
                "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                "status": p.status
            })
            
        db.close()
        
        if transactions:
            return {
                "reconciled": True,
                "transactions": transactions
            }
        else:
            return {
                "reconciled": False,
                "transactions": []
            }
    except Exception as e:
        return {"error": str(e)}
