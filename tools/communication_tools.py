import uuid
from backend.database import SessionLocal
from backend.tool_registry import ToolContext
from backend.tools.email_tool import prepare_email_execute, send_email_execute

def stage_recovery_email(recipient, subject, body):
    """
    Adapter: Prepare email draft via backend tool registry.
    """
    try:
        db = SessionLocal()
        context = ToolContext(db=db)
        input_data = {
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "type": "RECOVERY"
        }
        
        # We don't have an invoice_id here, just use a dummy one for the audit
        result = prepare_email_execute(input_data, context)
        db.close()
        
        email_id = str(uuid.uuid4())
        
        draft = {
            "email_id": email_id,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "status": "DRAFT_PENDING_APPROVAL"
        }
        return draft
    except Exception as e:
        return {"error": str(e)}

def send_approved_email(email_id):
    """
    Final dispatch action after HITL approval via backend tools.
    """
    try:
        db = SessionLocal()
        context = ToolContext(db=db)
        
        input_data = {
            "email_id": email_id
        }
        
        result = send_email_execute(input_data, context)
        db.close()
        
        return {
            "success": True if result.status == "SUCCESS" else False,
            "email_id": email_id,
            "message": f"Email {email_id} dispatch attempt completed. Status: {result.status}"
        }
    except Exception as e:
        return {"error": str(e)}
