import { Invoice, Customer, Communication, PolicyDocument } from './models';

// Deterministic Demo Data from Requirements Section 36
export const mockCustomers: Customer[] = [
  {
    id: "C001",
    company_name: "Apex Manufacturing Pvt Ltd",
    industry: "Manufacturing",
    contact_name: "Priya Sharma",
    email: "priya@apexmfg.example",
    risk_level: "HIGH",
    customer_value: "HIGH",
    phone: "+1-555-0001",
  },
  {
    id: "C002",
    company_name: "BluePeak Technologies",
    industry: "Technology",
    contact_name: "Rahul Mehta",
    email: "finance@bluepeak.example",
    risk_level: "MEDIUM",
    customer_value: "HIGH",
    phone: "+1-555-0002",
    has_recent_extension_request: true
  },
  {
    id: "C003",
    company_name: "Crestline Retail Ltd",
    industry: "Retail",
    contact_name: "Ananya Rao",
    email: "accounts@crestline.example",
    risk_level: "LOW",
    customer_value: "MEDIUM",
    phone: "+1-555-0003",
  },
  {
    id: "C004",
    company_name: "Delta Logistics Pvt Ltd",
    industry: "Logistics",
    contact_name: "Arjun Patel",
    email: "invalid@delta-logistics.example",
    risk_level: "HIGH",
    customer_value: "HIGH",
    phone: "+1-555-0004",
  },
  {
    id: "C005",
    company_name: "Everstone Foods Ltd",
    industry: "Food & Beverage",
    contact_name: "Neha Verma",
    email: "finance@everstone.example",
    risk_level: "MEDIUM",
    customer_value: "MEDIUM",
    phone: "+1-555-0005",
  },
  {
    id: "C006",
    company_name: "Falcon Infrastructure",
    industry: "Infrastructure",
    contact_name: "Vikram Singh",
    email: "finance@falconinfra.example",
    risk_level: "HIGH",
    customer_value: "HIGH",
    phone: "+1-555-0006",
  }
];

export const mockInvoices: Invoice[] = [
  { id: "INV-1001", customer_id: "C001", amount: 185000, invoice_date: "2026-07-01", due_date: "2026-08-04", days_overdue: 47, status: "OVERDUE", currency: "INR" },
  { id: "INV-1002", customer_id: "C002", amount: 125000, invoice_date: "2026-07-20", due_date: "2026-08-19", days_overdue: 32, status: "OVERDUE", currency: "INR" },
  { id: "INV-1003", customer_id: "C003", amount: 72000, invoice_date: "2026-08-04", due_date: "2026-09-04", days_overdue: 16, status: "OVERDUE", currency: "INR" },
  { id: "INV-1004", customer_id: "C004", amount: 310000, invoice_date: "2026-06-20", due_date: "2026-07-20", days_overdue: 61, status: "OVERDUE", currency: "INR" },
  { id: "INV-1005", customer_id: "C005", amount: 58000, invoice_date: "2026-08-01", due_date: "2026-09-01", days_overdue: 19, status: "OVERDUE", currency: "INR" },
  { id: "INV-1006", customer_id: "C006", amount: 520000, invoice_date: "2026-06-10", due_date: "2026-07-10", days_overdue: 71, status: "OVERDUE", currency: "INR" },
  { id: "INV-1007", customer_id: "C001", amount: 18000, invoice_date: "2026-07-10", due_date: "2026-08-10", days_overdue: 41, status: "OVERDUE", currency: "INR" },
  { id: "INV-1008", customer_id: "C003", amount: 24000, invoice_date: "2026-07-30", due_date: "2026-08-30", days_overdue: 21, status: "OVERDUE", currency: "INR" },
  { id: "INV-1009", customer_id: "C002", amount: 95000, invoice_date: "2026-08-15", due_date: "2026-09-15", days_overdue: 5, status: "OVERDUE", currency: "INR" },
  { id: "INV-1010", customer_id: "C005", amount: 42000, invoice_date: "2026-07-15", due_date: "2026-08-15", days_overdue: 36, status: "OVERDUE", currency: "INR" },
  { id: "INV-1011", customer_id: "C006", amount: 15000, invoice_date: "2026-08-12", due_date: "2026-09-12", days_overdue: 8, status: "OVERDUE", currency: "INR" },
  { id: "INV-1012", customer_id: "C004", amount: 38000, invoice_date: "2026-07-01", due_date: "2026-08-01", days_overdue: 50, status: "OVERDUE", currency: "INR" },
];

