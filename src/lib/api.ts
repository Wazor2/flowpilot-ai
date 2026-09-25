export type Workflow = {
  id: string;
  objective: string;
  mode: string;
  status: string;
  current_step?: string | null;
  current_plan?: unknown;
  created_at?: string;
  updated_at?: string;
};

export type AuditEvent = {
  id: string;
  workflow_id: string;
  timestamp?: string;
  event_type: string;
  actor: string;
  tool?: string | null;
  status?: string | null;
  input_summary?: string | null;
  result_summary?: string | null;
  approval_state?: string | null;
  reason?: string | null;
  summary?: string | null;
};

export type Approval = {
  id: string;
  workflow_id: string;
  action: string;
  reason?: string | null;
  status: string;
  requested_at?: string;
  requested_by?: string | null;
  draft?: { invoice_id?: string; recipient?: string; subject?: string; body?: string } | null;
};

export type Customer = {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  status?: string;
  risk_level?: string;
};

export type Invoice = {
  id: string;
  invoice_number?: string;
  customer_id: string;
  amount: number;
  due_date: string;
  status: string;
  days_overdue?: number;
};

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    cache: 'no-store',
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Backend request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export { API_BASE };
