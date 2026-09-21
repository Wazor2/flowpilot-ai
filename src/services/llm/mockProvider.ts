import { LLMProvider } from './provider';

export class MockLLMProvider implements LLMProvider {
  async generatePlan(objective: string): Promise<any> {
    // Expected Object Interpretation from 36.7
    return Promise.resolve({
      understanding: "resolve_high_value_overdue_invoices",
      plan: [
        { id: "step-1", name: "Retrieve Invoices", description: "Fetch all invoices from database", status: "PENDING" },
        { id: "step-2", name: "Filter Invoices", description: "Filter overdue invoices > ₹50,000", status: "PENDING" },
        { id: "step-3", name: "Retrieve Customer Context", description: "Fetch customer details and history", status: "PENDING" },
        { id: "step-4", name: "Analyze History & Check Policy", description: "Analyze communication history against business policy", status: "PENDING" },
        { id: "step-5", name: "Prioritize", description: "Prioritize cases based on risk and value", status: "PENDING" },
        { id: "step-6", name: "Generate Recommendation", description: "Generate recommendations based on analysis", status: "PENDING" },
        { id: "step-7", name: "Generate Communication", description: "Draft communications and recommend actions", status: "PENDING" },
        { id: "step-8", name: "Request Approval", description: "Request approval for sensitive actions", status: "PENDING" },
        { id: "step-9", name: "Execute", description: "Execute approved actions", status: "PENDING" },
        { id: "step-10", name: "Verify", description: "Verify execution success", status: "PENDING" }
      ]
    });
  }

  async analyzeCases(context: any): Promise<any> {
    // Expected AI Analysis from 36.9
    return Promise.resolve([
      { invoice_id: "INV-1001", priority: "HIGH", recommendation: "High-priority escalation", approval_required: true, reason: "Amount: ₹185,000, 47 days overdue, High Risk, Payment Not Received, No resolution from previous comms." },
      { invoice_id: "INV-1002", priority: "LOW", recommendation: "Do NOT send escalation immediately. Schedule a follow-up after the extension period.", approval_required: false, reason: "Customer recently requested payment extension." },
      { invoice_id: "INV-1003", priority: "LOW", recommendation: "Monitor payment status. Do not send aggressive escalation.", approval_required: false, reason: "Customer confirmed payment is being processed." },
      { invoice_id: "INV-1004", priority: "HIGH", recommendation: "Find alternative verified contact and prepare escalation.", approval_required: true, reason: "Amount: ₹310,000, 61 days overdue, High Risk, Previous email failed." },
      { invoice_id: "INV-1005", priority: "MEDIUM", recommendation: "Send clarification response rather than escalation.", approval_required: false, reason: "Customer requested invoice clarification." },
      { invoice_id: "INV-1006", priority: "CRITICAL", recommendation: "Finance escalation.", approval_required: true, reason: "Amount: ₹520,000, 71 days overdue, High Risk, Multiple reminders ignored. Requires finance-manager approval." },
      { invoice_id: "INV-1009", priority: "MEDIUM", recommendation: "Standard reminder.", approval_required: false, reason: "Amount: ₹95,000, 5 days overdue, Medium Risk." }
    ]);
  }

  async generateDrafts(cases: any[]): Promise<any> {
    return Promise.resolve(cases.filter(c => c.approval_required).map(c => ({
      invoice_id: c.invoice_id,
      subject: `URGENT: Payment Follow-up — Invoice ${c.invoice_id}`,
      body: `Dear Customer,\n\nThis is an urgent follow-up regarding invoice ${c.invoice_id} which is significantly overdue.\n\nPlease arrange for immediate payment to avoid further escalation.`,
      priority: c.priority,
      reason: c.reason
    })));
  }
}
