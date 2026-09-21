from utils.audit_logger import AuditLogger
from tools.database_tools import get_overdue_invoices
from tools.spreadsheet_tools import check_bank_reconciliation
from tools.document_tools import search_crm_pdf_notes
from tools.communication_tools import stage_recovery_email

logger = AuditLogger()

class PlannerAgent:
    def __init__(self):
        self.name = "PlannerAgent"
        
    def plan_recovery(self, goal):
        logger.log_event(self.name, "Received Goal", {"goal": goal})
        
        # Step 1: Fetch invoices
        invoices = get_overdue_invoices()
        logger.log_event(self.name, "Plan Step Executed", {"step": "Fetch Invoices", "count": len(invoices) if isinstance(invoices, list) else 0})
        
        plan = []
        if isinstance(invoices, list):
            for inv in invoices:
                plan.append({"action": "process_invoice", "invoice": inv})
                
        return plan

class ExecutorAgent:
    def __init__(self):
        self.name = "ExecutorAgent"
        
    def execute_plan(self, plan_items):
        results = []
        for item in plan_items:
            if item.get("action") == "process_invoice":
                invoice = item.get("invoice")
                logger.log_event(self.name, "Executing Task", {"task": "process_invoice", "invoice_id": invoice.get('invoice_id')})
                
                # Check reconciliation first
                recon = check_bank_reconciliation(invoice.get('invoice_id'))
                if recon.get('reconciled'):
                    logger.log_event(self.name, "Reconciliation Success", {"invoice_id": invoice.get('invoice_id'), "note": "Payment found in bank statements."})
                    results.append({"invoice_id": invoice.get('invoice_id'), "status": "RESOLVED_INTERNALLY", "reason": "Payment found in bank statement"})
                    continue
                
                # Check if email is missing
                email = invoice.get('email')
                if not email:
                    logger.log_event(self.name, "Missing Email Fallback Triggered", {"invoice_id": invoice.get('invoice_id'), "customer": invoice.get('customer_name')})
                    pdf_result = search_crm_pdf_notes(invoice.get('customer_name'))
                    if pdf_result.get('found'):
                        email = pdf_result.get('email')
                        logger.log_event(self.name, "Fallback Success", {"invoice_id": invoice.get('invoice_id'), "found_email": email})
                    else:
                        logger.log_event(self.name, "Fallback Failed", {"invoice_id": invoice.get('invoice_id')})
                        results.append({"invoice_id": invoice.get('invoice_id'), "status": "FAILED", "reason": "No contact email found"})
                        continue
                
                # Stage Email
                draft = stage_recovery_email(
                    recipient=email,
                    subject=f"Overdue Notice: Invoice {invoice.get('invoice_id')}",
                    body=f"Dear {invoice.get('customer_name')},\n\nYour invoice {invoice.get('invoice_id')} for ${invoice.get('amount')} is overdue. Please arrange payment."
                )
                logger.log_event(self.name, "Drafted Email", {"invoice_id": invoice.get('invoice_id'), "draft_id": draft.get('email_id')})
                
                results.append({
                    "invoice_id": invoice.get('invoice_id'), 
                    "status": "DRAFT_READY",
                    "draft": draft,
                    "amount": invoice.get('amount')
                })
        return results

class SafeguardVerifierAgent:
    def __init__(self):
        self.name = "SafeguardVerifierAgent"
        
    def verify_results(self, execution_results):
        verified_items = []
        for result in execution_results:
            if result.get("status") == "DRAFT_READY":
                amount = result.get("amount", 0)
                draft = result.get("draft")
                
                # Check High-Impact rule: > $1000 or any email dispatch requires HITL
                needs_approval = True
                reason = "All email dispatches require approval."
                if amount > 1000:
                    reason = "High amount (> $1000) and email dispatch require approval."
                    
                logger.log_event(self.name, "Verification Check", {
                    "invoice_id": result.get('invoice_id'),
                    "needs_approval": needs_approval,
                    "reason": reason
                })
                
                result["requires_hitl"] = needs_approval
                result["hitl_reason"] = reason
            
            verified_items.append(result)
            
        return verified_items
