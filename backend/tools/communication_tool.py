from typing import Dict, Any
from ..tool_registry import ToolResult, ToolContext
from ..models import Communication

def get_communication_history_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    customer_id = input_data.get("customer_id")
    if not customer_id:
        return ToolResult(status="FAILED", error="Missing customer_id")
        
    db = context.db
    comms = db.query(Communication).filter(Communication.customer_id == customer_id).order_by(Communication.timestamp.desc()).all()
    
    results = []
    for c in comms:
        results.append({
            "id": c.id,
            "channel": c.channel,
            "recipient": c.recipient,
            "subject": c.subject,
            "status": c.status,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None
        })
        
    return ToolResult(status="SUCCESS", data={"history": results})

def get_last_contact_execute(input_data: Dict[str, Any], context: ToolContext) -> ToolResult:
    customer_id = input_data.get("customer_id")
    if not customer_id:
        return ToolResult(status="FAILED", error="Missing customer_id")
        
    db = context.db
    last_comm = db.query(Communication).filter(Communication.customer_id == customer_id).order_by(Communication.timestamp.desc()).first()
    
    if not last_comm:
        return ToolResult(status="SUCCESS", data={"last_contact": None})
        
    return ToolResult(status="SUCCESS", data={
        "last_contact": {
            "id": last_comm.id,
            "channel": last_comm.channel,
            "timestamp": last_comm.timestamp.isoformat() if last_comm.timestamp else None
        }
    })
