export interface Invoice {
  id: string;
  customer_id: string;
  invoice_date: string;
  due_date: string;
  amount: number;
  currency: string;
  status: 'PAID' | 'OVERDUE' | 'PENDING';
  days_overdue: number;
}

export interface Customer {
  id: string;
  company_name: string;
  industry: string;
  customer_value: 'HIGH' | 'MEDIUM' | 'LOW';
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
  contact_name: string;
  email: string;
  phone: string;
  has_recent_extension_request?: boolean;
}

export interface Communication {
  id: string;
  customer_id: string;
  date: string;
  channel: 'EMAIL' | 'PHONE' | 'PORTAL';
  subject: string;
  summary: string;
  sentiment: 'POSITIVE' | 'NEUTRAL' | 'NEGATIVE';
  resolution_status: 'RESOLVED' | 'UNRESOLVED' | 'PENDING' | 'FAILED';
}

export interface PolicyDocument {
  id: string;
  title: string;
  content: string;
}