export const mockCommunications: Communication[] = [
  { id: "COM-1", customer_id: "C001", date: "2026-08-20", channel: "EMAIL", subject: "Payment Reminder", summary: "First payment reminder sent.", sentiment: "NEUTRAL", resolution_status: "UNRESOLVED" },
  { id: "COM-2", customer_id: "C001", date: "2026-09-05", channel: "EMAIL", subject: "Payment Follow-up", summary: "Customer acknowledged the invoice but did not provide a payment date.", sentiment: "NEUTRAL", resolution_status: "UNRESOLVED" },
  { id: "COM-3", customer_id: "C002", date: "2026-09-10", channel: "EMAIL", subject: "Payment Extension Request", summary: "Customer requested an additional 14 days to complete payment.", sentiment: "NEUTRAL", resolution_status: "PENDING" },
  { id: "COM-4", customer_id: "C003", date: "2026-09-12", channel: "EMAIL", subject: "Payment Reminder", summary: "Customer confirmed payment is being processed.", sentiment: "POSITIVE", resolution_status: "PENDING" },
  { id: "COM-5", customer_id: "C004", date: "2026-08-15", channel: "EMAIL", subject: "Payment Reminder", summary: "No response from customer.", sentiment: "NEUTRAL", resolution_status: "UNRESOLVED" },
  { id: "COM-6", customer_id: "C004", date: "2026-09-01", channel: "EMAIL", subject: "Second Payment Reminder", summary: "Email bounced because the contact address was invalid.", sentiment: "NEGATIVE", resolution_status: "FAILED" },
  { id: "COM-7", customer_id: "C005", date: "2026-09-05", channel: "EMAIL", subject: "Payment Reminder", summary: "Customer requested invoice clarification.", sentiment: "NEUTRAL", resolution_status: "PENDING" },
  { id: "COM-8", customer_id: "C006", date: "2026-08-05", channel: "EMAIL", subject: "Payment Reminder", summary: "No response.", sentiment: "NEUTRAL", resolution_status: "UNRESOLVED" },
  { id: "COM-9", customer_id: "C006", date: "2026-08-25", channel: "EMAIL", subject: "Payment Escalation", summary: "Customer did not respond to previous communication.", sentiment: "NEGATIVE", resolution_status: "UNRESOLVED" },
];

export const mockPolicies: PolicyDocument[] = [
  {
    id: "POL-001",
    title: "BUSINESS COLLECTION POLICY",
    content: `Rule 1: Invoices below ₹50,000 can receive standard reminders.
Rule 2: Invoices of ₹50,000 or more require priority evaluation.
Rule 3: Invoices above ₹100,000 that are more than 30 days overdue require manager approval before escalation communication.
Rule 4: Invoices above ₹500,000 require finance-manager approval.
Rule 5: If a customer requested a payment extension within the previous 14 days, do not send an escalation reminder.
Rule 6: If an email fails, search available customer records for an alternative verified contact.
Rule 7: No external communication may be sent without approval when the applicable policy requires approval.
Rule 8: Every workflow action must be recorded in the audit log.`
  }
];

export const mockPaymentStatus: Record<string, string> = {
  "INV-1001": "Not Received",
  "INV-1002": "Not Received",
  "INV-1003": "Processing",
  "INV-1004": "Not Received",
  "INV-1005": "Not Received",
  "INV-1006": "Not Received",
  "INV-1009": "Not Received"
};
