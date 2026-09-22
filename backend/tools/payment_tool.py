from typing import Dict, Any
from ..tool_registry import ToolResult, ToolContext
from ..models import Payment

def get_payment_status_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    invoice_id = input_data.get("invoice_id")
    if not invoice_id:
        return ToolResult(status="FAILED", error="Missing invoice_id")
        
    db = context.db
    payments = db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
    
    total_paid = sum(p.amount for p in payments if p.status == "COMPLETED")
    
    return ToolResult(status="SUCCESS", data={
        "invoice_id": invoice_id,
        "total_paid": total_paid,
        "payments_count": len(payments)
    })

def get_payment_history_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    invoice_id = input_data.get("invoice_id")
    if not invoice_id:
        return ToolResult(status="FAILED", error="Missing invoice_id")
        
    db = context.db
    payments = db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
    
    results = []
    for p in payments:
        results.append({
            "id": p.id,
            "amount": p.amount,
            "status": p.status,
            "date": p.payment_date.isoformat() if p.payment_date else None,
            "reference": p.reference
        })
        
    return ToolResult(status="SUCCESS", data={"history": results})
