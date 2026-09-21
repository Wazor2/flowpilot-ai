import json
import uuid

def stage_recovery_email(recipient, subject, body):
    """
    Prepare email draft for human approval.
    """
    email_id = str(uuid.uuid4())
    draft = {
        "email_id": email_id,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "status": "DRAFT_PENDING_APPROVAL"
    }
    
    # In a real system, this would save to a DB. For our prototype, we'll return it to the agent.
    return draft

def send_approved_email(email_id):
    """
    Final dispatch action after HITL approval.
    """
    # In a real system, this would mark the draft as sent in a DB and dispatch via SMTP/API.
    # For prototype, we just return success.
    return {
        "success": True,
        "email_id": email_id,
        "message": f"Email {email_id} has been dispatched successfully."
    }
